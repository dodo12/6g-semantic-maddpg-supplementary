# 00 — Diagnostic projet (Jalon 1)

Date : 2026-10-11. Projet : `C:\paper_6g`. Audit antérieur : `C:\8ivfb_audit` (intact, non modifié).

## 1. Fichiers identifiés (lu / exécuté / vérifié / identifié)

| Fichier | Statut |
|---|---|
| `C:\8ivfb_audit\01_audit_8ivfb.py` | lu, exécuté précédemment (12 PLY mesurés) — non réexécuté ici |
| `C:\8ivfb_audit\results\sequence_summary.csv` | lu + vérifié, copié dans `original/` |
| `C:\8ivfb_audit\results\dataset_manifest.csv` | lu + vérifié, copié dans `original/` |
| `C:\8ivfb_audit\results\payload_latency_audit.csv` | lu + vérifié, copié dans `original/` |
| `C:\8ivfb_audit\results\REPORT_PHASE1.md`, `dataset_metadata.json`, `frame_integrity_report.csv` | lus, copiés dans `original/` |
| `C:\8ivfb_audit\data\*.ply` (12 fichiers, ~230 Mo) | vérifiés présents, utilisés comme données d'entrée |
| Manuscrit cible (Transformer + MADDPG + QoE 6G) | **AUCUN fichier source** : texte fourni inline dans la consigne → transcrit en valeurs de référence dans `original/MANUSCRIPT_SOURCE.md` (NON relu depuis un fichier) |
| Commentaires ER1–ER19 | fournis inline avec le manuscrit → transcrits en `01_REVIEWER_ACTION_MATRIX.csv` (lus) |
| `Desktop\paper 38\paper 38.docm` | identifié : article PV sans rapport (vérifié via unzip, résumé en §5) |
| `Desktop\Dear Editor and Reviewers.docx` | lu : concerne un AUTRE article (DRL+GA+RIS) → contexte uniquement (§5) |
| Code original de l'étude | **perdu, confirmé** : aucune archive retrouvée |

## 2. Informations scientifiques récupérées (manuscrit inline)
- Système : U=4 utilisateurs × 4 séquences 8iVFB, fc=28 GHz, PL(η=2.8, PL0=61.4 dB, σ=8.2 dB, d0=1 m), Rayleigh, B_total=1 Gbps (**unité suspecte**, voir ER8), Pmax=2 W, Dmax=50 ms.
- Encodeur : 4 couches, 8 têtes, d=256, FFN 512, GELU, latent 128, loss MSE+0.1·Chamfer, 80 époques, Adam 3e-4, split 70/15/15.
- MADDPG : Dec-POMDP, CTDE + critique à attention, δ=0.95, τ=0.01, buffer 1e6, batch 256, lr 1e-4/1e-3, 120 épisodes × 300 pas, bruit 0.3→0.01, κ=10.
- QoE = 0.6·Qnorm − 0.25·Dnorm − 0.15·Enorm, « ∈ [0,1] » (**FAUX**, voir §4).
- Valeurs revendiquées : QoE 0.968 [0.961,0.975], latence 367.2→10.35 ms (−97.2 %), α=0.05, SE 1.56 vs 1.59, énergie 734.4→20.58 mJ, D1-PSNR 67.8 dB, S_frame≈17.5 Gbits, Ru≈250 Mbps.

## 3. Paramètres connus / inconnus
- Connus : tout le §2 + stats audit (4×300 frames, IDs loot 1000–1299, longdress 1051–1350, redandblack 1450–1749, soldier 536–835 ; PLY ascii x,y,z float + RGB uchar).
- Inconnus (→ `configs/assumptions.yaml`) : N0 (densité de bruit),λ/µ de file M/D/1, fenc (1.2 ms admis), Ddec, P_compute, hyperparamètres exacts du grid-search ω, graines, réalisations de canal, code des 11 figures.

## 4. Résultats anciens : vérifiables vs non vérifiables
- Vérifiables (et À CORRIGER) : 17.5 Gbits/250 Mbps = 70 s ≠ 3.5 ms (ER8) ; QoE∈[0,1] faux (min −0.4, max 0.6) ; Doppler 0.78 kHz faux à 10 km/h (vrai ≈ 259 Hz, ER19) ; B_total en Gbps faux pour une bande (ER8) ; redandblack min 640 070 < 724 000 (audit) ; Table III/IV vs Fig.6 contradictions signalées (ER9/ER11).
- Non vérifiables (code perdu, pas de logs) : QoE 0.968, latences 10.35/367.2 ms, SE, énergies, courbes Figs.2–11, D1-PSNR 67.8 dB, α→0.05 appris, t-SNE. → **retirés, remplacés par nouvelles expériences**.

## 5. Documents tiers examinés (contexte, pas preuves)
- `paper 38.docm` : article photovoltaïque (souillure/ombrage, La Réunion) — hors sujet, aucune réutilisation.
- `Dear Editor and Reviewers.docx` : réponse à reviewers pour un article DRL+GA+RIS (autre méthode, autre revue). Thèmes récurrents utiles : comparaisons quantitatives, courbes DRL, labels de figures en anglais, modèle système. Ne constitue PAS le jeu de reviewers du présent manuscrit.

## 6. Dépendances / matériel
- Python 3.14.4, numpy 2.4.5, pandas 3.0.3, matplotlib 3.10.9, scipy 1.17.1, scikit-learn 1.8.0, requests 2.34.2. **Pas de torch/TF, pas de GPU** → implémentation CPU numpy/sklearn, version réduite documentée (§8 du prompt maître).

## 7. Plan expérimental (jalons 2–6)
B : split par blocs + holdout séquence soldier (généralisation inter-séquence). C : autoencodeur MLP entraîné (sklearn) + scoring MHA numpy à poids fixés (seed), flux float16 mesuré, baselines raw + sous-échantillonnage. D : MADDPG numpy 4 agents + 4 baselines (fixe, aléatoire, heuristique, DDPG centralisé), 3 graines. E : couplage avec flux mesurés, T_tx=B/R, énergie. F : QoE corrigée (re-normalisée [0,1]) + sensibilité. G : stats descriptives + CI, robustesse (débit, distance/Doppler, α, poids). H–K : figures traçables, manuscrit révisé (copie .md), réponse ER1–19, validation finale.
