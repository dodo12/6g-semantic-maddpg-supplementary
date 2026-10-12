# Journal des modifications (change_log.md)

## Scientifiques
1. Résumé : toutes les valeurs historiques remplacées par mesures de reconstruction (QoE max 0,727 heuristic ; MADDPG 0,568).
2. B_total : 1 Gbps → 1 GHz (ER8).
3. S_frame 17,5 Gbits + Dtx 3,5 ms + −97,2 % : RETIRÉS (70 s démontrés, ER8).
4. QoE : formule corrigée + clip (bornes [0,1] prouvées fausses avant).
5. Table IV points/frame : valeurs d'audit (longdress 757 k → 834 315 ; redandblack + note min 640 070).
6. Doppler : 0,78 kHz → 259 Hz @10 km/h (ER19).
7. Baselines : taxonomie réécrite, 6 méthodes exécutées (ER2) ; Single-DRL redéfini (acteur partagé).
8. Stats : Wilcoxon/Bonferroni/CIs historiques retirés (données perdues) ; n=3 descriptif (ER4).
9. Figures 2–11 historiques : TOUTES remplacées par FIG-D/C/M/E/Q/G issues des CSV.
10. Citations : [12] officialisée ; [20] découplée de 8iVFB ; % de [7]/[9]/[11]/[22] retirés (ER17/18).
11. Énergie : équation E=P·T ajoutée Sec III ; 734,4/20,58 mJ retirés (ER15).
12. t-SNE/perceptual-threshold/α*=0,10 : descriptions réécrites sur données mesurées (ER7/ER16).

## Rédactionnelles
- Note « RECONSTRUCTION EXPERIMENTALE » ajoutée ; aucune page/section revendiquée sans preuve.
- Anciennes valeurs conservées ci-dessous (old_vs_new_values.csv), jamais écrasées silencieusement.
