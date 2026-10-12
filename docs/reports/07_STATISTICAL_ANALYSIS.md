# 07 — Statistiques et robustesse (Phase G)

## Protocole
n=3 graines (42/123/2026) ; moyennes des 10 derniers épisodes ; moyenne±écart-type,
médiane, IC-t 95 % INDICATIFS (`statistical_summary.csv`). Frames corrélées :
jamais utilisées comme répétitions indépendantes. Aucun test de supériorité
revendiqué (n=3 insuffisant pour Wilcoxon ; constat descriptif uniquement).

## Robustesse (`robustness_results.csv`, 28 conditions, méthodes figées, graine 42)
- Heuristic : QoE 0,68–0,79 sur TOUTES les conditions (B×4, λ×3, distance×0,7/1,3).
  Stable et premier partout.
- Effet distance dominant : ×0,7 → 0,785 ; ×1,3 → 0,68 (heuristic).
- B 0,5→2 GHz : 0,70 → 0,74 (modeste) ; λ 30→10 fps : 0,725 → 0,742 (modeste).
- fixed1/fixed05 restent à ~0,51–0,53 partout (congestion structurelle).
- Méthodes APPRISES exclues des balayages (poids non sauvegardés — limite
  assumée ; le réentraînement par condition dépassait le budget CPU).

## Limites d'inférence
IC normaux à bornes négatives sur latences (distribution asymétrique : lire
médiane/viol_rate plutôt que moyenne). Aucune affirmation « p < 0,001 » reprise.
