"""Encodeur semantique REDUIT (CPU/numpy) — version honnete.
Architecture : projection lineaire 6->64 (poids FIXES, seed) + 1 couche MHA
numpy (4 tetes, d=64) pour le SCORING des tokens + autoencodeur MLP (sklearn,
ENTRAINE) 6->64->16->64->6 dont la couche centrale (16) est le latent transmis
en float16. N'est PAS le Transformer 4x256 entraine du manuscrit (H-ENCODER).
"""
import json
import time
import numpy as np

D_MODEL = 64
N_HEADS = 4
LATENT_DIM = 16


def _softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)


class AttentionScorer:
    """MHA single-couche a poids fixes : score = masse d'attention recue."""

    def __init__(self, d_in=6, d_model=D_MODEL, n_heads=N_HEADS, seed=42):
        rng = np.random.default_rng(seed)
        self.W_in = rng.normal(0, np.sqrt(2 / d_in), (d_in, d_model))
        self.b_in = np.zeros(d_model)
        self.W_qkv = rng.normal(0, np.sqrt(2 / d_model), (3, n_heads, d_model, d_model // n_heads))
        self.W_o = rng.normal(0, np.sqrt(2 / d_model), (d_model, d_model))

    def scores(self, x):
        h = x @ self.W_in + self.b_in  # (N, d)
        N = h.shape[0]
        dh = D_MODEL // N_HEADS
        q = np.einsum("nd,hde->nhe", h, self.W_qkv[0]).reshape(N, N_HEADS, dh)
        k = np.einsum("nd,hde->nhe", h, self.W_qkv[1]).reshape(N, N_HEADS, dh)
        att = _softmax(np.einsum("nhe,mhe->nhm", q, k) / np.sqrt(dh), axis=-1)
        return att.mean(axis=1).mean(axis=0)  # masse moyenne recue par token (N,)


class BottleneckAE:
    """Autoencodeur 6->64->16->64->6 (sklearn, relu — GELU indisponible, ecart documente)."""

    def __init__(self, seed=42):
        from sklearn.neural_network import MLPRegressor
        from sklearn.preprocessing import StandardScaler
        self.scaler = StandardScaler()
        self.mlp = MLPRegressor(hidden_layer_sizes=(64, 16, 64), activation="relu",
                               max_iter=800, tol=1e-4, random_state=seed)

    def fit(self, X):
        Xs = self.scaler.fit_transform(X)
        self.mlp.fit(Xs, Xs)
        return self

    def encode(self, X):
        Xs = self.scaler.transform(X)
        a1 = np.maximum(Xs @ self.mlp.coefs_[0] + self.mlp.intercepts_[0], 0)
        z = np.maximum(a1 @ self.mlp.coefs_[1] + self.mlp.intercepts_[1], 0)
        assert z.shape[1] == LATENT_DIM, z.shape
        return z

    def decode(self, z):
        a3 = np.maximum(z @ self.mlp.coefs_[2] + self.mlp.intercepts_[2], 0)
        out = a3 @ self.mlp.coefs_[3] + self.mlp.intercepts_[3]
        return self.scaler.inverse_transform(out)


def pack_stream(z16, meta):
    header = json.dumps(meta).encode("utf-8")
    return len(header).to_bytes(4, "little") + header + z16.tobytes()


def chamfer_mse(a, b):
    """MSE symetrique de Chamfer sur coords voxel (N,3),(M,3)."""
    from scipy.spatial.distance import cdist
    d2 = cdist(a, b, "sqeuclidean")
    return float(0.5 * (d2.min(axis=1).mean() + d2.min(axis=0).mean()))


def d1_psnr(mse, pmax=1023.0):
    if mse <= 0:
        return 120.0  # plafond documente (reconstruction parfaite)
    return float(10 * np.log10(3 * pmax ** 2 / mse))


def compress_frame(pts_norm, vox, alpha, order, ae):
    """pts_norm : (Ns,6) normalise ; vox : (Ns,6) brut ; order : indices tries
    par score d'attention (pre-calcules). Retourne dict de metriques MESUREES."""
    from scipy.spatial.distance import cdist  # noqa: F401 (import anticipe)
    ns = len(pts_norm)
    k = max(8, int(round(alpha * ns)))
    t0 = time.perf_counter()
    keep = np.asarray(order)[:k]
    z = ae.encode(pts_norm[keep]).astype(np.float16)
    meta = {"ns": ns, "k": int(k), "dim": LATENT_DIM, "dtype": "float16"}
    stream = pack_stream(z, meta)
    enc_t = time.perf_counter() - t0
    t1 = time.perf_counter()
    rec = ae.decode(z.astype(np.float32))
    dec_t = time.perf_counter() - t1
    # distorsion : plus proche dans la frame d'origine (coords voxel)
    d2 = np.asarray(__import__("scipy").spatial.distance.cdist(rec[:, :3] * 1023.0, vox[:, :3], "sqeuclidean"))
    mse_d1 = float(d2.min(axis=1).mean())
    cham = float(0.5 * (d2.min(axis=1).mean() + d2.min(axis=0).mean()))
    raw_bytes = ns * 6 * 4  # float32
    return {"k": k, "stream_bytes": len(stream), "raw_bytes": raw_bytes,
            "alpha_measured": len(stream) / raw_bytes,
            "chamfer": cham, "d1_psnr_db": d1_psnr(mse_d1),
            "enc_ms": enc_t * 1000, "dec_ms": dec_t * 1000}


def attn_select(pts_norm, vox, alpha, order):
    """Selection attention + transmission EXACTE (float16) : isole l'apport du
    scoring Transformer par rapport au sous-echantillonnage uniforme."""
    from scipy.spatial.distance import cdist
    ns = len(pts_norm)
    k = max(8, int(round(alpha * ns)))
    t0 = time.perf_counter()
    keep = np.sort(np.asarray(order)[:k])
    z16 = pts_norm[keep].astype(np.float16)
    stream = pack_stream(z16, {"ns": ns, "k": int(k), "dim": 6, "dtype": "float16"})
    enc_t = time.perf_counter() - t0
    d2 = cdist(z16.astype(np.float32)[:, :3] * 1023.0, vox[:, :3], "sqeuclidean")
    mse_d1 = float(d2.min(axis=1).mean())
    cham = float(0.5 * (d2.min(axis=1).mean() + d2.min(axis=0).mean()))
    return {"k": k, "stream_bytes": len(stream), "raw_bytes": ns * 6 * 4,
            "alpha_measured": len(stream) / (ns * 6 * 4),
            "chamfer": cham, "d1_psnr_db": d1_psnr(mse_d1),
            "enc_ms": enc_t * 1000, "dec_ms": 0.0}


def baseline_uniform(pts_norm, vox, alpha, seed=0):
    ns = len(pts_norm)
    k = max(8, int(round(alpha * ns)))
    rng = np.random.default_rng(seed)
    keep = np.sort(rng.choice(ns, k, replace=False))
    t0 = time.perf_counter()
    z16 = pts_norm[keep].astype(np.float16)
    stream = pack_stream(z16, {"ns": ns, "k": int(k), "dim": 6, "dtype": "float16"})
    enc_t = time.perf_counter() - t0
    from scipy.spatial.distance import cdist
    d2 = cdist(z16.astype(np.float32)[:, :3] * 1023.0, vox[:, :3], "sqeuclidean")
    mse_d1 = float(d2.min(axis=1).mean())
    cham = float(0.5 * (d2.min(axis=1).mean() + d2.min(axis=0).mean()))
    return {"k": k, "stream_bytes": len(stream), "raw_bytes": ns * 6 * 4,
            "alpha_measured": len(stream) / (ns * 6 * 4),
            "chamfer": cham, "d1_psnr_db": d1_psnr(mse_d1),
            "enc_ms": enc_t * 1000, "dec_ms": 0.0}
