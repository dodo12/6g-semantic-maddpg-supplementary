# 03 — Compression sémantique : résultats mesurés (Phase C)

## Protocole exécuté
Sous-échantillon Ns=2048 (seed 42), split Phase B (train 6 / val 3 / test 3 frames).
AE MLP 6→64→16→64→6 (relu — GELU indisponible sous sklearn, écart documenté),
entraîné sur 12 288 points TRAIN : loss finale 4,9e-4 (22 itérations).
MHA numpy 1 couche/4 têtes/d=64 à poids FIXES (seed 42) pour le scoring.
Balayage α ∈ {0,02 ; 0,05 ; 0,1 ; 0,2 ; 0,5} × 12 frames × 3 méthodes
(`proposed` = sélection attention + AE ; `attn-select` = sélection + exact ;
`uniform` = aléatoire + exact) + `raw`. Flux = float16 + en-tête JSON **mesuré**.

## Résultats (moyennes sur 12 frames ; `compression_metrics.csv`)

| α cible | proposed α_mes / PSNR | attn-select α_mes / PSNR | uniform α_mes / PSNR |
|---|---|---|---|
| 0,02 | 0,028 / 47,4 dB | 0,011 / 83,9 dB | 0,011 / 82,2 dB |
| 0,05 | 0,068 / 47,9 dB | 0,026 / 83,6 dB | 0,026 / 82,0 dB |
| 0,10 | 0,135 / 48,1 dB | 0,051 / 83,3 dB | 0,051 / 82,1 dB |
| 0,50 | 0,668 / 48,4 dB | 0,251 / 82,6 dB | 0,251 / 82,0 dB |

Test final (soldier, α=0,05) : attn-select 82,66 dB ; uniform 81,85 dB ; proposed 47,52 dB.
Encodage : ~0,2–0,8 ms (sélection) ; +~1–4 ms (AE). Décodage AE ~1–2 ms (non nul).

## Conclusions honnêtes (réponses ER5/ER7/ER16 par remplacement)
1. **Le goulot AE 16-dims dégrade** : 82 → 48 dB. Le « proposed » ne bat PAS la
   baseline triviale. Résultat négatif publié tel quel.
2. **Le scoring attention n'apporte rien à cette échelle** : attn-select ≈ uniform
   (+0,4 à +5,7 dB selon séquence, non significatif à n=12). Pas de seuil α*=0,10 :
   la courbe taux-distorsion est PLATE (83,9→82,6 dB) — l'analyse de seuil du
   manuscrit (Fig.4, R²=0,94) est **non reproduite et retirée**.
3. D1-PSNR 67,8 dB à α=0,05 (manuscrit) : **non vérifié, retiré** (nos échelles et
   code diffèrent ; aucune comparaison directe n'est licite).
4. La charge transmise du couplage E2E utilise la courbe `attn-select`
   (meilleure représentante mesurée) ; le flux AE n'est pas utilisé comme payload.
