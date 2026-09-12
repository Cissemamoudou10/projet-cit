"""État transitoire entre deux requêtes HTTP, jamais stocké côté serveur —
mécanisme générique, extrait après coup (US-SES-06, § 0.1, Prompt 25) : la
première version (US-SES-05, import de stagiaires) encodait directement des
octets de fichier dans un champ caché, taillée pour cet unique usage. La
proposition de répartition transporte une donnée structurée, pas un fichier :
le dénominateur commun aux deux est l'octet-flux, pas le format qu'il porte.
Chaque appelant sérialise son propre contenu en octets (le fichier tel quel
pour l'import, du JSON pour une proposition) avant de les confier ici.

`decoder` ne lève jamais : un champ cor rompu ou absent (onglet fermé puis
rouvert, champ trafiqué) doit produire une valeur absente à traiter par
l'appelant, jamais une exception technique remontée jusqu'à l'utilisateur.
"""

import base64
import binascii


def encoder(payload: bytes) -> str:
    return base64.b64encode(payload).decode("ascii")


def decoder(valeur: str) -> bytes | None:
    try:
        return base64.b64decode(valeur, validate=True)
    except (binascii.Error, ValueError):
        return None
