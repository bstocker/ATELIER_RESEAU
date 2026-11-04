#!/bin/sh
set -eu

# Docker nomme les interfaces eth0/eth1 dans un ordre imprévisible.
# On les renomme "lan" et "wan" pour que les commandes des exercices
# soient toujours les mêmes, quelle que soit la machine.
rename_if() {
    subnet="$1"; new_name="$2"
    cur=$(ip -o -4 addr show | awk -v s="$subnet" 'index($4, s) == 1 {print $2; exit}')
    if [ -n "$cur" ] && [ "$cur" != "$new_name" ]; then
        ip link set "$cur" down
        ip link set "$cur" name "$new_name"
        ip link set "$new_name" up
    fi
}
rename_if "172.20.0." wan
rename_if "172.20.1." lan

echo "============================================================"
echo " Routeur NAT démarré"
echo "   Interface WAN (côté Internet) : wan  -> 172.20.0.254"
echo "   Interface LAN (côté réseau local) : lan  -> 172.20.1.254"
echo "============================================================"

# Le routage IP est activé par docker-compose (sysctls) ; on l'affiche.
echo "ip_forward = $(cat /proc/sys/net/ipv4/ip_forward)"

# Remise à zéro des règles
iptables -F
iptables -t nat -F
iptables -t mangle -F

# PAT (NAT overload) : tout ce qui sort côté WAN prend l'IP du routeur
iptables -t nat -A POSTROUTING -o wan -j MASQUERADE

# Transfert autorisé sans filtrage (pour le lab uniquement, PAS en production)
iptables -P FORWARD ACCEPT

echo
echo "Règles NAT actives :"
iptables -t nat -L -n -v --line-numbers
echo
echo "Routeur prêt. Astuce : 'conntrack -L' affiche la table de traduction NAT."
exec tail -f /dev/null
