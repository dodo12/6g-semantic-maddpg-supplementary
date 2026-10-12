import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Phase C : entraine l'AE sur TRAIN, balaye alpha x 12 frames + 2 baselines."""
import os, sys, csv
import numpy as np
# (portable : SUPP_ROOT/code, voir en-tete)
from src.dataset.loader import FRAMES
from src.semantic_transformer.encoder import AttentionScorer, BottleneckAE, compress_frame, baseline_uniform, attn_select

TRAIN = ["loot_1000", "loot_1150", "longdress_1051", "longdress_1201", "redandblack_1450", "redandblack_1600"]
VAL = ["loot_1299", "longdress_1350", "redandblack_1749"]
TEST = ["soldier_536", "soldier_686", "soldier_835"]
ALPHAS = [0.02, 0.05, 0.1, 0.2, 0.5]

data = np.load(os.path.join(SUPP_ROOT, "data", "processed", "subsampled.npz"))
Xtr = np.concatenate([data[f] for f in TRAIN]).astype(np.float64)
print("train samples:", Xtr.shape, flush=True)
ae = BottleneckAE(seed=42).fit(Xtr)
print("AE trained, loss=%.6f, iters=%d" % (ae.mlp.loss_, ae.mlp.n_iter_), flush=True)
scorer = AttentionScorer(seed=42)

rows = []
for fid in list(FRAMES):
    pts = data[fid].astype(np.float64)
    vox = data[fid + "_vox"].astype(np.float64)
    split = "train" if fid in TRAIN else ("val" if fid in VAL else "test")
    order = np.argsort(-scorer.scores(pts))
    for a in ALPHAS:
        m = compress_frame(pts, vox, a, order, ae)
        rows.append({"frame": fid, "sequence": FRAMES[fid][0], "split": split, "method": "proposed",
                     "alpha_target": a, **{k: round(v, 4) if isinstance(v, float) else v for k, v in m.items()}})
        t = attn_select(pts, vox, a, order)
        rows.append({"frame": fid, "sequence": FRAMES[fid][0], "split": split, "method": "attn-select",
                     "alpha_target": a, **{k: round(v, 4) if isinstance(v, float) else v for k, v in t.items()}})
        u = baseline_uniform(pts, vox, a)
        rows.append({"frame": fid, "sequence": FRAMES[fid][0], "split": split, "method": "uniform",
                     "alpha_target": a, **{k: round(v, 4) if isinstance(v, float) else v for k, v in u.items()}})
    rows.append({"frame": fid, "sequence": FRAMES[fid][0], "split": split, "method": "raw",
                 "alpha_target": 1.0, "k": len(pts), "stream_bytes": len(pts) * 6 * 4,
                 "raw_bytes": len(pts) * 6 * 4, "alpha_measured": 1.0,
                 "chamfer": 0.0, "d1_psnr_db": 120.0, "enc_ms": 0.0, "dec_ms": 0.0})
    print("frame done:", fid, flush=True)

with open(os.path.join(SUPP_ROOT, "results", "compression_metrics.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

import pandas as pd
df = pd.DataFrame(rows)
g = df.groupby(["sequence", "method", "alpha_target"]).agg(
    stream_bytes=("stream_bytes", "mean"), alpha_measured=("alpha_measured", "mean"),
    chamfer=("chamfer", "mean"), d1_psnr_db=("d1_psnr_db", "mean"),
    enc_ms=("enc_ms", "mean"), dec_ms=("dec_ms", "mean"), n=("frame", "count")).reset_index()
g.to_csv(os.path.join(SUPP_ROOT, "results", "compression_by_sequence.csv"), index=False)
print("OK", len(rows), "rows")
print(g[g.alpha_target == 0.05][["sequence", "method", "alpha_measured", "d1_psnr_db", "enc_ms"]].to_string())
