import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Phase D : MADDPG (numpy/CPU) + 5 baselines, 3 graines.
Payloads = pleines frames estimees par regle de trois (meme alpha) depuis les
flux attn-select mesures (Ns=2048) ; Q et Denc restes a l'echelle pilote.
Tout est documente dans reports/04_MADDPG_RESULTS.md."""
import os, sys, csv
import numpy as np
import pandas as pd
# (portable : SUPP_ROOT/code, voir en-tete)
from src.radio_environment.channel import step_rate_bps, queue_md1_ms
from src.maddpg.maddpg import MADDPG
from src.metrics.qoe import qoe
import argparse


def parse_args(argv=None):
    _AP = argparse.ArgumentParser()
    _AP.add_argument("--seeds", nargs="+", type=int, default=[42, 123, 2026])
    _AP.add_argument("--ep", type=int, default=80)
    _AP.add_argument("--steps", type=int, default=50)
    _AP.add_argument("--out_log", default=os.path.join(SUPP_ROOT, "results", "maddpg_training_log.csv"))
    return _AP.parse_args(argv)


_ARGS = parse_args() if __name__ == "__main__" else parse_args([])
SEEDS = _ARGS.seeds
EP, STEPS = _ARGS.ep, _ARGS.steps

SEQ = ["loot", "soldier", "longdress", "redandblack"]
DIST = {"loot": 90.0, "soldier": 120.0, "longdress": 60.0, "redandblack": 110.0}
N_FULL = {"longdress": 834315.0, "loot": 793821.0, "redandblack": 727071.0, "soldier": 1075299.0}
B_TOT = 1e9
PMAX = 2.0
DMAX = 50.0
KAPPA = 10.0  # echelle : penalite = KAPPA x depassement RELATIF (D-Dmax)/Dmax ;
# la forme brute du manuscrit (KAPPA x ms) ecrase le gradient (10^3 vs QoE~1) ; ecart documente


def load_curves():
    df = pd.read_csv(os.path.join(SUPP_ROOT, "results", "compression_by_sequence.csv"))
    d = df[df.method == "attn-select"].sort_values("alpha_target")
    curves = {}
    for s in SEQ:
        sub = d[d.sequence == s]
        curves[s] = {c: (sub.alpha_target.to_numpy(), sub[c].to_numpy())
                     for c in ("stream_bytes", "d1_psnr_db", "enc_ms")}
    return curves


def payload_full_bits(seq, alpha):
    k_full = alpha * N_FULL[seq]
    return (k_full * 6 * 2 + 200.0) * 8.0  # float16 + en-tete ; cf. rapport


def interp(curves, seq, alpha, key):
    x, y = curves[seq][key]
    return float(np.interp(alpha, x, y))


def run_episode(policy, curves, rng, train=True, noise=0.0, B_tot=B_TOT, lam=30.0, dist_scale=1.0):
    obs = np.zeros((4, 5))
    prev = np.zeros((4, 3))
    backlog = np.zeros(4)
    r_ewma = np.full(4, 250e6)  # debit moyen court-terme par utilisateur (init 250 Mbps)
    ep = {"reward": 0.0, "qoe": [], "lat": [], "se": [], "en": [], "viol": 0, "alpha": [],
          "denc": [], "dtx": [], "dq": [], "etx": [], "ecomp": [], "pmean": []}
    for t in range(STEPS):
        if policy["kind"] in ("maddpg", "single"):
            u = policy["agent"].act(obs, noise=noise)
            p, shares, alpha = policy["agent"].map_actions(u)
        elif policy["kind"] == "fixed1":
            p, shares, alpha = np.full(4, PMAX), np.full(4, 0.25), np.full(4, 1.0)
        elif policy["kind"] == "fixed05":
            p, shares, alpha = np.full(4, PMAX), np.full(4, 0.25), np.full(4, 0.5)
        elif policy["kind"] == "random":
            p = rng.uniform(0.1, PMAX, 4)
            shares = rng.dirichlet(np.ones(4))
            alpha = rng.uniform(0.02, 0.5, 4)
        elif policy["kind"] == "heuristic":
            inv = np.array([1.0 / (DIST[s] * dist_scale) for s in SEQ])
            shares = inv / inv.sum()
            p, alpha = np.full(4, 1.0), np.full(4, 0.05)
        q, dms, emj, se, r = [], [], [], [], []
        obs2 = np.zeros_like(obs)
        for i, s in enumerate(SEQ):
            d_m = DIST[s] * dist_scale
            bw = max(1e6, shares[i] * B_tot)
            rate, snr, pl = step_rate_bps(p[i], bw, d_m, rng=rng)
            pay = payload_full_bits(s, alpha[i])
            qdb = interp(curves, s, min(alpha[i], 0.5), "d1_psnr_db")
            denc = interp(curves, s, min(alpha[i], 0.5), "enc_ms")
            dtx = pay / rate * 1000.0
            # File DYNAMIQUE (arriéré) : le M/D/1 stationnaire par pas est invalide
            # sous fading non stationnaire ; Dq = temps de vidage de l'arriéré.
            dq = backlog[i] / r_ewma[i] * 1000.0
            rho = (pay * lam) / rate  # charge instantanee (indicative)
            r_ewma[i] = 0.2 * rate + 0.8 * r_ewma[i]
            D = denc + dtx + dq + 0.35
            E = p[i] * dtx + 65.0 * denc  # mJ : W*ms = mJ (H-CPU)
            qq = qoe(qdb, D, E)
            q.append(qq); dms.append(D); emj.append(E); se.append(rate / bw)
            ep["denc"].append(denc); ep["dtx"].append(dtx); ep["dq"].append(dq)
            ep["etx"].append(p[i] * dtx); ep["ecomp"].append(65.0 * denc)
            ep["pmean"].append(p[i])
            backlog[i] = max(0.0, backlog[i] + pay - rate / lam)
            obs2[i] = [np.log10(1 + snr) / 3.0, min(1.0, backlog[i] / (pay + 1)),
                       p[i] / PMAX, shares[i], d_m / 120.0]
        QoE = float(np.mean(q))
        pen = KAPPA * float(sum(max(0.0, (x - DMAX) / DMAX) for x in dms))
        step_r = QoE * 4 - pen
        ep["reward"] += step_r
        ep["qoe"].append(QoE); ep["lat"].append(float(np.mean(dms)))
        ep["se"].append(float(np.mean(se))); ep["en"].append(float(np.mean(emj)))
        ep["viol"] += sum(1 for x in dms if x > DMAX) / 4
        ep["alpha"].append(float(np.mean(alpha)))
        if train and policy["kind"] in ("maddpg", "single"):
            u_raw = policy["agent"].act(obs, noise=0.0)
            policy["agent"].store(obs, u_raw, step_r, obs2)
            for _ in range(2):
                policy["agent"].update()
        obs = obs2
        prev = np.stack([p / PMAX, shares, alpha], axis=1)
    n = STEPS
    return {"reward": ep["reward"] / n, "qoe": float(np.mean(ep["qoe"])),
            "lat": float(np.mean(ep["lat"])), "se": float(np.mean(ep["se"])),
            "en": float(np.mean(ep["en"])), "viol": ep["viol"] / n,
            "alpha": float(np.mean(ep["alpha"])),
            "denc": float(np.mean(ep["denc"])), "dtx": float(np.mean(ep["dtx"])),
            "dq": float(np.mean(ep["dq"])), "ddec": 0.35,
            "etx": float(np.mean(ep["etx"])), "ecomp": float(np.mean(ep["ecomp"])),
            "pmean": float(np.mean(ep["pmean"]))}


def main():
    curves = load_curves()
    methods = ["maddpg", "single", "fixed1", "fixed05", "random", "heuristic"]
    log = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        agents = {"maddpg": MADDPG(seed=seed), "single": MADDPG(seed=seed, shared_actor=True)}
        for ep in range(EP):
            noise = 0.3 + (0.01 - 0.3) * ep / max(1, EP - 1)
            for m in methods:
                pol = {"kind": m, "agent": agents.get(m)}
                r = run_episode(pol, curves, rng, train=True, noise=noise if m in ("maddpg", "single") else 0.0)
                log.append({"method": m, "seed": seed, "episode": ep, **{k: round(v, 5) for k, v in r.items()}})
            if (ep + 1) % 10 == 0:
                print(f"seed {seed} ep {ep+1}/{EP}", flush=True)
    pd.DataFrame(log).to_csv(_ARGS.out_log, index=False)
    df = pd.DataFrame(log)
    last = df[df.episode >= EP - 10].groupby(["method", "seed"]).mean(numeric_only=True).reset_index()
    tag = "" if _ARGS.out_log.endswith("maddpg_training_log.csv") else "_pilot"
    last.to_csv(os.path.join(SUPP_ROOT, "results", "radio_metrics_by_seed%s.csv") % tag, index=False)
    agg = last.groupby("method").agg(["mean", "std"])
    agg.to_csv(os.path.join(SUPP_ROOT, "results", "radio_metrics%s.csv") % tag)
    print(agg[[("qoe", "mean"), ("lat", "mean"), ("se", "mean"), ("en", "mean"), ("viol", "mean"), ("alpha", "mean")]].to_string())
    print("OK", len(log))


if __name__ == "__main__":
    main()
