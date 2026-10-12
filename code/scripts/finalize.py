import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Finalisation : fusionne les 3 runs officiels ; produit les CSV E/F/G.
Sensibilite QoE : recalculee algebriquement depuis les moyennes journalisees
(Qn inverse depuis QoE/Dn/En ; ecrêtages signales)."""
import sys, json
import numpy as np
import pandas as pd

R = os.path.join(SUPP_ROOT, "results") + os.sep
df = pd.concat([pd.read_csv(R + f"final_seed{s}.csv") for s in (42, 123, 2026)], ignore_index=True)
df.to_csv(R + "maddpg_training_log.csv", index=False)
EP = df.episode.max()
last = df[df.episode >= EP - 9].groupby(["method", "seed"]).mean(numeric_only=True).reset_index()
last.to_csv(R + "radio_metrics_by_seed.csv", index=False)
agg = last.groupby("method").agg(["mean", "std"])
agg.to_csv(R + "radio_metrics.csv")

m = last.groupby("method").mean(numeric_only=True)
# --- E : decompositions (moyennes sur graines des moyennes ep.) ---
lat = pd.DataFrame({"denc_ms": m.denc, "dtx_ms": m.dtx, "dq_ms": m.dq,
                    "ddec_ms": m.ddec, "total_ms": m.denc + m.dtx + m.dq + m.ddec})
lat.to_csv(R + "latency_breakdown.csv")
en = pd.DataFrame({"etx_mj": m.etx, "ecomp_mj": m.ecomp, "total_mj": m.etx + m.ecomp})
en.to_csv(R + "energy_breakdown.csv")
e2e = pd.DataFrame({"qoe": m.qoe, "lat_ms": m.lat, "energy_mj": m.en, "se_bps_hz": m.se,
                    "viol_rate": m.viol, "alpha": m.alpha,
                    "dmax_ok": (m.lat <= 50.0)})
e2e.to_csv(R + "end_to_end_metrics.csv")
# --- F : QoE ---
last[["method", "seed", "qoe"]].to_csv(R + "qoe_results.csv", index=False)
with open(R + "qoe_ranges.json", "w") as f:
    json.dump({"Q_dB": [40.0, 90.0], "D_ms": [0.0, 50.0], "E_mJ": [0.0, 100.0],
               "weights": [0.6, 0.25, 0.15], "correction": "(raw+0.4)/1.0"}, f, indent=2)
sens = []
for _, r in last.iterrows():
    Dn = min(1.0, r.lat / 50.0)
    En = min(1.0, r.en / 100.0)
    Qn = (r.qoe - 0.4 + 0.25 * Dn + 0.15 * En) / 0.6  # inversion algebrique
    clipped = (r.lat / 50.0 > 1.0) or (r.en / 100.0 > 1.0)
    for w1 in (0.4, 0.5, 0.6, 0.7, 0.8):
        for w2 in (0.1, 0.25, 0.4):
            w3 = round(1 - w1 - w2, 6)
            if w3 < 0.05 - 1e-9 or w3 > 0.25 + 1e-9:
                continue
            sens.append({"method": r.method, "seed": r.seed, "w1": w1, "w2": w2, "w3": w3,
                         "qoe_recomputed": min(1.0, max(0.0, (w1 * Qn - w2 * Dn - w3 * En + 0.4))),
                         "clipped_inputs": clipped})
pd.DataFrame(sens).to_csv(R + "qoe_sensitivity.csv", index=False)
# --- G : resume statistique (n=3 graines ; IC-t indicatifs) ---
from scipy import stats as _st
rows = []
for method, sub in last.groupby("method"):
    for metric in ("qoe", "lat", "se", "en"):
        x = sub[metric].to_numpy()
        ci = _st.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=_st.sem(x)) if len(x) > 1 else (np.nan, np.nan)
        rows.append({"method": method, "metric": metric, "n_seeds": len(x),
                     "mean": x.mean(), "sd": x.std(ddof=1), "median": np.median(x),
                     "ci95_lo": ci[0], "ci95_hi": ci[1],
                     "note": "n=3 : IC indicatifs, aucune superiorite revendiquee"})
pd.DataFrame(rows).to_csv(R + "statistical_summary.csv", index=False)
print("OK finalize")
print(lat.round(2).to_string())
print(en.round(2).to_string())
