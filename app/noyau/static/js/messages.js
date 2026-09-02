"use strict";

/* Fermeture manuelle (croix) et disparition automatique du bloc de
 * messages (noyau/ossature/messages.html) — aucun des deux n'était câblé
 * dans la charte, voir docs/suivi/CHARTE-INTEGRATION.md.
 *
 * Transition posée en JS (pas en classes Tailwind) : ce fichier n'est pas
 * scanné par la compilation Tailwind, une classe qui n'existe que dans une
 * chaîne JS ne serait jamais générée.
 */
(function () {
  var DELAI_DISPARITION_MS = 6000;
  var DUREE_TRANSITION_MS = 200; // durée « notif » de tailwind.config.js

  function fermer(message) {
    message.style.transition = "opacity " + DUREE_TRANSITION_MS + "ms ease-out";
    message.style.opacity = "0";
    window.setTimeout(function () {
      message.remove();
    }, DUREE_TRANSITION_MS);
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-message]").forEach(function (message) {
      var minuteur = window.setTimeout(function () {
        fermer(message);
      }, DELAI_DISPARITION_MS);

      var bouton = message.querySelector("[data-fermeture-message]");
      if (bouton) {
        bouton.addEventListener("click", function () {
          window.clearTimeout(minuteur);
          fermer(message);
        });
      }
    });
  });
})();
