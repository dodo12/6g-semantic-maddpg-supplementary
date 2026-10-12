# 02 — Audit dataset 8iVFB v2 (Phase A)

## Provenance / licence (vérifiées le 2026-10-11, HTTP 200)
- Page : https://plenodb.jpeg.org/pc/8ilabs ; archive `8iVFBv2.7z` : 5 943 803 179 o.
- 4 ZIP (HEAD 200, `Accept-Ranges: bytes`, Range 206 vérifié) : longdress 1 635 191 404,
  loot 1 201 242 833, redandblack 1 241 096 174, soldier 1 748 391 289 o.
- Licence 8i : recherche non commerciale, redistribution interdite, citation
  d'Eon et al., ISO/IEC WG11M40059/WG1M74006, 2017. `Counts.txt` : 1 ligne
  `<points> <fichier>` par frame, format vérifié sur les 4 fichiers.
- Inventaire distant (EOCD + central directory) : **609 entrées/ZIP dont 300 PLY**,
  300 PNG, `Counts.txt`, licence/citation. 7z non inspectable partiellement.

## Statistiques complètes — métadonnées fournisseur (1200 frames, `results/counts_full.csv`)

| Séquence | Frames | n | Min | Q1 | Médiane | Q3 | Max | Moyenne | Écart-type |
|---|---|---|---|---|---|---|---|---|---|
| longdress | 1051–1350 | 300 | 733 580 | 808 075 | 835 104 | 858 669 | 916 250 | 834 315.3 | 37 083.4 |
| loot | 1000–1299 | 300 | 770 822 | 782 886 | 789 877 | 804 382 | 835 458 | 793 821.3 | 13 361.8 |
| redandblack | 1450–1749 | 300 | 640 070 | 698 617 | 732 487 | 757 395 | 816 879 | 727 070.8 | 39 850.4 |
| soldier | 536–835 | 300 | 1 044 513 | 1 061 120 | 1 083 210 | 1 089 853 | 1 103 974 | 1 075 299.0 | 16 493.9 |

IDs consécutifs sans lacune ni doublon (300/300 par séquence) ; 30 fps × 10 s plausibles,
numérotation arbitraire (ne commence PAS à 0 — ne jamais supposer un départ à zéro).
**Contradiction confirmée** : manuscrit « 735 k–1,1 M » / Table IV « 724 k min »
vs redandblack min **640 070** et longdress min 733 580. Correction Table IV (old_vs_new_values.csv) :
loot 785 k → 793 821 ; soldier 1,1 M → 1 075 299 ; longdress 757 k → 834 315 ; redandblack 724 k → 727 071 (moyenne).

## Mesures directes PLY (12 échantillons Range, `C:\8ivfb_audit\data`, `original/dataset_manifest.csv`)
PLY ascii 1.0, `x,y,z:float + red,green,blue:uchar`, en-têtes `element vertex N` =
lignes de données (12/12), 0 valeur non finie, boîtes englobantes 0–1023 conformes
voxels 10 bits. `Counts.txt` = en-tête PLY sur les 12/12 (ex. loot f1000 : 784 142).

## Limites
- 1200 statistiques = métadonnées fournisseur (pas de mesure point par point) ;
  mesure directe limitée à 12 frames (contrainte 5,9 Go). Toute statistique publiée
  ultérieurement provient de `counts_full.csv` ou des 12 PLY mesurés — traçabilité totale.
