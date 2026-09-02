#!/bin/sh
# Rend toutes les figures PlantUML en SVG (memoire) et PNG (presentation).
# Usage : sh rendre.sh [chemin/vers/plantuml.jar]
JAR="${1:-plantuml.jar}"
if [ ! -f "$JAR" ]; then
  echo "Introuvable : $JAR"
  echo "Usage : sh rendre.sh /c/outils/plantuml/plantuml.jar"
  exit 1
fi
mkdir -p rendu/svg rendu/png
java -jar "$JAR" -charset UTF-8 -DPLANTUML_LIMIT_SIZE=16384 -tsvg -o "$(pwd)/rendu/svg" ./*.puml
java -jar "$JAR" -charset UTF-8 -DPLANTUML_LIMIT_SIZE=16384 -tpng -o "$(pwd)/rendu/png" ./*.puml
echo "Figures rendues dans rendu/svg et rendu/png"
