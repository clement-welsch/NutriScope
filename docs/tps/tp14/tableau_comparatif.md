# TP14 - Tableau comparatif des mod�les

> Canevas pr�par� le 26 novembre 2026. Remplacer � � RENSEIGNER � par des mesures produites par le notebook ; ne pas recopier les rep�res de l'�nonc�.

## Conditions de comparaison

| �l�ment | Valeur retenue |
| --- | --- |
| Parquet / version / empreinte | � RENSEIGNER |
| Nombre de lignes | � RENSEIGNER |
| Split | Split du TP13, conserv� tel quel |
| Validation crois�e | Stratifi�e, 5 plis, shuffle=True, random_state=42, m�mes indices |
| Features candidates | 7 nutriments obligatoires, variables optionnelles et cat�gories pr�vues par le sujet |
| Colonnes exclues | nutriscore_score, code, product_name, brands, split et la cible |
| Pr�traitement | Imputation, indicateurs de manque, standardisation et one-hot avec regroupement rare, appris dans le pipeline |

## R�sultats CV sur le train

Consigner les moyennes et �carts-types r�ellement calcul�s. Les temps doivent provenir de l'ex�cution du notebook.

| Mod�le | F1 macro (moy. � �cart-type) | Accuracy | Balanced accuracy | Fit moyen (s) | Pr�diction moyenne (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Dummy - classe majoritaire | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER |
| Dummy - stratifi� | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER |
| Arbre - profondeur 3 | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER |
| Arbre - profondeur 8 | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER |
| R�gression logistique | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER |
| For�t al�atoire | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER |
| Mod�le �quilibr� (si retenu) | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER |

## Test final - apr�s le choix du mod�le

| Mod�le retenu | F1 macro | Accuracy | Balanced accuracy | �cart CV/test en F1 macro |
| --- | ---: | ---: | ---: | ---: |
| � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER | � RENSEIGNER |

**Matrice de confusion normalis�e par ligne :** � RENSEIGNER (chaque ligne somme � 1).

**Classes difficiles et direction des confusions :** � RENSEIGNER.

## Analyse � r�diger apr�s les mesures

- Rapport accuracy / F1 macro de la baseline majoritaire et explication : � RENSEIGNER.
- D�s�quilibre des classes et effet de class_weight balanced : � RENSEIGNER.
- Fuite reproduite avec nutriscore_score : F1 macro et importance par permutation : � RENSEIGNER.
- Contr�le anti-fuite et contr�le n�gatif : � RENSEIGNER.
- Importances du mod�le honn�te, coh�rence avec les composantes officielles et proxies : � RENSEIGNER.
- Trois erreurs r�elles de natures diff�rentes : produit, nutriments, diagnostic et action : � RENSEIGNER.
- Phrase de synth�se � reporter dans docs/journal.md : � RENSEIGNER.

## R�f�rences

- �nonc� : [tp-14-predire-le-nutriscore.md](tp-14-predire-le-nutriscore.md).
- Notebook : [notebooks/ml_nutriscore.ipynb](../../../notebooks/ml_nutriscore.ipynb).
- Donn�es Open Food Facts contributors, licence ODbL 1.0.

