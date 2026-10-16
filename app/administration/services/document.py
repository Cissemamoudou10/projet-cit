"""Production des documents officiels depuis les gabarits — RG-58, P5
(US-SUI-06, prompt 45). Service UNIQUE : toute story qui produit un PDF
(US-SUI-06 aujourd'hui, US-EVAL-07 demain) passe par `ServiceDocument.
produire`, jamais par un second appel direct à WeasyPrint.

Polices et mise en page paginée résolues par `django.contrib.staticfiles.
finders` — jamais une ressource réseau (BNF-06), et sans dépendre de
`collectstatic` (les apps de test n'en lancent pas).

**`weasyprint` s'importe à l'intérieur de `produire`, jamais en tête de
module.** WeasyPrint charge ses bibliothèques natives (GTK3/Pango/Cairo) dès
son propre `import`, pas seulement à l'usage — absentes sous Windows
(poste de développement), un import en tête de module ferait échouer
l'import de CE module, et donc de tout module qui en dépend (`ServiceSuivi`,
les vues), même pour un usage qui ne produit aucun PDF. Constaté réellement :
`from weasyprint import HTML` en tête faisait échouer la découverte de
TOUTES les vues du projet par les tests d'architecture (`_toutes_les_vues`
importe chaque module de vues), bien au-delà de ce service."""

from pathlib import Path

from django.contrib.staticfiles import finders
from django.template.loader import render_to_string

from administration.exceptions import ErreurGabaritIntrouvable
from administration.models import GabaritDocument

FICHIER_REPERE_STATIQUES = "css/polices.css"


def _base_url_statique() -> str:
    chemin = finders.find(FICHIER_REPERE_STATIQUES)
    if chemin is None:
        raise ErreurGabaritIntrouvable(
            f"Fichier statique repère introuvable : {FICHIER_REPERE_STATIQUES} — "
            "les polices et la mise en page PDF ne peuvent pas être résolues."
        )
    racine = Path(chemin).parent.parent
    return racine.as_uri() + "/"


class ServiceDocument:
    # Le gabarit (`GabaritDocument`) est administrable — § 11.2, catalogue des
    # domaines : « document » n'en fait pas partie, « administration » est le
    # domaine qui porte déjà ce qui est éditable par l'administrateur.
    DOMAINE = "administration"

    @staticmethod
    def produire(type_document, nom_gabarit_html: str, contexte: dict) -> bytes:
        """Rend `nom_gabarit_html` (un gabarit Django, jamais de texte en dur
        pour l'en-tête/les mentions/la signature) avec `contexte` complété du
        `GabaritDocument` du type demandé, puis produit le PDF. Aucune
        habilitation ici : chaque appelant (`ServiceSuivi`, plus tard
        `ServiceEvaluation`) vérifie la sienne avant d'appeler ce service."""
        try:
            gabarit = GabaritDocument.objects.get(type_document=type_document)
        except GabaritDocument.DoesNotExist as erreur:
            raise ErreurGabaritIntrouvable(
                f"Aucun gabarit chargé pour « {type_document} » — "
                "lancez `initialiser_gabarits_documents`."
            ) from erreur
        from weasyprint import HTML

        html = render_to_string(nom_gabarit_html, {**contexte, "gabarit": gabarit})
        return HTML(string=html, base_url=_base_url_statique()).write_pdf()
