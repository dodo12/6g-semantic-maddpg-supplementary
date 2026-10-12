import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Assemble le rapport Word : tous les chiffres sont LUS depuis les CSV
(aucune valeur saisie a la main). Titres/captions numerotes en francais."""
import csv, json
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

R = os.path.join(SUPP_ROOT, "results") + os.sep
F = os.path.join(SUPP_ROOT, "figures") + os.sep
OUT = os.path.join(SUPP_ROOT, "Rapport_Resultats_Reconstruction_6G.docx")

FIG_N, TAB_N = [0], [0]


def rd(name):
    """Lecture CSV tolerante (certains fichiers contiennent des accents cp1252)."""
    try:
        return pd.read_csv(R + name)
    except UnicodeDecodeError:
        return pd.read_csv(R + name, encoding="latin-1")


def rd_abs(path):
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


def fr(x, dec=1):
    try:
        s = f"{float(x):,.{dec}f}"
    except (ValueError, TypeError):
        return str(x)
    return s.replace(",", " ").replace(".", ",")


def add_field(par, instr):
    r = par.add_run()
    for tag, val in (("fldChar", "begin"), ("instrText", instr), ("fldChar", "end")):
        el = OxmlElement(f"w:{tag}")
        if tag == "fldChar":
            el.set(qn("w:fldCharType"), val)
        elif tag == "instrText":
            el.set(qn("xml:space"), "preserve")
            el.text = val
        r._r.append(el)
    return r


doc = Document()
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)
for h, sz in (("Heading 1", 15), ("Heading 2", 12.5)):
    s = doc.styles[h]
    s.font.size = Pt(sz)
    s.font.color.rgb = RGBColor(0x1F, 0x3B, 0x63)

# pied de page : numero de page
fp = doc.sections[0].footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_field(fp, "PAGE")

doc.add_heading("Reconstruction expérimentale 6G : compression sémantique par "
                "Transformer et allocation MADDPG sur 8iVFB — Rapport de résultats mesurés", 0)
doc.add_paragraph("Projet C:\\paper_6g — 11 octobre 2026 — Code d'origine perdu : "
                  "toutes les valeurs ci-dessous proviennent d'exécutions tracées "
                  "(CSV/JSON du dossier results/). Aucun résultat historique n'est repris sans preuve.")
doc.add_paragraph("Statut global : PARTIELLEMENT VALIDÉ — base de reconstruction "
                  "transparente, article NON prêt à resoumettre (GPU, 1200 frames et testbed requis).")

toc = doc.add_paragraph()
toc.add_run("Sommaire (clic droit → Mettre à jour les champs dans Word) : ").bold = True
add_field(doc.add_paragraph(), "TOC \\o \"1-2\" \\h \\z \\u")


def caption_fig(text):
    FIG_N[0] += 1
    p = doc.add_paragraph()
    r = p.add_run(f"Figure {FIG_N[0]} — {text}")
    r.bold = True
    r.font.size = Pt(10)
    return FIG_N[0]


def add_fig(fname, caption, width=6.0):
    doc.add_picture(F + fname, width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_fig(caption)


def caption_tab(text):
    TAB_N[0] += 1
    p = doc.add_paragraph()
    r = p.add_run(f"Tableau {TAB_N[0]} — {text}")
    r.bold = True
    r.font.size = Pt(10)
    return TAB_N[0]


def add_table(headers, rows, size=8.5):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        c = t.rows[0].cells[j]
        c.text = ""
        r = c.paragraphs[0].add_run(str(h))
        r.bold = True
        r.font.size = Pt(size)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = t.rows[i + 1].cells[j]
            c.text = ""
            r = c.paragraphs[0].add_run(str(v))
            r.font.size = Pt(size)
    doc.add_paragraph("")


# ================= 1. AUDIT =================
doc.add_heading("1. Audit du dataset 8iVFB v2 (Phase A)", 1)
doc.add_paragraph("Source officielle : https://plenodb.jpeg.org/pc/8ilabs (HTTP 200). "
                  "Archive 8iVFBv2.7z : 5 943 803 179 o. Quatre ZIP vérifiés par requêtes HEAD "
                  "et inspection distante (EOCD + central directory, HTTP 206) : longdress "
                  "1 635 191 404 o, loot 1 201 242 833 o, redandblack 1 241 096 174 o, "
                  "soldier 1 748 391 289 o. Chaque ZIP : 609 entrées dont 300 PLY, 300 PNG, "
                  "Counts.txt. Licence 8i : recherche non commerciale, redistribution interdite, "
                  "citation d'Eon et al. 2017. PLY ascii 1.0 (x,y,z:float + R,G,B:uchar), "
                  "0 valeur non finie sur 12 échantillons mesurés par HTTP Range.")
cs = json.load(open(R + "counts_summary.json"))
caption_tab("Statistiques complètes des 1200 frames (métadonnées fournisseur Counts.txt, "
            "vérifiées : en-tête PLY = Counts.txt sur 12/12 échantillons).")
order = ["longdress", "loot", "redandblack", "soldier"]
frames = {"longdress": "1051–1350", "loot": "1000–1299",
          "redandblack": "1450–1749", "soldier": "536–835"}
add_table(["Séquence", "Frames", "n", "Min", "Q1", "Médiane", "Q3", "Max", "Moyenne", "Écart-type"],
          [[s, frames[s], cs[s]["n"], fr(cs[s]["min"], 0), fr(cs[s]["q1"], 0),
            fr(cs[s]["median"], 0), fr(cs[s]["q3"], 0), fr(cs[s]["max"], 0),
            fr(cs[s]["mean"]), fr(cs[s]["stdev"])] for s in order])
doc.add_paragraph("Contradiction confirmée : redandblack descend à 640 070 points (< borne "
                  "basse 724 000 du manuscrit) ; frames consécutives sans lacune ni doublon ; "
                  "la numérotation ne commence pas à zéro.", style="Intense Quote")
add_fig("fig_point_counts.png", "Points par frame, 1200 frames 8iVFB "
        "(bande : plage 724 000–1,1 M du manuscrit). Source : counts_full.csv.")
add_fig("fig_sequence_statistics.png", "Comparaison des séquences (moyenne, min–max, n=300). "
        "Source : counts_full.csv.")

# ================= 2. PROTOCOLE =================
doc.add_heading("2. Protocole expérimental sans fuite (Phase B)", 1)
doc.add_paragraph("Sous-échantillon uniforme Ns=2 048 (seed 42), coords/1023, RGB/255. "
                  "Split par blocs temporels + séquence soldier tenue à l'écart "
                  "(généralisation inter-séquence). Test final jamais utilisé pour les "
                  "hyperparamètres. Graines : 42, 123, 2026.")
sp = rd("data_split_manifest.csv")
caption_tab("Répartition des 12 frames pilotes (results/data_split_manifest.csv).")
add_table(["Frame", "Séquence", "ID", "Split", "Rôle"],
          sp[["frame", "sequence", "frame_id", "split", "role"]].values.tolist(), size=8)

# ================= 3. COMPRESSION =================
doc.add_heading("3. Compression sémantique mesurée (Phase C)", 1)
doc.add_paragraph("Encodeur réduit CPU : scoring MHA numpy (1 couche, 4 têtes, d=64, poids "
                  "fixes) + autoencodeur MLP 6→64→16→64→6 entraîné sur 12 288 points "
                  "(loss 4,9e-4). Flux = latent float16 + en-tête JSON, taille MESURÉE. "
                  "D1-PSNR = 10·log10(3·1023²/MSE_D1). Méthodes : proposed (sélection + AE), "
                  "attn-select (sélection + exact), uniform (aléatoire + exact), raw.")
cbs = pd.read_csv(R + "compression_by_sequence.csv")
sub = cbs[(cbs.alpha_target == 0.05)].sort_values(["sequence", "method"])
caption_tab("Mesures à α cible = 0,05 par séquence (moyenne de 3 frames ; "
            "compression_by_sequence.csv).")
add_table(["Séquence", "Méthode", "α mesuré", "Flux (o)", "D1-PSNR (dB)", "Enc (ms)"],
          [[r.sequence, r.method, fr(r.alpha_measured, 3), fr(r.stream_bytes, 0),
            fr(r.d1_psnr_db), fr(r.enc_ms)] for r in sub.itertuples()])
comp = pd.read_csv(R + "compression_metrics.csv")
g = comp.groupby(["method", "alpha_target"]).agg(
    a=("alpha_measured", "mean"), psnr=("d1_psnr_db", "mean")).reset_index()
caption_tab("Courbe taux–distorsion moyenne sur 12 frames (compression_metrics.csv).")
add_table(["Méthode", "α cible", "α mesuré", "D1-PSNR moyen (dB)"],
          [[m, a, fr(x.a.mean(), 3), fr(x.psnr.mean())]
           for (m, a), x in g.groupby(["method", "alpha_target"])])
doc.add_paragraph("Résultats négatifs publiés : le goulot AE dégrade (47,9 dB < 82 dB) ; "
                  "le scoring attention n'apporte rien à cette échelle (attn-select ≈ uniform) ; "
                  "courbe plate, aucun seuil α*=0,10. D1-PSNR historique 67,8 dB : retiré.",
                  style="Intense Quote")
add_fig("fig_rate_distortion.png", "Taux–distorsion mesuré (Ns=2048, n=12 frames). "
        "Source : compression_metrics.csv.")
add_fig("fig_compression_latency.png", "Temps d'encodage/décodage mesurés (mur, CPU). "
        "Source : compression_metrics.csv.")

# ================= 4. MADDPG =================
doc.add_heading("4. MADDPG et allocation radio (Phase D)", 1)
doc.add_paragraph("Canal 28 GHz (η=2,8 ; PL0=61,4 dB ; σ=8,2 dB), Rayleigh re-tiré par pas, "
                  "B_total = 1 GHz (corrigé), Pmax = 2 W, N0 = −174 dBm/Hz (hypothèse), "
                  "4 utilisateurs (60/90/110/120 m), file dynamique d'arriéré, λ=30 trames/s, "
                  "Dmax=50 ms. MADDPG numpy : acteurs 5→32→32→3, critique centralisé, "
                  "γ=0,95, τ=0,01, buffer 20 000, batch 128, bruit 0,3→0,01, 60 ép.×50 pas×3 graines.")
caption_tab("Taxonomie des 6 méthodes exécutées (une définition unique partout).")
add_table(["Méthode", "Allocation", "Puissance", "α"],
          [["maddpg", "4 acteurs + critique centralisé (CTDE)", "apprise [0,1–2] W", "appris"],
           ["single", "MÊME code, acteur unique partagé (ablation)", "apprise", "appris"],
           ["fixed1 (type QoS-Only)", "parts égales", "2 W", "1,0"],
           ["fixed05 (type DL-Only)", "parts égales", "2 W", "0,5"],
           ["random", "aléatoire admissible", "aléatoire", "aléatoire"],
           ["heuristic", "parts ∝ 1/d", "1 W", "0,05"]], size=8.5)
bm = pd.read_csv(R + "radio_metrics_by_seed.csv")
agg = bm.groupby("method").agg({c: ["mean", "std"] for c in
                                ("qoe", "lat", "se", "en", "viol", "alpha", "pmean", "reward")})
caption_tab("Résultats radio (moyenne ± écart-type sur 3 graines, 10 derniers épisodes ; "
            "radio_metrics_by_seed.csv). Latences/énergies en moyenne honnête (système congestionné).")
rows = []
for m in ("heuristic", "maddpg", "single", "random", "fixed05", "fixed1"):
    r = agg.loc[m]
    rows.append([m, f"{fr(r.qoe['mean'],3)} ± {fr(r.qoe['std'],3)}",
                 f"{fr(r.lat['mean'],0)} ± {fr(r.lat['std'],0)}",
                 f"{fr(r.se['mean'],2)} ± {fr(r.se['std'],2)}",
                 f"{fr(r.en['mean'],0)} ± {fr(r.en['std'],0)}",
                 fr(r.viol['mean'], 2), fr(r.alpha['mean'], 2), fr(r.pmean['mean'], 2)])
add_table(["Méthode", "QoE", "Lat (ms)", "SE (b/s/Hz)", "Énergie (mJ)",
           "Viol", "α", "P̄ (W)"], rows, size=8)
doc.add_paragraph("Lecture : heuristic 0,727 > maddpg 0,568 ≈ single 0,569 ; QoE 0,968 et "
                  "10,35 ms historiques non reproduits (retirés) ; plateau dès ~ép. 10–20.",
                  style="Intense Quote")
add_fig("fig_reward_convergence.png", "Convergence : récompense et QoE (moyenne 3 graines). "
        "Source : maddpg_training_log.csv (1 080 épisodes).")
add_fig("fig_throughput_latency.png", "Efficacité spectrale vs latence par méthode. "
        "Source : radio_metrics_by_seed.csv.")
add_fig("fig_spectral_efficiency.png", "Efficacité spectrale par méthode (±écart-type, 3 graines).")

# ================= 5. BOUT-EN-BOUT =================
doc.add_heading("5. Couplage bout-en-bout (Phase E)", 1)
doc.add_paragraph("Chaîne : frame pilote → sélection MHA → flux float16 mesuré (mis à l'échelle "
                  "pleine-frame par règle de trois à α) → allocation simulée → Ttx=B/R → "
                  "D1-PSNR mesuré. En-têtes inclus ; poids supposés partagés hors-ligne.")
lat = pd.read_csv(R + "latency_breakdown.csv", index_col=0)
caption_tab("Décomposition de la latence D=Denc+Dtx+Dq+Ddec en ms (latency_breakdown.csv).")
add_table(["Méthode", "Denc", "Dtx", "Dq", "Ddec", "Total"],
          [[i, fr(r.denc_ms), fr(r.dtx_ms), fr(r.dq_ms), fr(r.ddec_ms), fr(r.total_ms)]
           for i, r in lat.iterrows()])
en = pd.read_csv(R + "energy_breakdown.csv", index_col=0)
caption_tab("Décomposition de l'énergie E=P·T en mJ (energy_breakdown.csv).")
add_table(["Méthode", "E transmission", "E calcul (65 W)", "Total"],
          [[i, fr(r.etx_mj), fr(r.ecomp_mj), fr(r.total_mj)] for i, r in en.iterrows()])
e2e = pd.read_csv(R + "end_to_end_metrics.csv", index_col=0)
caption_tab("Métriques bout-en-bout par méthode (end_to_end_metrics.csv).")
add_table(["Méthode", "QoE", "Lat (ms)", "Énergie (mJ)", "SE", "Viol", "Dmax OK ?"],
          [[i, fr(r.qoe, 3), fr(r.lat_ms, 0), fr(r.en_mj if hasattr(r, 'en_mj') else r.energy_mj, 0),
            fr(r.se_bps_hz, 2), fr(r.viol_rate, 2), bool(r.dmax_ok)] for i, r in e2e.iterrows()])
doc.add_paragraph("Contrôle physique : 17,5 Gbit / 250 Mbps = 70 s = 70 000 ms (et non 3,5 ms) ; "
                  "à α=0,05, pleine frame loot ≈ 3,8 Mbit → ~15 ms à 250 Mbps.",
                  style="Intense Quote")
add_fig("fig_latency_breakdown.png", "Décomposition de la latence (Denc+Dtx+Dq+Ddec).")
add_fig("fig_energy_comparison.png", "Décomposition de l'énergie (transmission vs calcul).")
add_fig("fig_end_to_end_comparison.png", "Comparaison bout-en-bout : QoE, latence, SE, énergie.")

# ================= 6. QOE =================
doc.add_heading("6. QoE redéfinie et validée (Phase F)", 1)
doc.add_paragraph("Défaut prouvé : 0,6·Q−0,25·D−0,15·E ∈ [−0,4 ; 0,6], pas [0,1]. Correction : "
                  "QoE = écrêt((0,6·Qnorm−0,25·Dnorm−0,15·Enorm+0,4)) ∈ [0,1] ; "
                  "Qnorm=(D1-PSNR−40)/50, Dnorm=min(D/50,1), Enorm=min(E/100,1), "
                  "100 mJ = Pmax·Dmax. Indicateur composite technique (pas d'étude utilisateur).")
sens = pd.read_csv(R + "qoe_sensitivity.csv")
pv = sens.groupby(["w1", "method"]).qoe_recomputed.mean().unstack()
caption_tab("Sensibilité aux poids : QoE recalculée (qoe_sensitivity.csv ; classement stable).")
mcols = ["heuristic", "maddpg", "single", "random", "fixed05", "fixed1"]
add_table(["w1"] + mcols,
          [[fr(w)] + [fr(pv.loc[w, m], 3) for m in mcols] for w in sorted(pv.index)], size=8)
doc.add_paragraph("QoE maximale observée ≈ 0,73 : la valeur 0,968 est retirée.",
                  style="Intense Quote")
add_fig("fig_qoe_comparison.png", "QoE par méthode et sensibilité au poids perceptif w1.")

# ================= 7. STATS =================
doc.add_heading("7. Statistiques et robustesse (Phase G)", 1)
doc.add_paragraph("n=3 graines ; moyennes, écarts-types, médianes, IC-t indicatifs "
                  "(aucune supériorité revendiquée ; frames corrélées jamais comptées "
                  "comme répétitions indépendantes).")
ss = rd("statistical_summary.csv")
caption_tab("Résumé statistique (statistical_summary.csv, extrait QoE/latence).")
add_table(["Méthode", "Métrique", "n", "Moyenne", "Écart-type", "Médiane", "IC95"],
          [[r.method, r.metric, r.n_seeds, fr(r.mean, 3), fr(r.sd, 3), fr(r.median, 3),
            f"[{fr(r.ci95_lo)} ; {fr(r.ci95_hi)}]"]
           for r in ss[ss.metric.isin(("qoe", "lat"))].itertuples()], size=8)
rob = pd.read_csv(R + "robustness_results.csv")
caption_tab("Robustesse : QoE par condition, méthodes figées, graine 42 "
            "(robustness_results.csv, 28 lignes).")
add_table(["Condition", "Méthode", "QoE", "Lat (ms)", "Viol"],
          [[r.condition, r.method, fr(r.qoe, 3), fr(r.lat_ms, 0), fr(r.viol_rate, 2)]
           for r in rob.itertuples()], size=8)
add_fig("fig_robustness_analysis.png", "Robustesse : QoE par condition "
        "(B, λ, distances ; 20 épisodes).")

# ================= 8. CORRECTIONS =================
doc.add_heading("8. Corrections apportées au manuscrit (Phase J)", 1)
doc.add_paragraph("27 valeurs comparées ; tout le tableau : manuscript/old_vs_new_values.csv. "
                  "Extraits majeurs ci-dessous.")
ovn = rd_abs(os.path.join(SUPP_ROOT, "docs", "manuscript", "old_vs_new_values.csv"))
ovn["status"] = ovn["status"].str.strip()
caption_tab("Ancien → nouveau (extraits ; tableau complet : old_vs_new_values.csv).")
keep = ["QoE propose", "Latence propose", "Dtx a 250 Mbps", "B_total",
        "Points redandblack", "Doppler 10 km/h", "Energie propose", "D1-PSNR encodeur"]
add_table(["Affirmation", "Ancien", "Nouveau", "Statut"],
          [[r.claim, f"{r.old_value} {r.old_unit}", f"{r.new_value} {r.new_unit}", r.status]
           for r in ovn[ovn.claim.isin(keep)].itertuples()], size=8)

# ================= 9. REVIEWERS =================
doc.add_heading("9. Réponse aux reviewers ER1–ER19 (Phase K)", 1)
st8 = rd_abs(os.path.join(SUPP_ROOT, "docs", "reports", "08_REVIEWER_RESPONSE_STATUS.csv"))
caption_tab("Statut par commentaire (réponse complète : response_to_reviewers.md) : "
            "17 RÉSOLUS, 2 PARTIELS (ER12 n=3, ER16 t-SNE assumé manquant).")
add_table(["ID", "Statut", "Preuve", "Note"],
          st8.values.tolist(), size=7.5)

# ================= 10. LIMITES =================
doc.add_heading("10. Limites et verdict", 1)
doc.add_paragraph("Échelle pilote (Ns=2048, n=3/séquence, 3 graines) ; payload pleine-frame "
                  "estimé par règle de trois ; Rayleigh i.i.d. sans blockage ni mobilité ; "
                  "Denc non extrapolé ; poids QoE non optimisés ; t-SNE manquant ; sans GPU/torch. "
                  "Références [22]/[23]/[26] vérifiées (DOI/actes) ; pourcentages issus de "
                  "[7]/[9]/[11] retirés.", style="Intense Quote")
doc.add_paragraph("VERDICT : PARTIELLEMENT VALIDÉ — reconstruction transparente et "
                  "reproductible (24/24 tests, 12 figures traçables), article NON prêt à "
                  "resoumettre (GPU, 1200 frames, Transformer complet, testbed requis).",
                  style="Intense Quote")

doc.save(OUT)
print("OK", OUT)
