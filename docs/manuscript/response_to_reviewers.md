# Réponse aux reviewers (ER1–ER19) — ton respectueux, sans sur-déclaration

> Le code d'origine étant perdu, AUCUNE expérience historique n'est revendiquée.
> Chaque point est traité par correction du texte et/ou nouvelle expérience
> tracée (`evidence`). Les valeurs historiques non reproduites sont RETIRÉES,
> pas ajustées.

## ER1 (résumé « 18,6–22,8 % » — bases mélangées)
Problème : gains vs ablation confondus. Réponse : fourchette supprimée du résumé
révisé ; chaque comparaison utilise sa propre base (`end_to_end_metrics.csv`).
Preuve : `manuscript/updated_manuscript.md` (résumé), `old_vs_new_values.csv`.
Limite : historique non rejouable. **RÉSOLU (par retrait + remplacement).**

## ER2 (Single-DRL contradictoire ; Bonferroni ; labels figures)
Réponse : taxonomie réécrite — 6 méthodes exécutées aux définitions uniques
(`single` = acteur partagé) ; toutes les figures régénérées avec légendes
cohérentes au code. Preuve : `scripts/run_phaseD.py`, FIG-M1. **RÉSOLU.**

## ER3 (réf [20], plage 735 k, split 180 vs 300 frames)
Réponse : [20] découplée de 8iVFB ; [12] → URL plenodb officielle ; Table IV
corrigée par audit (moyennes + min 640 070 signalé) ; protocole décrit tel
qu'exécuté (12 pilotes, §Phase B). Preuve : `reports/02_DATASET_AUDIT.md`,
`counts_full.csv`. **RÉSOLU.**

## ER4 (12 tests vs 3 baselines ; r de Rosenthal ; n=120)
Réponse : statistiques historiques retirées (données perdues) ; protocole actuel
n=3 graines, descriptif, sans p-valeur ; effet « rank-biserial » non repris.
Preuve : `statistical_summary.csv`, `reports/07`. **RÉSOLU (retrait + protocole honnête).**

## ER5 (Fig.2 : MSE seule, convergence ~2 ép. pas 20, titre Fig.1)
Réponse : figure remplacée par la courbe de notre AE (loss 4,9e-4) ; texte aligné
sur le tracé. Preuve : logs d'entraînement §03. **RÉSOLU.**

## ER6 (Fig.3 : 0,98 vs 0,968, Single-DRL en légende, une seule ligne)
Réponse : nouvelle FIG-M1 depuis `maddpg_training_log.csv` (plateau ~ép. 10–20,
QoE ≤ 0,73) ; légendes = noms du code. **RÉSOLU.**

## ER7 (Fig.4 invérifiable — CRITIQUE)
Réponse : analyse de seuil ABANDONNÉE ; nouvelle FIG-C1 (nuage mesuré, courbe
plate, pas de R² revendiqué). **RÉSOLU (retrait justifié).**

## ER8 (17,5 Gbit / 250 Mbps = 3,5 s, pas 3,5 ms — CRITIQUE)
Réponse : calcul refait (70 s) ; charge de référence remplacée par flux mesurés
(~3,8 Mbit) ; B_total corrigé en GHz ; −97,2 % retiré. Preuves : tests unitaires
OK, `payload` mesuré. **RÉSOLU.**

## ER9 (SE indépendante du payload ; Fig.6 0,02 vs Table III)
Réponse : interprétation restreinte ; FIG-M2/M3 + Table III régénérées depuis les
mêmes CSV (SE 1,7–2,4). **RÉSOLU.**

## ER10 (Fig.5 : courbes plates, pas de CIs/marqueurs)
Réponse : nouvelle figure temporelle depuis les logs, sans allégation de
fluctuations ; CIs là où n le permet. **RÉSOLU.**

## ER11 (Fig.6 énergie 1556 vs 20,58 mJ ; axe linéaire)
Réponse : équation E=P·T ajoutée Sec III ; FIG-E1 + Table V régénérées depuis
`energy_breakdown.csv` (287–13 824 mJ honnêtes). **RÉSOLU.**

## ER12 (Fig.7 : dispersions mal attribuées)
Réponse : boxplots régénérés ; n=3/seq → valeur indicative, étiquetée.
**PARTIELLEMENT RÉSOLU** (échantillon trop petit pour des IQR robustes).

## ER13 (Fig.8 : axe linéaire ; σ≈6,8 > 5 ms)
Réponse : descriptions d'axes corrigées depuis les données ; σ recalculé et
publié tel quel. **RÉSOLU.**

## ER14 (Fig.9 : pourcentages CDF à recalculer)
Réponse : pourcentages recalculés depuis les CSV ; CDF décrites sans embellissement.
**RÉSOLU.**

## ER15 (énergie = 2W×latence ; Fig.10 353 vs 706 ; E indéfinie)
Réponse : définition ajoutée ; décomposition Etx/Ecomp mesurée (Etx > 98 %) ;
anciennes valeurs retirées. **RÉSOLU.**

## ER16 (t-SNE : colorbar 0,75–0,91, pas de clusters)
Réponse : analyse latente non reconduite à l'identique ; description restreinte
aux observations ; embeddings disponibles sur demande du code. **PARTIELLEMENT
RÉSOLU** (pas de nouvelle figure t-SNE produite — signalé comme MANQUANT §7 du
rapport final plutôt que fabriqué).

## ER17 ([11] 18–24 % invérifiable)
Réponse : la référence EXISTE (T-ITS 27(2), 2026, vérifié) mais les % sont
retirés. **RÉSOLU.**

## ER18 ([9] 30–60 %, [22]/[7] 70 % invérifiables)
Réponse : [22] confirmé (TCCN 2019, DOI vérifié) mais « 70 % » retiré ; « 30–60 % »
retiré. **RÉSOLU.**

## ER19 (Doppler 0,78 kHz faux)
Réponse : corrigé à ≈ 259 Hz avec formule et test (`test_doppler`). **RÉSOLU.**

**Bilan : 17 RÉSOLUS, 2 PARTIELLEMENT (ER12 échantillon, ER16 figure manquante assumée).**
