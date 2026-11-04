#!/usr/bin/env python3
"""
osi_inspect.py — visualisation d'une trame pcap décomposée par couche OSI.

Usage:
    ./osi_inspect.py                        # liste toutes les trames du pcap
    ./osi_inspect.py 4                      # détaille la trame n°4
    ./osi_inspect.py 4 --pcap /tmp/dhcp.pcap --container lab_dhcp_server

Le script délègue la lecture à tshark (dans le conteneur cible) et regroupe
les champs JSON par couche OSI pour produire un tableau pédagogique.
"""
import argparse
import json
import subprocess
import sys

PROTO_TO_LAYER = [
    ("eth",     "L2",  "Liaison — Ethernet"),
    ("arp",     "L2/3", "Liaison/Réseau — ARP"),
    ("ip",      "L3",  "Réseau — IPv4"),
    ("ipv6",    "L3",  "Réseau — IPv6"),
    ("icmp",    "L3",  "Réseau — ICMP"),
    ("udp",     "L4",  "Transport — UDP"),
    ("tcp",     "L4",  "Transport — TCP"),
    ("tls",     "L6",  "Présentation — TLS"),
    ("http",    "L7",  "Application — HTTP"),
    ("dns",     "L7",  "Application — DNS"),
    ("dhcp",    "L7",  "Application — DHCP"),
    ("bootp",   "L7",  "Application — DHCP/BOOTP"),
]

HIGHLIGHT = {
    "eth": [
        ("eth.src",  "MAC source",
         "Carte réseau émettrice sur le segment local"),
        ("eth.dst",  "MAC destination",
         "Prochain saut sur le LAN (souvent le routeur). ff:ff:ff:ff:ff:ff = broadcast"),
        ("eth.type", "EtherType",
         "Protocole L3 encapsulé : 0x0800=IPv4, 0x86DD=IPv6, 0x0806=ARP"),
    ],
    "arp": [
        ("arp.src.proto_ipv4", "IP source",
         "IP de celui qui demande ou répond"),
        ("arp.dst.proto_ipv4", "IP cible",
         "IP dont on cherche la MAC"),
        ("arp.opcode", "Opcode",
         "1 = request, 2 = reply"),
    ],
    "ip": [
        ("ip.src",   "IP source",
         "Adresse logique de l'émetteur (couche 3)"),
        ("ip.dst",   "IP destination",
         "Destinataire final — peut traverser plusieurs routeurs"),
        ("ip.ttl",   "TTL",
         "Time To Live, décrémenté à chaque saut. Évite les boucles infinies"),
        ("ip.proto", "Protocole encapsulé",
         "Indique ce qu'IP transporte : 6=TCP, 17=UDP, 1=ICMP"),
        ("ip.len",   "Longueur totale",
         "Taille en octets de l'en-tête IP + payload"),
    ],
    "tcp": [
        ("tcp.srcport",     "Port source",
         "Port éphémère choisi par le client (généralement > 1024)"),
        ("tcp.dstport",     "Port destination",
         "Port du service : 80=HTTP, 443=HTTPS, 22=SSH, 25=SMTP..."),
        ("tcp.flags.str",   "Flags",
         "Bits de contrôle : S=SYN, A=ACK, F=FIN, R=RST, P=PUSH"),
        ("tcp.seq",         "Numéro de séquence",
         "Position du 1er octet de payload dans le flux TCP"),
        ("tcp.ack",         "Numéro d'ACK",
         "Prochain octet attendu en retour (cumulatif)"),
        ("tcp.window_size", "Fenêtre",
         "Octets que je peux encore recevoir sans ACK (contrôle de flux)"),
    ],
    "udp": [
        ("udp.srcport", "Port source",
         "Port émetteur. Pas de connexion, pas de handshake en UDP"),
        ("udp.dstport", "Port destination",
         "Port du service UDP : 53=DNS, 67/68=DHCP, 123=NTP..."),
        ("udp.length", "Longueur",
         "Taille du datagramme UDP (en-tête + payload)"),
    ],
    "http": [
        ("http.request.method",   "Méthode",
         "Verbe HTTP : GET (lire), POST (envoyer), PUT, DELETE..."),
        ("http.request.uri",      "URI",
         "Chemin de la ressource demandée côté serveur"),
        ("http.request.version",  "Version",
         "Version du protocole HTTP utilisée"),
        ("http.host",             "Host",
         "Hôte ciblé — permet le virtual hosting (plusieurs sites par IP)"),
        ("http.user_agent",       "User-Agent",
         "Identifiant logiciel du client (navigateur, curl, bot...)"),
        ("http.response.code",    "Code réponse",
         "Statut : 2xx=OK, 3xx=redirection, 4xx=erreur client, 5xx=erreur serveur"),
        ("http.content_type",     "Content-Type",
         "Type MIME du corps : text/html, application/json, image/png..."),
        ("http.content_length",   "Content-Length",
         "Taille (octets) du corps de la réponse"),
    ],
    "dns": [
        ("dns.qry.name", "Question",
         "Nom de domaine demandé"),
        ("dns.qry.type", "Type",
         "Type d'enregistrement : 1=A, 28=AAAA, 5=CNAME, 15=MX..."),
        ("dns.a",        "Réponse A",
         "Adresse IPv4 correspondant au nom interrogé"),
    ],
    "dhcp": [
        ("dhcp.option.dhcp",                  "Type DHCP (opt 53)",
         "Étape DORA : 1=DISCOVER, 2=OFFER, 3=REQUEST, 5=ACK, 6=NAK, 7=RELEASE"),
        ("dhcp.id",                           "Transaction ID",
         "xid : numéro tiré au hasard par le client, identique dans les 4 messages"),
        ("dhcp.hw.mac_addr",                  "MAC du client",
         "Adresse MAC du client qui demande une configuration"),
        ("dhcp.ip.your",                      "IP attribuée",
         "Champ yiaddr : IP proposée/attribuée par le serveur (0.0.0.0 côté client)"),
        ("dhcp.option.dhcp_server_id",        "Serveur (opt 54)",
         "IP du serveur DHCP qui fait l'offre"),
        ("dhcp.option.subnet_mask",           "Masque (opt 1)",
         "Masque de sous-réseau du LAN"),
        ("dhcp.option.router",                "Passerelle (opt 3)",
         "IP du routeur par défaut à utiliser pour sortir du LAN"),
        ("dhcp.option.domain_name_server",    "DNS (opt 6)",
         "Serveur(s) DNS à utiliser"),
        ("dhcp.option.ip_address_lease_time", "Bail (opt 51)",
         "Durée de validité du bail, en secondes"),
    ],
    "bootp": [
        ("bootp.ip.client", "IP client",
         "IP que le client connaît déjà (0.0.0.0 au tout premier démarrage)"),
        ("bootp.ip.your",   "IP attribuée",
         "IP attribuée par le serveur (champ yiaddr)"),
        ("bootp.ip.server", "IP serveur",
         "IP du serveur DHCP qui répond"),
    ],
}

WIDTH = 132


def run_tshark(container, pcap, args):
    cmd = ["docker", "exec", container, "tshark", "-r", pcap] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        sys.exit("Erreur : 'docker' introuvable dans le PATH.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Erreur tshark : {e.stderr.strip() or e}")
    return result.stdout


def find_field(node, key):
    """Recherche récursive d'une clé dans la structure JSON de tshark."""
    if isinstance(node, dict):
        if key in node:
            v = node[key]
            return ", ".join(str(x) for x in v) if isinstance(v, list) else str(v)
        for v in node.values():
            r = find_field(v, key)
            if r is not None:
                return r
    elif isinstance(node, list):
        for v in node:
            r = find_field(v, key)
            if r is not None:
                return r
    return None


def list_frames(container, pcap):
    print(run_tshark(container, pcap, []), end="")


def show_frame(container, pcap, n):
    raw = run_tshark(container, pcap, ["-T", "json", "--no-duplicate-keys", "-Y", f"frame.number == {n}"])
    data = json.loads(raw)
    if not data:
        sys.exit(f"Trame {n} introuvable dans {pcap}.")

    layers = data[0]["_source"]["layers"]
    frame = layers.get("frame", {})

    print()
    print("=" * WIDTH)
    print(f"  Trame {n}  |  {frame.get('frame.len', '?')} octets  "
          f"|  {frame.get('frame.time', '?')}")
    protos_present = [p for p, _, _ in PROTO_TO_LAYER if p in layers]
    print(f"  Pile présente : {' > '.join(protos_present) or '(aucune)'}")
    print("=" * WIDTH)
    print(f"  {'OSI':<5} | {'Protocole':<24} | {'Champ':<18} = {'Valeur':<22} | Explication")
    print("-" * WIDTH)

    for proto_key, osi, label in PROTO_TO_LAYER:
        if proto_key not in layers:
            continue
        print(f"  {osi:<5} | {label:<24} |")
        for entry in HIGHLIGHT.get(proto_key, []):
            field_key, field_label, explanation = entry
            val = find_field(layers, field_key)
            if val is not None:
                if len(val) > 22:
                    val = val[:19] + "..."
                print(f"  {'':5} | {'':24} |   {field_label:<18} = {val:<22} | {explanation}")
        print("-" * WIDTH)

    if "http" in layers:
        body = find_field(layers, "http.file_data")
        if body:
            preview = " ".join(body.replace("\\n", " ").replace("\\r", " ").split())[:200]
            print(f"  Payload HTTP (extrait) : {preview}")
            print("-" * WIDTH)


def main():
    p = argparse.ArgumentParser(
        description="Visualisation par couche OSI d'une trame pcap (via tshark)."
    )
    p.add_argument("frame", nargs="?", type=int,
                   help="Numéro de trame à détailler (omettre pour lister)")
    p.add_argument("--pcap", default="/tmp/http.pcap",
                   help="Chemin du pcap DANS le conteneur (défaut: /tmp/http.pcap)")
    p.add_argument("--container", default="lab_client",
                   help="Conteneur Docker cible (défaut: lab_client)")
    args = p.parse_args()

    if args.frame is None:
        list_frames(args.container, args.pcap)
    else:
        show_frame(args.container, args.pcap, args.frame)


if __name__ == "__main__":
    main()
