"""Forme unique d'une violation d'une contrainte dure — E1/H3, Prompt 30 :
code de la règle, message désignant l'élément en cause, et l'ORIGINE du
conflit (§ 12, directive utilisateur) — `"base"` face à une séance déjà en
base, `"lot"` face à une candidate antérieure du même lot déjà acceptée.
Les deux motifs appellent des actions différentes côté appelant (reporter
la candidate en conflit avec l'existant ; réordonner ou fusionner deux
candidates du même lot) : jamais fondus dans un seul message texte à
analyser, toujours ce champ structuré.
"""


def violation(code: str, message: str, origine: str = "base") -> dict:
    return {"code": code, "message": message, "origine": origine}
