# Supplementary Material — Perception-Centric QoE Optimization for 6G
Volumetric Point Cloud Communications (experimental reconstruction)

Reconstruction partielle, transparente et reproductible d'un cadre 6G combinant
compression sémantique (Transformer réduit) et allocation MADDPG sur le benchmark
8i Voxelized Full Bodies (8iVFB v2). Code d'origine perdu : aucun résultat historique
n'est repris sans preuve ; les valeurs non reproduites sont RETIRÉES et remplacées
par des mesures tracées. Statut : PARTIELLEMENT VALIDÉ (voir `docs/FINAL_VALIDATION_REPORT.md`).

## Contenu
- `code/src/` : chargeur dataset, encodeur sémantique (MHA numpy + AE sklearn),
  canal 28 GHz, MADDPG numpy, QoE corrigée.
- `code/scripts/` : `run_phaseB/C/D`, `run_robustness`, `finalize`, `make_figures`,
  `build_docx_report`, `fetch_counts` (ordre d'exécution = ordre alphabétique B→figures).
- `code/tests/` : 24 tests unitaires/fumée (tous passés le 2026-10-12).
- `code/configs/` : protocole (split sans fuite), radio, hypothèses H-*.
- `code/data_processed/subsampled.npz` : 12 frames pilotes Ns=2048 (permet de
  reproduire SANS les 230 Mo de PLY, non redistribuables).
- `results/` : 17 CSV/JSON finaux (R = résultats mesurés, jamais saisis).
- `figures/` : 12 figures PNG + PDF (toutes générées depuis les CSV).
- `docs/` : diagnostic, matrice reviewers ER1–ER19, rapports 02–08, manuscrit révisé
  (extraits), journal des modifications, ancien→nouveau, preuves par affirmation.
- `Rapport_Resultats_Reconstruction_6G.docx` : rapport unifié (14 tableaux, 12 figures).

## Résultats principaux (mesurés)
Compression α=0,05 : sélection-attention 83,6 dB ≈ uniforme 82,0 dB ; goulot AE
47,9 dB (résultat négatif publié). Radio (3 graines) : heuristique QoE **0,727** >
MADDPG 0,568 ≈ mono-agent 0,569 > aléatoire/fixes. 17,5 Gbit/250 Mbps = **70 s**
(pas 3,5 ms). QoE historique 0,968 et −97,2 % : retirés.

## Liens utiles
- Dataset officiel (page, licence, archives) : https://plenodb.jpeg.org/pc/8ilabs
- Archives directes : `…/pc/8ilabs/{longdress,loot,redandblack,soldier}.zip`,
  complète `…/pc/8ilabs/8iVFBv2.7z` (~5,9 Go) ; licence : `…/pc/8ilabs/license.pdf`
  (recherche non commerciale, redistribution interdite — les PLY ne sont PAS inclus ici).
- Références vérifiées : Lowe et al., MADDPG, NeurIPS 2017
  (https://proceedings.neurips.cc/paper_files/paper/2017/file/68a9750337a418a86fe06c1991a1d64c-Paper.pdf) ;
  Xie et al., DeepSC, IEEE TSP 69 (doi:10.1109/TSP.2021.3071210) ;
  Bourtsoulatze et al., DeepJSCC, IEEE TCCN 5(3) (doi:10.1109/TCCN.2019.2919300) ;
  3GPP TR 38.901 v16.1.0.

## Reproduction (CPU, ~1 h : Phase D ~30 min)
```bash
pip install -r code/requirements.txt
python code/scripts/run_phaseB.py      # besoin des PLY (EIGHTIVFB_DATA) OU sauter (npz fourni)
python code/scripts/run_phaseC.py
python code/scripts/run_phaseD.py      # 60 ep. x 50 pas x 6 methodes x 3 graines
python code/scripts/finalize.py
python code/scripts/run_robustness.py
python code/scripts/make_figures.py
python -m unittest discover -s code/tests -t code
```
Environnement vérifié : Python 3.14.4, numpy 2.4.5, pandas 3.0.3, matplotlib 3.10.9,
scipy 1.17.1, scikit-learn 1.8.0 (Windows 10 CPU, sans GPU/torch).

## Limites (à citer dans l'article)
Échelle pilote (Ns=2048, n=3/séquence, 3 graines) ; payload pleine-frame estimé ;
Rayleigh i.i.d. sans blockage/mobilité ; poids QoE non optimisés ; t-SNE manquant.
