import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Phase H : TOUTES les figures sont generees depuis les CSV (jamais de valeurs
saisies). Style sobre, unites SI, barres d'erreur quand justifiees."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.path.join(SUPP_ROOT, "results") + os.sep
F = os.path.join(SUPP_ROOT, "figures") + os.sep
plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white",
                     "font.family": "sans-serif", "font.size": 9,
                     "axes.grid": True, "grid.alpha": 0.3})
trace = []


def save(fig_id, filename, source_csv, metrics):
    for ext in ("png", "pdf"):
        plt.savefig(os.path.join(F, filename + "." + ext), dpi=150 if ext == "png" else None,
                    bbox_inches="tight")
    plt.close()
    trace.append({"figure_id": fig_id, "filename": filename + ".png",
                  "source_csv": source_csv, "plotting_script": "scripts/make_figures.py",
                  "experiment_id": "repro-2026-10", "metrics": metrics,
                  "validation_status": "CSV-trace"})


comp = pd.read_csv(R + "compression_metrics.csv")
cbs = pd.read_csv(R + "compression_by_sequence.csv")
log = pd.read_csv(R + "maddpg_training_log.csv")
bm = pd.read_csv(R + "radio_metrics_by_seed.csv")
lat = pd.read_csv(R + "latency_breakdown.csv", index_col=0)
en = pd.read_csv(R + "energy_breakdown.csv", index_col=0)
e2e = pd.read_csv(R + "end_to_end_metrics.csv", index_col=0)
sens = pd.read_csv(R + "qoe_sensitivity.csv")
rob = pd.read_csv(R + "robustness_results.csv")
counts = pd.read_csv(R + "counts_full.csv")

# --- dataset : 1200 compteurs ---
fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharey=False)
for ax, seq in zip(axes.flat, ("longdress", "loot", "redandblack", "soldier")):
    sub = counts[counts.sequence == seq].reset_index()
    ax.plot(sub.index, sub.points_counts_txt, lw=0.7)
    ax.axhspan(724000, 1100000, alpha=0.12)
    ax.set_title(seq)
    ax.set_xlabel("indice de frame (ordre Counts.txt)")
    ax.set_ylabel("points")
fig.suptitle("8iVFB : points par frame, 1200 frames (metadonnees fournisseur)")
fig.tight_layout()
save("FIG-D1", "fig_point_counts", "counts_full.csv", "points/frame")

fig, ax = plt.subplots(figsize=(8, 4.5))
q = counts.groupby("sequence").points_counts_txt
stats = pd.DataFrame({"mean": q.mean(), "min": q.min(), "max": q.max()})
ax.bar(stats.index, stats["mean"])
ax.errorbar(stats.index, stats["mean"], yerr=[stats["mean"] - stats["min"], stats["max"] - stats["mean"]],
            fmt="none", ecolor="black", capsize=5)
ax.set_ylabel("points (moyenne, etendue min-max)")
ax.set_title("Comparaison des sequences 8iVFB (n=300/séquence)")
fig.tight_layout()
save("FIG-D2", "fig_sequence_statistics", "counts_full.csv", "mean/min/max")

# --- compression : taux-distorsion ---
fig, ax = plt.subplots(figsize=(7, 4.5))
for m in ("proposed", "attn-select", "uniform"):
    sub = comp[comp.method == m].groupby("alpha_target").agg(
        a=("alpha_measured", "mean"), psnr=("d1_psnr_db", "mean"),
        psd=("d1_psnr_db", "std")).reset_index()
    ax.errorbar(sub.a, sub.psnr, yerr=sub.psd, marker="o", label=m, capsize=3)
ax.set_xlabel("alpha mesure (octets flux / octets bruts)")
ax.set_ylabel("D1-PSNR (dB)")
ax.set_title("Taux-distorsion mesure (Ns=2048, n=12 frames)")
ax.legend()
fig.tight_layout()
save("FIG-C1", "fig_rate_distortion", "compression_metrics.csv", "alpha/D1-PSNR")

fig, ax = plt.subplots(figsize=(7, 4.5))
sub = comp[comp.method.isin(("proposed", "attn-select"))].groupby("alpha_target").agg(
    e=("enc_ms", "mean"), d=("dec_ms", "mean")).reset_index()
x = np.arange(len(sub))
w = 0.35
ax.bar(x - w / 2, sub.e, w, label="encodage")
ax.bar(x + w / 2, sub.d, w, label="decodage (AE seul)")
ax.set_xticks(x, [str(a) for a in sub.alpha_target])
ax.set_xlabel("alpha cible")
ax.set_ylabel("ms (mur, CPU)")
ax.set_title("Temps d'encodage/decodage mesures")
ax.legend()
fig.tight_layout()
save("FIG-C2", "fig_compression_latency", "compression_metrics.csv", "enc_ms/dec_ms")

# --- MADDPG : convergence ---
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, col in zip(axes, ("reward", "qoe")):
    for m in ("maddpg", "single", "heuristic", "fixed1"):
        s = log[log.method == m].groupby("episode")[col].mean()
        ax.plot(s.index, s.values, lw=1.2, label=m)
    ax.set_xlabel("episode")
    ax.set_ylabel("recompense/pas" if col == "reward" else "QoE moyenne")
    ax.legend(fontsize=8)
axes[0].set_title("Recompense d'entrainement (moyenne 3 graines)")
axes[1].set_title("QoE (moyenne 3 graines)")
fig.tight_layout()
save("FIG-M1", "fig_reward_convergence", "maddpg_training_log.csv", "reward/QoE")

# --- radio : debit vs latence + SE + energie ---
fig, ax = plt.subplots(figsize=(7, 4.5))
agg = bm.groupby("method").agg(se=("se", "mean"), lat=("lat", "mean"),
                               se_sd=("se", "std"), lat_sd=("lat", "std")).reset_index()
ax.errorbar(agg.se, agg.lat, xerr=agg.se_sd, yerr=agg.lat_sd, fmt="o", capsize=4)
for _, r in agg.iterrows():
    ax.annotate(r.method, (r.se, r.lat), fontsize=8)
ax.set_xlabel("efficacite spectrale (b/s/Hz)")
ax.set_ylabel("latence moyenne (ms)")
ax.set_title("Debit vs latence par methode")
fig.tight_layout()
save("FIG-M2", "fig_throughput_latency", "radio_metrics_by_seed.csv", "SE/latency")

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.bar(agg.method, agg.se, yerr=agg.se_sd, capsize=4)
ax.set_ylabel("b/s/Hz")
ax.set_title("Efficacite spectrale par methode (moyenne 3 graines)")
plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
fig.tight_layout()
save("FIG-M3", "fig_spectral_efficiency", "radio_metrics_by_seed.csv", "SE")

fig, ax = plt.subplots(figsize=(7, 4.5))
x = np.arange(len(en))
ax.bar(x, en.etx_mj, label="transmission (P*Ttx)")
ax.bar(x, en.ecomp_mj, bottom=en.etx_mj, label="calcul (65W*Tenc)")
ax.set_xticks(x, en.index, rotation=20)
ax.set_ylabel("mJ")
ax.set_title("Decomposition de l'energie")
ax.legend()
fig.tight_layout()
save("FIG-E1", "fig_energy_comparison", "energy_breakdown.csv", "Etx/Ecomp")

fig, ax = plt.subplots(figsize=(7, 4.5))
x = np.arange(len(lat))
b1 = ax.bar(x, lat.denc_ms, label="enc")
b2 = ax.bar(x, lat.dtx_ms, bottom=lat.denc_ms, label="tx")
b3 = ax.bar(x, lat.dq_ms, bottom=lat.denc_ms + lat.dtx_ms, label="file")
ax.bar(x, lat.ddec_ms, bottom=lat.denc_ms + lat.dtx_ms + lat.dq_ms, label="dec")
ax.set_xticks(x, lat.index, rotation=20)
ax.set_ylabel("ms (moyenne, echelle pilote pleine-charge)")
ax.set_title("Decomposition de la latence (Denc+Dtx+Dq+Ddec)")
ax.legend()
fig.tight_layout()
save("FIG-E2", "fig_latency_breakdown", "latency_breakdown.csv", "Denc/Dtx/Dq/Ddec")

fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for ax, col, lab in zip(axes.flat, ("qoe", "lat_ms", "se_bps_hz", "energy_mj"),
                        ("QoE corrigee", "latence (ms)", "SE (b/s/Hz)", "energie (mJ)")):
    ax.bar(e2e.index, e2e[col])
    ax.set_title(lab)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", fontsize=8)
fig.suptitle("Bout-en-bout par methode (moyenne 3 graines)")
fig.tight_layout()
save("FIG-E3", "fig_end_to_end_comparison", "end_to_end_metrics.csv", "QoE/lat/SE/E")

# --- QoE : comparaison + sensibilite ---
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
q = bm.groupby("method").agg(m=("qoe", "mean"), s=("qoe", "std")).reset_index()
axes[0].bar(q.method, q.m, yerr=q.s, capsize=4)
axes[0].set_title("QoE corrigee par methode")
plt.setp(axes[0].get_xticklabels(), rotation=20, ha="right")
s2 = sens[sens.w2 == 0.25].groupby("w1").agg(m=("qoe_recomputed", "mean")).reset_index()
axes[1].plot(s2.w1, s2.m, marker="o")
axes[1].set_xlabel("w1 (poids qualite)")
axes[1].set_ylabel("QoE recalculee (moyenne)")
axes[1].set_title("Sensibilite au poids perceptif (w2=0.25)")
fig.tight_layout()
save("FIG-Q1", "fig_qoe_comparison", "qoe_results.csv+qoe_sensitivity.csv", "QoE/w1")

# --- robustesse ---
fig, ax = plt.subplots(figsize=(9, 4.5))
for m in rob.method.unique():
    s = rob[rob.method == m]
    ax.plot(s.condition, s.qoe, marker="o", label=m)
ax.set_ylabel("QoE")
ax.set_title("Robustesse : QoE par condition (graine 42, 20 ep.)")
plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=8)
ax.legend(fontsize=8)
fig.tight_layout()
save("FIG-G1", "fig_robustness_analysis", "robustness_results.csv", "QoE/condition")

pd.DataFrame(trace).to_csv(R + "results_figure_traceability.csv", index=False)
print("OK figures:", len(trace))
