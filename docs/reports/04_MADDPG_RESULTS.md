# 04 — MADDPG : résultats mesurés (Phase D)

## Taxonomie figée (réponse ER2 — une définition partout)
- `maddpg` : 4 acteurs MLP 5→32→32→3 + critique centralisé, CTDE, bruit 0,3→0,01.
- `single` : MÊME code, acteur UNIQUE partagé (ablation mono-agent centralisée).
- `fixed1` : parts égales, P=Pmax, α=1 (type QoS-Only). `fixed05` : idem α=0,5 (type DL-Only).
- `random` : politique aléatoire admissible. `heuristic` : parts ∝ 1/d, P=1 W, α=0,05.
Écart documenté : pénalité κ=10 appliquée au dépassement RELATIF (forme brute du
manuscrit en ms écrase le gradient : récompenses ∈ [−8000, −200]).

## Conditions exécutées
100 épisodes × 50 pas (pilotes) puis 60 × 50 officiels, 3 graines (42/123/2026),
canal Rayleigh re-tiré par pas, file dynamique d'arriéré + EWMA (le M/D/1
stationnaire par pas est invalide sous fading non stationnaire — écart documenté).
Convergence : plateau dès ~ép. 10–20 (pas de divergence ni collapse).

## Résultats (moyenne 3 graines, 10 derniers épisodes ; `radio_metrics.csv`)

| Méthode | QoE | Lat moy (ms) | SE | Énergie (mJ) | Viol | α | P moy (W) |
|---|---|---|---|---|---|---|---|
| heuristic | **0,727** | 281 | 1,92 | 287 | 0,30 | 0,05 | 1,00 |
| maddpg | 0,568 | 6 341 | 1,71 | 2 852 | 0,89 | 0,23–0,31 | 0,88 |
| single | 0,569 | 1 974 | 1,99 | 1 877 | 0,87 | 0,08–0,44 | 1,27 |
| random | 0,556 | 3 437 | 2,31 | 1 961 | 0,95 | ~0,26 | 1,05 |
| fixed05 | 0,517 | 2 541 | 2,44 | 2 832 | 0,99 | 0,50 | 2,00 |
| fixed1 | 0,512 | 10 029 | 2,43 | 13 824 | 1,00 | 1,00 | 2,00 |

## Conclusions (réponses ER2/ER6/ER10 par remplacement)
1. Les agents apprennent (P < Pmax : 0,88 W ; α < 0,5) mais **ne battent pas
   l'heuristique** à ce budget (60 ép., CPU) : QoE 0,57 vs 0,73.
2. QoE 0,968 / latence 10,35 ms / −97,2 % du manuscrit : **non reproduits, retirés**.
   Le système honnête à λ=30 trames/s est congestionné sauf forte compression.
3. `single` (partagé) ≈ `maddpg` : aucun gain multi-agent démontré ici (échantillon
   trop petit pour conclure ; pas de revendication de synergie).
