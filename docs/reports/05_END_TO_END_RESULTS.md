# 05 — Bout-en-bout (Phase E)

## Chaîne exécutée
Frame pilote (Ns=2048) → scoring MHA + sélection → flux float16 **mesuré**
(`attn-select`), mis à l'échelle pleine-frame par règle de trois à α identique
(k=α·N, N=moyenne d'audit) → allocation radio simulée → Ttx=B/R → décodage →
D1-PSNR mesuré. En-têtes inclus (200 o) ; poids AE/acteurs supposés partagés
hors-ligne (side-info exclue — documenté).

## Décomposition de la latence (ms, moyenne 3 graines ; `latency_breakdown.csv`)

| Méthode | Denc | Dtx | Dq | Ddec | Total |
|---|---|---|---|---|---|
| heuristic | 0,24 | 271 | 9,6 | 0,35 | 281 |
| single | 0,50 | 1 371 | 602 | 0,35 | 1 974 |
| fixed05 | 0,79 | 1 390 | 1 150 | 0,35 | 2 541 |
| maddpg | 0,58 | 5 209 | 1 131 | 0,35 | 6 341 |
| fixed1 | 0,79 | 6 886 | 3 142 | 0,35 | 10 029 |

Dtx+Dq dominent (>> Denc+Ddec). Ttx=B/R vérifié par test (17,5 Gbit/250 Mbps =
70 s — ER8 ; à α=0,05, pleine frame loot ≈ 3,8 Mbit → ~15 ms à 250 Mbps,
cohérent avec nos Dtx hors fading).

## Énergie (`energy_breakdown.csv`, mJ)
Etx=P·Ttx domine (>98 %) ; Ecomp=65 W·Tenc < 2 %. P̄ mesurée : maddpg 0,88 W
(power-control appris) vs fixed 2,00 W — mais Ttx reste élevé : l'énergie suit
la latence. Le récit « puissance réduite » du manuscrit ne suffit pas sans
réduction de Ttx (réponse ER15 par remplacement : définition E=P·T ajoutée,
valeurs 734/20 mJ retirées).

## Limites
Denc à l'échelle Ns (extrapolation O(N²) non mesurée) ; fading Rayleigh i.i.d.
sans blockage ; mobilité nulle (Doppler 259 Hz vérifié analytiquement, ER19).
