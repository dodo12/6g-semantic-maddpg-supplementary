# Manuscrit révisé — copie de travail (RECONSTRUCTION, pas confirmation)

> Statut : révision partielle issue d'expériences RECONSTRUITES (CPU/numpy,
> 12 frames pilotes). Ne confirme PAS les résultats historiques : les valeurs non
> reproduites sont RETIRÉES et remplacées par les mesures `results/` ou marquées
> NON VÉRIFIÉES. Titre et structure conservés.

## Titre (inchangé)
Perception-Centric QoE Optimization for 6G Volumetric Point Cloud Communications
via Transformer Semantic Encoding and Multi-Agent Deep Reinforcement Learning:
A Trace-Driven Benchmark Evaluation — **RECONSTRUCTION EXPERIMENTALE** (note ajoutée).

## Résumé (RÉÉCRIT — remplace les valeurs 0,968 / 18,6–22,8 % / 97,2 % / 0,050 appris)
« Sur 12 frames pilotes 8iVFB (Ns=2048, CPU), un encodeur réduit (attention +
autoencodeur) atteint 83,6 dB D1-PSNR à α_mes=0,026 sans battre le
sous-échantillonnage uniforme (82,0 dB). Couplé à une simulation 28 GHz
(pathloss 3GPP UMi-NLOS, Rayleigh), une heuristique d'allocation (α=0,05)
obtient QoE corrigée 0,727 ; MADDPG (numpy, 60 épisodes × 3 graines) atteint
0,568 et n'apprend pas de gain multi-agent à ce budget. La charge de
17,5 Gbits à 250 Mbps exige 70 s (et non 3,5 ms) : l'affirmation de latence
est retirée. »

## III-B (corrigé)
B_total = **1 GHz** (le « 1 Gbps » était l'unité d'un débit — ER8).
N0 = −174 dBm/Hz (hypothèse H-N0, absente du texte d'origine).

## III-C (corrigé)
D = Denc+Dtx+Dq+Ddec avec Dq = arriéré/débit (file dynamique ; le M/D/1
stationnaire par pas est invalide sous fading non stationnaire).
S_frame : mis à l'échelle depuis les flux MESURÉS (règle de trois à α) ;
17,5 Gbits retiré comme charge de référence (ER8 : incohérent avec 1,1 M pts).

## III-D (corrigé — ER : bornes)
QoE = clip((0,6·Qnorm − 0,25·Dnorm − 0,15·Enorm + 0,4)) ∈ [0,1] ;
plages Q [40,90] dB, D [0,50] ms, E [0,100] mJ = Pmax·Dmax.
L'ancienne formule ne garantissait PAS [0,1] ([−0,4 ; 0,6]).

## V-A (corrigé — exécuté réellement)
12 frames pilotes (split §Phase B : train 6 / val 3 futures / test soldier 3) ;
pas de split 70/15/15 sur 1200 (données indisponibles) ; D1-PSNR d'entrée du
corpus : non mesuré (retiré) ; citation dataset : URL officielle plenodb (pas le
miroir github) ; [20] retirée du support 8iVFB (ER3).

## V-E (remplacé)
Nouveau Tableau III = `end_to_end_metrics.csv` (heuristic 0,727 ; maddpg 0,568 ;
latences honnêtes ; SE ≈ 1,7–2,4). Anciens 0,968/10,35 ms/97,2 % : RETIRÉS.
Parité SE : interprétation restreinte (SE indépendante du payload — ER9).

## V-H (Table IV corrigée, moyennes d'audit)
loot 793 821 / soldier 1 075 299 / longdress 834 315 / redandblack 727 071
(min 640 070 — contradiction 724 k signalée) ; distances et α : valeurs de
simulation de la reconstruction, pas du système d'origine.

## VI-E (corrigé — ER19)
Doppler 10 km/h @ 28 GHz ≈ **259 Hz** (0,78 kHz = 30 km/h).

## Références (vérifiées le 2026-10-11)
[22] DeepJSCC confirmé (TCCN 5(3), DOI 10.1109/TCCN.2019.2919300) mais « 70 % »
retiré (non attribuable). [23] DeepSC confirmé (TSP 69). [26] MADDPG confirmé
(NeurIPS 2017, pp. 6379–6390). [11] existe (T-ITS 27(2), 2026) mais « 18–24 % »
non vérifié → retiré. « 30–60 % » ([9]) → retiré. [12] → URL plenodb officielle.
