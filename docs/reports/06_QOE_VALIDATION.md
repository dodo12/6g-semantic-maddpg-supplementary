# 06 — QoE : redéfinition et validation (Phase F)

## Preuve du défaut (test `test_manuscript_claim_false` : OK)
QoE = 0,6·Q − 0,25·D − 0,15·E avec Q,D,E ∈ [0,1] donne [−0,4 ; 0,6], **pas [0,1]**.
L'affirmation du manuscrit (Sec. III-D) est mathématiquement fausse.

## Définition corrigée (`src/metrics/qoe.py`, `qoe_ranges.json`)
- Qnorm=(D1-PSNR−40)/50 dB ; Dnorm=min(D/50 ms,1) ; Enorm=min(E/100 mJ,1),
  100 mJ = Pmax·Dmax (référence physique) ; poids (0,6 ; 0,25 ; 0,15).
- QoE = clip((0,6·Q − 0,25·D − 0,15·E + 0,4)) ∈ [0,1] par construction (testé).
- Indicateur composite TECHNIQUE (pas d'étude utilisateur) — étiqueté tel quel.

## Résultats (`qoe_results.csv`, `qoe_sensitivity.csv`)
QoE (poids nominaux) : heuristic 0,727 ; maddpg 0,568 ; single 0,569 ;
random 0,556 ; fixed 0,51–0,52. **0,968 non reproduit, retiré** (aucune QoE > 0,74
observée ; le plafond mesuré vient de Dq/Dtx, pas du codage).
Sensibilité w1∈[0,4 ; 0,8] : le CLASSEMENT est stable (heuristic toujours premier ;
écarts ~±0,2) ; au-delà de w1=0,7 l'écrêtage à 1,0 mord (documenté dans le CSV).
Poids non optimisés par grid-search ici (limite : pas de validation d'un triplet
« optimal » ; triplet du manuscrit repris par défaut, sans allégation d'optimalité).
