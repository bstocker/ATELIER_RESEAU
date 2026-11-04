#!/usr/bin/env bash
# Exécuté UNE fois, à la création du Codespace.
set -euo pipefail

echo "==> Installation des dépendances Python"
pip install --quiet -r requirements.txt

echo "==> Attente du démarrage de Docker"
for _ in $(seq 1 60); do
    docker info >/dev/null 2>&1 && break
    sleep 2
done

echo "==> Construction des images du lab (environ 3 minutes)"
cd lab
docker compose --profile bonus build

echo
echo "✅ Codespace prêt ! Commencez par lab/exercises/00_prise_en_main.md"
