# Exercice 2 — Le modèle OSI dans une vraie capture

**Niveau :** ⭐⭐ · **Durée :** ~1 h
**📖 Fiche théorique à lire avant :** `https://<votre-site>.pythonanywhere.com/osi`

## 🎯 Objectifs

- **Capturer** (enregistrer) les paquets d'une vraie visite de page web.
- Retrouver dans ces paquets les **couches du modèle OSI** et leurs en-têtes.
- Observer la « poignée de main » TCP qui précède chaque échange HTTP.

> 🖥️ Préparation : lab démarré (`docker compose up -d` dans le dossier `lab`).
> Ouvrez **deux terminaux client** 💻 (voir exercice 0, étape 4) et gardez un terminal Codespace 🖥️.

---

## Partie A — Capturer une visite web

### Étape 1 — Préparer la capture

💻 **Terminal client n°1** — supprimez une éventuelle ancienne capture :

```bash
rm -f /tmp/http.pcap
```

### Étape 2 — Lancer l'enregistrement

💻 **Terminal client n°1** — lancez `tcpdump`, le « magnétophone » du réseau :

```bash
tcpdump -i eth0 -U -nn -c 20 -w /tmp/http.pcap host 172.20.0.10
```

Ce que veut dire chaque morceau :

| Morceau | Signification |
| ------- | ------------- |
| `-i eth0` | écouter sur l'interface `eth0` |
| `-c 20` | s'arrêter tout seul après 20 paquets |
| `-w /tmp/http.pcap` | enregistrer dans ce fichier (au lieu d'afficher) |
| `host 172.20.0.10` | ne garder que les paquets échangés avec le site web |
| `-U -nn` | écrire immédiatement, ne pas traduire les adresses en noms |

👀 `tcpdump` affiche `listening on eth0…` puis **attend**. C'est normal : il enregistre.

### Étape 3 — Visiter le site web

💻 **Terminal client n°2** — pendant que tcpdump tourne, demandez deux pages :

```bash
curl http://172.20.0.10/
curl http://172.20.0.10/whoami
```

👀 Dans le terminal n°1, tcpdump s'arrête et affiche `20 packets captured`.
S'il attend encore, relancez une fois `curl http://172.20.0.10/`.

### Étape 4 — Lister les paquets capturés

🖥️ **Terminal Codespace** (à la racine du dépôt — tapez `cd ..` si vous êtes dans `lab`) :

```bash
./lab/exercises/osi_inspect.py
```

👀 Une ligne par paquet. Exemple :

```
 1  172.20.1.50 → 172.20.0.10  TCP 74 52790 → 80 [SYN] ...
 2  172.20.0.10 → 172.20.1.50  TCP 74 80 → 52790 [SYN, ACK] ...
 3  172.20.1.50 → 172.20.0.10  TCP 66 52790 → 80 [ACK] ...
 4  172.20.1.50 → 172.20.0.10  HTTP 141 GET / HTTP/1.1
 ...
 8  172.20.0.10 → 172.20.1.50  HTTP 948 HTTP/1.1 200 OK  (text/html)
```

**Question A.1.** Les 3 premiers paquets ne contiennent pas encore de HTTP. Ils portent les
indicateurs `[SYN]`, `[SYN, ACK]`, `[ACK]`. Comment s'appelle cet échange, et à quoi sert-il ?

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

**Question A.2.** Repérez le numéro du paquet contenant la **requête** `GET /` et celui contenant
la **réponse** `200 OK`. Qui envoie chacun d'eux (IP source) ?

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

---

## Partie B — Éplucher un paquet couche par couche

### Étape 5 — Détailler la requête HTTP

🖥️ Affichez le détail du paquet de la requête (remplacez `4` par le numéro trouvé en A.2) :

```bash
./lab/exercises/osi_inspect.py 4
```

👀 Le script affiche un tableau **par couche OSI** (L2, L3, L4, L7), avec pour chaque champ sa
**valeur** dans votre capture et une **explication**.

**Question B.1.** Complétez le tableau avec les valeurs de **votre** capture :

| Couche OSI         | Protocole | Champ observé       | Valeur dans ma capture |
| ------------------ | --------- | ------------------- | ---------------------- |
| 7 — Application    | HTTP      | Méthode et chemin   | …                      |
| 4 — Transport      | TCP       | Port source         | …                      |
| 4 — Transport      | TCP       | Port destination    | …                      |
| 3 — Réseau         | IPv4      | IP source           | …                      |
| 3 — Réseau         | IPv4      | IP destination      | …                      |
| 3 — Réseau         | IPv4      | TTL                 | …                      |
| 2 — Liaison        | Ethernet  | MAC source          | …                      |
| 2 — Liaison        | Ethernet  | MAC destination     | …                      |
| 1 — Physique       | —         | (non visible)       | —                      |

**Question B.2.** Le port destination est `80`. Que désigne-t-il ? Le port source est un grand
nombre (ex. `52790`) : qui l'a choisi, et pourquoi n'est-il pas toujours le même ?

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

**Question B.3.** La **MAC destination** est-elle celle du site web `internet` ? À quelle machine
appartient-elle ? (Comparez avec `ip neigh` dans le terminal client, et repensez à l'exercice 1.)

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

### Étape 6 — Comparer avec un paquet sans HTTP

🖥️ Affichez le premier paquet (le `SYN`) :

```bash
./lab/exercises/osi_inspect.py 1
```

**Question B.4.** Recopiez la ligne `Pile présente : …` des paquets 1 et 4. Quelle couche manque
dans le paquet 1 ? Pourquoi ?

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

### Étape 7 — Regarder la réponse du serveur

🖥️ Affichez le paquet contenant `200 OK` (remplacez `8` par votre numéro) :

```bash
./lab/exercises/osi_inspect.py 8
```

**Question B.5.** Quel est le `Content-Type` de la réponse ? Que contient la ligne
`Payload HTTP (extrait)` ? Dans quelle couche OSI ranger le `Content-Type` (le **format** des
données) ? Aidez-vous de la fiche théorique.

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

---

## Partie C — Encapsulation

**Question C.1.** En vous aidant du *Vocabulaire* de la fiche OSI, expliquez avec vos mots ce
qu'est l'**encapsulation**, en prenant l'exemple de la requête `GET /` que vous avez capturée.
Complétez le schéma :

```
[ Ethernet | IP | ……… | ……… ]
   L2       L3    L4    L7
```

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

**Question C.2.** Associez chaque nom de PDU à sa couche : **trame**, **paquet**, **segment**, **bit**.

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

---

## 🚀 Pour aller plus loin (facultatif)

**Question P.1.** Où l'adresse IP du client est-elle remplacée ? Capturez **côté WAN du routeur** :

🔀 Terminal routeur (`docker exec -it lab_nat_router bash`) :

```bash
tcpdump -i wan -nn -c 6 host 172.20.0.10
```

💻 Terminal client : `curl http://172.20.0.10/whoami`

Quelle IP source voyez-vous côté WAN ? Comparez avec votre capture côté client.

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

**Question P.2.** Sur votre propre ordinateur, ouvrez un site en `https://`. En quoi la capture
serait-elle différente ? Quelles informations ne pourrait-on plus lire ?

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

---

## ✅ Ce qu'il faut retenir

- `tcpdump` enregistre les paquets ; `osi_inspect.py` les décompose couche par couche.
- Avant tout échange HTTP, TCP ouvre la connexion avec 3 paquets : **SYN, SYN-ACK, ACK**.
- Chaque couche ajoute son **en-tête** : MAC (L2), IP (L3), ports (L4), requête HTTP (L7).
- La MAC de destination est celle du **prochain saut**, l'IP de destination est celle de la **cible finale**.

## 🆘 En cas de problème

| Problème | Solution |
| -------- | -------- |
| `tcpdump: /tmp/http.pcap: Permission denied` | 💻 `rm -f /tmp/http.pcap` puis relancez tcpdump |
| tcpdump n'atteint jamais 20 paquets | Relancez `curl` dans le terminal n°2, ou faites <kbd>Ctrl</kbd>+<kbd>C</kbd> |
| `osi_inspect.py` : `No such file or directory` | Vous n'êtes pas à la racine du dépôt. 🖥️ `cd /workspaces/*/` |
| `osi_inspect.py` : `Erreur tshark` | La capture est vide ou absente : recommencez l'étape 1 |
