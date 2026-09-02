"""Contrôle d'accès silencieux — RG-02, RG-02 bis.

La version qui lève et journalise (`verifier_habilitation`, couche
services) vit dans `administration` : journaliser exige `ServiceJournal`,
et `noyau` ne dépend d'aucune application — voir docs/suivi/DECISIONS.md,
D-09. Cette fonction-ci reste ici parce qu'elle ne journalise rien : le
processeur de contexte du noyau lui-même en a besoin pour filtrer la
navigation, sans créer de dépendance vers `administration`.
"""


def a_permission(utilisateur, permission: str) -> bool:
    """Silencieuse — pour les gabarits et la navigation, jamais pour un
    contrôle qui doit refuser une opération. `permission` suit la syntaxe
    native de Django : `"app_label.codename"` (le catalogue vit dans
    `noyau.Habilitation`, donc `"noyau.<domaine>_lecture"` ou `"_ecriture"`).
    """
    return utilisateur.is_authenticated and utilisateur.has_perm(permission)
