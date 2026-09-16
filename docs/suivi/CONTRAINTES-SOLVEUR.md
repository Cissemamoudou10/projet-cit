# Les six contraintes dures, sous forme exploitable par un modèle CP-SAT

US-PLAN-04, Prompt 30 § 7. Rendu pour le prototype CP-SAT (jalon C2, 26 septembre,
réévaluation de R6) — ce que `ServiceContraintes` applique en Python, un solveur
devra le modéliser à l'identique, faute de quoi il optimiserait un problème
différent de celui que le système contrôle réellement.

Vocabulaire commun : une **candidate** est un tuple (brigade, élément de
référentiel, instructeur, début, fin, lieu éventuel) — voir
`planification.services.contraintes.Candidate`. Le solveur manipule des
**intervalles optionnels** (`NewOptionalIntervalVar`) : une candidate non
retenue par le solveur a son booléen de présence à faux, sans quoi RG-34/RG-37
ne peuvent pas s'exprimer (une candidate absente du programme ne doit
contraindre personne).

## RG-34 — unicité d'affectation de l'instructeur

- **Variables** : un intervalle optionnel par candidate `(début, fin, présent)`,
  et un booléen de présence par candidate.
- **Forme** : `AddNoOverlap` sur l'ensemble des intervalles dont l'instructeur
  est le même — mais **UN SEUL INTERVALLE PAR SÉANCE**, jamais un par ligne de
  programme : les candidates qui partagent la même séance (regroupement,
  `cle_regroupement` non nul) doivent être fusionnées en un seul intervalle
  avant modélisation, sans quoi le solveur les traiterait comme deux
  occupations concurrentes de l'instructeur et refuserait à tort tout
  regroupement.
- **Portée** : centre entier — toutes les candidates de la semaine, toutes
  sessions et brigades confondues, jamais un sous-ensemble filtré par session.

## RG-35 — qualification

- **Variables** : le domaine de la variable « instructeur affecté » à une
  candidate portant la matière M.
- **Forme** : restriction de domaine, pas une contrainte au sens CP-SAT — la
  variable ne prend jamais une valeur hors de l'ensemble des instructeurs
  qualifiés pour M (`Qualification.objects.filter(matiere=M)`), construit une
  fois par matière avant résolution.
- **Portée** : par candidate, indépendante des autres.

## RG-36 — disponibilité de l'instructeur

- **Variables** : les mêmes intervalles optionnels que RG-34, plus un
  intervalle FIXE (toujours présent, jamais optionnel) par indisponibilité
  déclarée de cet instructeur sur l'horizon considéré.
- **Forme** : `AddNoOverlap` entre les intervalles de séances de l'instructeur
  et ses intervalles d'indisponibilité — un cas particulier de RG-34 où l'un
  des deux intervalles n'est jamais optionnel.
- **Portée** : par instructeur, sur l'horizon de résolution.

## RG-37 — lieu (trois sous-cas, trois formes différentes)

- **Salle attitrée** : AUCUNE variable de solveur — un préfiltre, hors modèle.
  La capacité contre l'effectif réel se vérifie une fois, avant résolution ;
  une brigade dont la salle est insuffisante n'a simplement aucune candidate
  valide à proposer au solveur pour cette matière.
- **Lieu partagé, mode SÉQUENTIEL** : `AddNoOverlap` sur les intervalles
  optionnels des candidates utilisant ce lieu — exactement RG-34, la ressource
  contrainte étant le lieu plutôt que l'instructeur. Un regroupement explicite
  ne lève pas la contrainte ici (E7) : fusionner les candidates regroupées en
  un seul intervalle, comme pour RG-34, est la seule façon d'admettre un
  regroupement sur un lieu séquentiel.
- **Lieu partagé, mode SIMULTANÉ** : `AddCumulative(intervalles, demandes,
  capacité)` — chaque candidate demande une quantité de ressource égale à
  l'effectif réel de sa brigade, la capacité du lieu borne la somme des
  demandes actives à tout instant. C'est la forme qui diffère le plus d'une
  simple exclusion mutuelle : plusieurs candidates non regroupées peuvent
  coexister tant que la somme tient dans la capacité.
- **Capacité ou mode de partage non renseignés** : traités comme le préfiltre
  de la salle attitrée — aucune candidate valide n'est produite pour ce lieu
  tant que la donnée manque (§ 4, directive utilisateur : refus, jamais une
  autorisation implicite).
- **Portée** : par lieu, sur l'horizon de résolution.

## RG-38 — créneau ouvert

- **Variables** : le domaine temporel (heure de début admissible) d'une
  candidate pour une brigade donnée.
- **Forme** : restriction de domaine — tout créneau recoupant une période
  bloquante dont la portée couvre la brigade (centre entier, sa session, ou
  elle-même) est retiré du domaine avant résolution, jamais modélisé comme une
  contrainte d'exclusion entre deux intervalles.
- **Portée** : par brigade, sur l'horizon de résolution — le calcul de portée
  (RG-30) doit être résolu une fois par période bloquante, pas par candidate.

## RG-39 — volume et prérequis

- **Volet volume (a)** : contrainte linéaire bornée —
  `somme(durée(candidate) pour candidate d'un élément E, retenues par le
  solveur) + volume déjà programmé(E) <= volume_prescrit(E)`. Un terme
  constant (le volume déjà programmé, calculé hors modèle) s'ajoute à une
  somme de variables (les candidates retenues).
- **Volet prérequis (b)** : contrainte de précédence — aucune candidate de
  l'élément E, pour la brigade B, n'est retenue avant que la somme des durées
  des candidates de l'élément prérequis pour B (déjà programmées, terme
  constant) atteigne le volume prescrit du prérequis. Modélisable comme une
  contrainte de précédence classique (`AddNoOverlap` temporel entre la fin du
  bloc prérequis et le début du bloc suivant) uniquement si le prérequis est
  entièrement programmé AVANT résolution ; sinon, c'est une contrainte
  logique (`AddImplication`) entre le booléen de présence de la candidate et
  le fait que le seuil soit atteint — cas encore ouvert pour le prototype, à
  trancher quand US-PLAN-03 posera la génération elle-même.
- **Portée** : (a) par élément de référentiel, toutes brigades confondues ;
  (b) par couple (élément prérequis, brigade).
