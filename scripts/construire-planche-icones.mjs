#!/usr/bin/env node
/**
 * Construit app/noyau/static/icones/planche.svg à partir de lucide-static,
 * une <symbol> par identifiant — docs/charte, § 1.11. Rejouable à chaque
 * mise à jour de version (`npm update lucide-static && node scripts/construire-planche-icones.mjs`).
 *
 * Trait 1,5 px (la charte), quand lucide-static livre du 2 px : le
 * stroke-width est réécrit, pas hérité du fichier source.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..");
const DOSSIER_ICONES = join(RACINE, "node_modules", "lucide-static", "icons");
const DESTINATION = join(RACINE, "app", "noyau", "static", "icones", "planche.svg");

// Identifiant français -> nom Lucide. docs/charte, § 1.11 — 36 entrées, dont
// 8 marquées « ? » (nom proposé, pas encore tranché) : voir
// docs/suivi/CHARTE-INTEGRATION.md.
const ICONES = {
  calendrier: "calendar-days",
  horloge: "clock",
  "grille-horaire": "grid-3x3",
  salle: "door-closed",
  groupe: "users",
  instructeur: "presentation",
  stagiaire: "graduation-cap",
  matiere: "book-open",
  seance: "calendar-clock",
  document: "file-text",
  "proces-verbal": "file-signature",
  signature: "signature",
  validation: "check",
  rejet: "x",
  avertissement: "triangle-alert",
  information: "info",
  recherche: "search",
  filtre: "filter",
  tri: "arrow-up-down",
  "tri-croissant": "arrow-up",
  "tri-decroissant": "arrow-down",
  export: "download",
  impression: "printer",
  ajout: "plus",
  modification: "pencil",
  suppression: "trash-2",
  verrou: "lock",
  historique: "history",
  alerte: "bell",
  statistique: "bar-chart-3",
  "fleche-suite": "arrow-right",
  "chevron-bas": "chevron-down",
  "chevron-droite": "chevron-right",
  actions: "ellipsis-vertical",
  "document-valide": "file-check",
  avenant: "file-clock",
};

mkdirSync(dirname(DESTINATION), { recursive: true });

const symboles = [];
const manquants = [];

for (const [identifiant, nomLucide] of Object.entries(ICONES)) {
  const source = join(DOSSIER_ICONES, `${nomLucide}.svg`);
  if (!existsSync(source)) {
    manquants.push(`${identifiant} (${nomLucide})`);
    continue;
  }
  const brut = readFileSync(source, "utf-8");
  const interieur = brut.match(/<svg[^>]*>([\s\S]*?)<\/svg>/)[1].trim();
  symboles.push(
    `  <symbol id="${identifiant}" viewBox="0 0 24 24" fill="none" stroke="currentColor" ` +
      `stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">\n    ${interieur
        .split("\n")
        .map((ligne) => ligne.trim())
        .join("\n    ")}\n  </symbol>`,
  );
}

const planche =
  `<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">\n` +
  `${symboles.join("\n")}\n` +
  `</svg>\n`;

writeFileSync(DESTINATION, planche, "utf-8");

console.log(`${symboles.length} icônes écrites dans ${DESTINATION.replace(RACINE, ".")}`);
if (manquants.length) {
  console.log(`\nManquantes dans lucide-static installé :\n- ${manquants.join("\n- ")}`);
}
