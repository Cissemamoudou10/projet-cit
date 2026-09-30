# Fichiers d'import de recette — US-SES-05

Générés par `charger_jeu_recette` (Prompt 34, § 3). Ne pas modifier à la main : relancer la commande régénère ce dossier à l'identique.

| Fichier | Contenu | Résultat attendu à l'import |
|---|---|---|
| `01-valide-10.csv` | 10 lignes valides (REC-001..010), séparateur « ; ». | |
| `02-valide-5.xlsx` | 5 lignes valides (REC-011..015), au format XLSX. | |
| `03-valide-45-colonnes-permutees.csv` | 45 lignes valides (REC-101..145), séparateur « , », colonnes dans un ordre permuté. | |
| `04-encodage-utf8-bom.csv` | 5 lignes accentuées (REC-401..405), encodage UTF-8 avec BOM. | |
| `05-encodage-cp1252.csv` | Mêmes identités que 04 (REC-401..405), encodage CP1252 — mêmes noms décodés attendus. | |
| `06-valide-colonnes-permutees.csv` | 5 lignes valides (REC-501..505), colonnes permutées autrement qu'en 03. | |
| `07-valide-entetes-majuscules.csv` | 5 lignes valides (REC-601..605), en-têtes tout en majuscules, sans accent. | |
| `08-colonne-matricule-absente.csv` | 5 lignes (REC-951..955) sans la colonne Matricule — refus global attendu. | |
| `09-matricule-manquant-ligne-12.csv` | 14 lignes (REC-701..714), matricule vidé sur la 12e ligne de données (ligne 13 avec l'en-tête). | |
| `10-doublon-dans-le-fichier.csv` | REC-201 répété deux fois + REC-202..205 — la seconde occurrence est en anomalie. | |
| `11-doublon-en-base.csv` | REC-001/REC-002 (déjà dans 01) + REC-801..803 — doublon en base UNIQUEMENT si 01 a déjà été importé dans la même session. | |
| `12-un-champ-vide-par-ligne.csv` | 5 lignes (REC-901..905), une colonne obligatoire différente vidée à chaque ligne. | |
| `13-faux-fichier.csv` | Un PDF renommé en .csv — refus de format attendu. | |

## Fichier 11 — recette en deux temps

`11-doublon-en-base.csv` ne produit un doublon en base (RG-18, détection bornée à la session) que si `01-valide-10.csv` a déjà été importé et confirmé dans la MÊME session. Séquence à suivre :

1. Importer et confirmer `01-valide-10.csv` dans une session.
2. Importer `11-doublon-en-base.csv` dans la MÊME session : `REC-001` et `REC-002` doivent apparaître en doublons en base, `REC-801` à `REC-803` en lignes valides.
