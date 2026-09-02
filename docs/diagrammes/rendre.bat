@echo off
REM Rend toutes les figures PlantUML en SVG (memoire) et PNG (presentation).
REM Usage : rendre.bat [chemin\vers\plantuml.jar]
setlocal
set JAR=C:\outils\plantuml\plantuml.jar
if not "%~1"=="" set JAR=%~1
if not exist "%JAR%" (
  echo Introuvable : %JAR%
  echo Passez le chemin en argument : rendre.bat C:\chemin\plantuml.jar
  exit /b 1
)
if not exist rendu\svg mkdir rendu\svg
if not exist rendu\png mkdir rendu\png
java -jar "%JAR%" -charset UTF-8 -DPLANTUML_LIMIT_SIZE=16384 -tsvg -o "%CD%\rendu\svg" *.puml
java -jar "%JAR%" -charset UTF-8 -DPLANTUML_LIMIT_SIZE=16384 -tpng -o "%CD%\rendu\png" *.puml
echo Figures rendues dans rendu\svg et rendu\png
endlocal
