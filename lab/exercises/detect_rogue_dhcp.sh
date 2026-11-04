#!/usr/bin/env bash
# Détecteur de faux serveur DHCP (exercice 5 bonus).
#
# À lancer DEPUIS LE TERMINAL CODESPACE, à la racine du dépôt :
#     docker exec -i lab_client bash < lab/exercises/detect_rogue_dhcp.sh
# Le script s'exécute alors sur le poste client. Ctrl+C pour l'arrêter.

# Adresse du SEUL serveur DHCP autorisé sur notre réseau
SERVEUR_AUTORISE="172.20.1.2"

echo "Surveillance des offres DHCP sur eth0 (Ctrl+C pour arrêter)..."

# tshark écoute le réseau et n'affiche, pour chaque OFFER (type DHCP = 2),
# que l'adresse du serveur qui l'a envoyée (option 54).
tshark -i eth0 -l -Y "dhcp.option.dhcp == 2" -T fields -e dhcp.option.dhcp_server_id 2>/dev/null |
while read -r serveur; do
    if [ "$serveur" = "$SERVEUR_AUTORISE" ]; then
        echo "OK     : offre du serveur autorisé $serveur"
    else
        echo "ALERTE : serveur DHCP NON autorisé détecté : $serveur"
    fi
done
