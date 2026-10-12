# FINAL_VALIDATION_REPORT.md — verdict scientifique global

## 1. Commentaires reviewers résolus ?
17/19 RÉSOLUS (ER1–ER11, ER13–ER15, ER17–ER19) par correction + preuve exécutée.
2 PARTIELS : ER12 (IQR à n=3, indicatifs) ; ER16 (t-SNE non reproduit — MANQUANT
assumé, non fabriqué). Détail : `manuscript/response_to_reviewers.md`,
`reports/08_REVIEWER_RESPONSE_STATUS.csv`.

## 2. Expériences effectivement exécutées
- Audit : 1200 compteurs distants + 12 PLY mesurés (Jalon 1/A).
- Compression : AE entraîné (loss 4,9e-4) + balayage 5 α × 12 frames × 4 méthodes = 192 lignes mesurées.
- Radio/MADDPG : 6 méthodes × 100/60 ép. × 50 pas × 3 graines (720 + 1080 épisodes), 24 tests logiciels OK.
- Robustesse : 28 conditions (méthodes figées). QoE : définition corrigée + sensibilité 5×3 poids.

## 3. Valeurs du manuscrit qui ont changé (pourquoi)
Toutes les valeurs phares ONT changé car les anciennes sont mathématiquement
réfutées (70 s vs 3,5 ms ; QoE ∉ [0,1] ; Doppler) ou non rejouables (code perdu) :
voir `manuscript/old_vs_new_values.csv` (27 lignes). Rien n'a été ajusté pour
retrouver les chiffres publiés.

## 4. Affirmations retirées faute de preuve
0,968 ; +18,6–22,8 % ; −97,2 % ; 10,35 ms ; α=0,05 appris ; 67,8 dB ; 17,5 Gbits
utiles ; 734/20 mJ ; R²=0,94/α*=0,10 ; t-SNE structuré ; synergie multi-agent ;
% issus de [7]/[9]/[11]/[22].

## 5. Limites subsistantes
Échelle pilote (Ns=2048, n=3/seq, 3 graines) ; payload pleine-frame estimé par
règle de trois ; Rayleigh i.i.d. sans blockage/mobilité ; Denc non extrapolé ;
poids QoE non optimisés ; t-SNE manquant ; pas de GPU/torch.

## 6. Statuts d'acceptation
| Critère | Statut |
|---|---|
| Reviewers recensés + preuves | VALIDE (17) / PARTIEL (2) |
| Stats dataset cohérentes | VALIDE |
| Split documenté sans fuite | VALIDE (temporel + holdout soldier) |
| Flux compressé mesurable | VALIDE (float16 + en-tête mesurés) |
| MADDPG exécuté et traçable | PARTIELLEMENT VALIDÉ (converge, ne bat pas l'heuristique) |
| QoE vérifiable | VALIDE (définition corrigée + tests) |
| Latence/énergie cohérentes | VALIDE (identités testées) |
| Baselines attribuées | VALIDE (6 méthodes, code unique) |
| Figures = CSV | VALIDE (traçabilité complète) |
| Manuscrit traçable | PARTIELLEMENT VALIDÉ (sections clés, pas l'article entier) |
| Tests essentiels | VALIDE (24/24) |
| Limites explicites | VALIDE |
| Réponse sans affirmation non vérifiée | VALIDE |

## 7. L'article est-il prêt à resoumettre ?
**NON — encore des expériences requises** : GPU + 1200 frames pour split 70/15/15
réel, entraînement Transformer complet, t-SNE manquant, testbed radio.
Le présent livrable est une **reconstruction partielle, transparente et
reproductible** — valable comme base de resoumission après ces compléments,
pas comme article fini.
