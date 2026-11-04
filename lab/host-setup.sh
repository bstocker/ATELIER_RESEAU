#!/usr/bin/env bash
# Pré-requis "hôte" du lab (lancé automatiquement au démarrage du Codespace).
#
# Pourquoi : Docker active br_netfilter, qui fait passer les trames des
# bridges par le pare-feu (iptables) de la machine hôte. Sa politique
# FORWARD DROP bloquerait alors le trafic entre nos deux réseaux lan et wan.
# En désactivant ce hook, c'est bien le conteneur nat-router qui route et
# fait le NAT — c'est exactement ce que l'on veut observer.
#
# Modification non persistante : à relancer après un redémarrage.
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    exec sudo -E "$0" "$@"
fi

KEY=net.bridge.bridge-nf-call-iptables
if ! sysctl -n "$KEY" >/dev/null 2>&1; then
    echo "[host-setup] $KEY absent (br_netfilter non chargé) : rien à faire."
    exit 0
fi

echo "[host-setup] Désactivation du hook br_netfilter IPv4 (valeur actuelle : $(sysctl -n $KEY))"
sysctl -w "$KEY=0" > /dev/null
echo "[host-setup] OK. Le lab peut router via nat-router."
