"""Statut d'un écart de volume horaire — RG-61, factorisé entre US-PLAN-07
(prompt 47) et US-SUI-02 (prompt 48, Temps 0, D-279 fermée).

**Une seule fonction de statut** (Temps 0, point 1 du prompt 48) : elle
reçoit une RÉFÉRENCE et une MESURE, jamais « le prescrit » et « le
programmé » nommément — PLAN-07 lui passe `(prescrit, programmé)`, US-SUI-02
lui passe `(prescrit, réalisé)` une fois la session terminée, ou
`(programmé échu, réalisé)` en cours de session (A2, le réalisé ne peut
jamais dépasser le programmé échu par construction — les séances réalisées
en sont un sous-ensemble — le dépassement n'y est donc jamais atteignable,
exactement ce que RG-61/A2 attendent).

`reference_echue` ne signifie PAS littéralement « la session est terminée » :
elle signifie que la RÉFÉRENCE passée est déjà entièrement constituée, donc
la comparaison est équitable. Pour PLAN-07 (référence = tout le prescrit de
la session), ce n'est vrai qu'une fois la session terminée (D-278). Pour
US-SUI-02, la référence choisie par l'appelant (programmé échu, ou prescrit
après la fin de session) l'est toujours par construction : l'appelant y
passe donc toujours `True`, et ne produit jamais le statut `en_cours` — un
test d'architecture interdit un second calcul de ce statut ailleurs.
"""

CONFORME = "conforme"
EN_COURS = "en_cours"
RETARD = "retard"
DEPASSEMENT = "depassement"


def statut_volume(reference, mesure, reference_echue, seuil):
    """E3/RG-61 : sur-mesure (« dépassement ») dès que le seuil est franchi
    au-dessus de la référence ; sous-mesure (« retard ») seulement si la
    référence est déjà échue — sinon `en_cours`, jamais un écart."""
    ecart_pourcent = abs(reference - mesure) / reference * 100 if reference else 0.0
    if mesure > reference:
        return (DEPASSEMENT if ecart_pourcent > seuil else CONFORME), ecart_pourcent
    if ecart_pourcent <= seuil:
        return CONFORME, ecart_pourcent
    return (RETARD if reference_echue else EN_COURS), ecart_pourcent
