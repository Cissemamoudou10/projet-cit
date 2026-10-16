"""Commande d'administration : crée le gabarit de chaque `TypeDocument`
(RG-58, US-SUI-06, prompt 45, P5) — catalogue de RÉFÉRENCE, nécessaire dans
tout environnement, y compris en production sur le réseau isolé du CIT
(BNF-06). Même précédent que `initialiser_natures_evenement`/
`initialiser_habilitations`, jamais une migration de données (D-122).

Idempotente sans écraser un gabarit déjà modifié par l'administrateur :
seul un type absent de la table est créé.
"""

from django.core.management.base import BaseCommand

from administration.models import GabaritDocument, TypeDocument

GABARITS_INITIAUX = {
    TypeDocument.PROGRESSION_REALISEE: {
        "en_tete": "Centre d'instruction des transmissions — Direction de formation",
        "mentions": "Document calculé automatiquement par le système de gestion des activités de formation.",
        "bloc_signature": "Visa du directeur de formation :",
    },
    TypeDocument.PROCES_VERBAL: {
        "en_tete": "Centre d'instruction des transmissions — Direction de formation",
        "mentions": "Procès-verbal de résultats.",
        "bloc_signature": "Visa du directeur de formation :",
    },
}


class Command(BaseCommand):
    help = "Crée le gabarit de chaque type de document (en-tête, mentions, bloc de signature)."

    def handle(self, *args, **options):
        for type_document, valeurs in GABARITS_INITIAUX.items():
            _, cree = GabaritDocument.objects.get_or_create(
                type_document=type_document, defaults=valeurs
            )
            if cree:
                self.stdout.write(self.style.SUCCESS(f"Gabarit créé : {type_document.label}"))
            else:
                self.stdout.write(f"{type_document.label} : déjà présent, non modifié.")
