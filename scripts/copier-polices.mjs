#!/usr/bin/env node
/**
 * Copie les polices depuis les paquets @fontsource vers app/noyau/static/polices/,
 * en renommant selon docs/charte, § 1.9. Rejouable à chaque mise à jour de version
 * (`npm update @fontsource/... && node scripts/copier-polices.mjs`).
 *
 * Sous-ensemble latin, style normal uniquement — aucune autre variante n'est
 * référencée par static/css/polices.css.
 */
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..");
const DESTINATION = join(RACINE, "app", "noyau", "static", "polices");

const POLICES = [
  { paquet: "barlow", graisses: [400, 500, 600, 700], prefixe: "barlow" },
  { paquet: "ibm-plex-sans", graisses: [400, 500, 600], prefixe: "plex-sans" },
  { paquet: "ibm-plex-mono", graisses: [400, 500], prefixe: "plex-mono" },
];

mkdirSync(DESTINATION, { recursive: true });

let copies = 0;

for (const { paquet, graisses, prefixe } of POLICES) {
  const dossierPaquet = join(RACINE, "node_modules", "@fontsource", paquet);

  for (const graisse of graisses) {
    const source = join(dossierPaquet, "files", `${paquet}-latin-${graisse}-normal.woff2`);
    const cible = join(DESTINATION, `${prefixe}-${graisse}.woff2`);
    if (!existsSync(source)) {
      throw new Error(`Fichier attendu introuvable : ${source}`);
    }
    copyFileSync(source, cible);
    copies += 1;
    console.log(`${cible.replace(RACINE, ".")}`);
  }

  const licenceSource = join(dossierPaquet, "LICENSE");
  const licenceCible = join(DESTINATION, `LICENCE-${paquet}.txt`);
  copyFileSync(licenceSource, licenceCible);
  console.log(`${licenceCible.replace(RACINE, ".")}`);
}

console.log(`\n${copies} fichiers .woff2 et ${POLICES.length} licences copiés dans app/noyau/static/polices/.`);
