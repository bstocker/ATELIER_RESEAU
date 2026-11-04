# Exercice 1 — Adresses IP, adresses MAC et ping

**Niveau :** ⭐ · **Durée :** ~45 min
**📖 Fiche théorique à lire avant :** `https://<votre-site>.pythonanywhere.com/bases`

## 🎯 Objectifs

- Lire l'adresse IP, le masque et l'adresse MAC d'une machine.
- Comprendre le rôle de la **passerelle** (le routeur).
- Voir **ARP** remplir la table des voisins.
- Tester la connectivité avec `ping` et `traceroute`.

> 📍 Tout cet exercice se fait dans le **terminal du client** 💻.
> 🖥️ Si besoin : `cd /workspaces/*/lab && docker compose up -d && docker exec -it lab_client bash`

---

## Partie A — Qui suis-je ?

### Étape 1 — Mes adresses

💻 Affichez vos interfaces réseau :

```bash
ip addr
```

👀 Repérez l'interface **`eth0`**. Sur la ligne `link/ether` se trouve l'**adresse MAC** ;
sur la ligne `inet` se trouvent l'**adresse IP** et le **masque** (après le `/`).

> 💡 L'interface `lo` (*loopback*, `127.0.0.1`) est une interface virtuelle qui permet à la
> machine de se parler à elle-même. On l'ignore dans cet exercice.

**Question A.1.** Complétez le tableau pour le client :

| Information        | Valeur pour le client |
| ------------------ | --------------------- |
| Nom de l'interface | …                     |
| Adresse MAC        | …                     |
| Adresse IP         | …                     |
| Masque (notation `/`) | …                  |
| Adresse du réseau  | …                     |

**Question A.2.** Le masque est `/24`. Combien de machines différentes peut-on placer dans ce réseau ?
(Indice : le dernier nombre de l'adresse peut varier de 0 à 255, mais 2 valeurs sont réservées.)

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

### Étape 2 — Ma passerelle

💻 Affichez la table de routage :

```bash
ip route
```

👀 Deux lignes apparaissent :

- `172.20.1.0/24 dev eth0 …` → « pour joindre mon réseau local, j'envoie directement sur `eth0` » ;
- `default via 172.20.1.254 …` → « pour **tout le reste**, je passe par `172.20.1.254` ».

**Question A.3.** Quelle est l'adresse de la passerelle du client ? À quelle machine du lab correspond-elle ?

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

---

## Partie B — Mes voisins (ARP)

### Étape 3 — Table ARP vide

💻 Videz puis affichez la table ARP (la liste des voisins dont le client connaît la MAC) :

```bash
ip neigh flush all
ip neigh
```

👀 La table est vide (ou ne contient que des lignes `FAILED`).

### Étape 4 — Un ping fait apparaître un voisin

💻 Envoyez 3 pings au serveur DHCP, qui est sur le **même réseau** que vous :

```bash
ping -c 3 172.20.1.2
```

👀 Vous devez voir 3 lignes `64 bytes from 172.20.1.2: icmp_seq=… ttl=64 time=… ms`
puis `0% packet loss`.

💻 Affichez à nouveau la table ARP :

```bash
ip neigh
```

**Question B.1.** Quelle nouvelle ligne est apparue ? Que contient-elle ? Pourquoi le client a-t-il
eu besoin de cette information **avant** de pouvoir envoyer le ping ?

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

### Étape 5 — Joindre une machine d'un autre réseau

💻 Videz la table ARP, puis faites un ping vers le site web `internet`, qui est sur un **autre réseau** :

```bash
ip neigh flush all
ping -c 3 172.20.0.10
ip neigh
```

**Question B.2.** Cette fois, le client n'a **pas** appris la MAC de `172.20.0.10`. De quelle IP
a-t-il appris la MAC ? Expliquez pourquoi, en vous aidant de la fiche théorique.

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

---

## Partie C — Le chemin vers Internet

### Étape 6 — Comparer les TTL

💻 Faites un ping vers le routeur, puis vers le site web, et regardez la valeur `ttl=` :

```bash
ping -c 2 172.20.1.254
ping -c 2 172.20.0.10
```

**Question C.1.** Notez le TTL des réponses dans les deux cas. Sont-ils identiques ? Que signifie
cette différence ? (Indice : chaque routeur traversé diminue le TTL de 1.)

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

### Étape 7 — traceroute

💻 Affichez la liste des routeurs traversés pour atteindre le site web :

```bash
traceroute -n 172.20.0.10
```

👀 Chaque ligne numérotée est un **saut** (*hop*).

**Question C.2.** Combien de sauts y a-t-il ? Quelle est l'adresse du premier saut ?
Dessinez (en texte) le chemin suivi : `client → … → internet`.

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

### Étape 8 — Le lab est isolé

💻 Essayez de joindre un vrai serveur d'Internet (le DNS de Google) :

```bash
ping -c 2 -W 2 8.8.8.8
```

**Question C.3.** Que se passe-t-il ? Pourquoi, selon vous ? (Pensez à ce qu'il y a derrière le routeur du lab.)

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

---

## Partie D — Synthèse

**Question D.1.** Complétez avec vos propres mots :

| Notion        | Explication en une phrase |
| ------------- | ------------------------- |
| Adresse IP    | …                         |
| Adresse MAC   | …                         |
| Passerelle    | …                         |
| ARP           | …                         |
| TTL           | …                         |

**Question D.2.** Vrai ou faux ? Justifiez : « Pour envoyer un paquet à `172.20.0.10`, le client met
dans la trame la MAC de `172.20.0.10`. »

> 💬 **Votre réponse :**
>
> _Remplacez ce texte par votre réponse._

---

## ✅ Ce qu'il faut retenir

- `ip addr` → mes adresses ; `ip route` → ma passerelle ; `ip neigh` → mes voisins (ARP).
- Sur le **même réseau**, on parle directement à la machine (on demande sa MAC avec ARP).
- Vers un **autre réseau**, on confie le paquet à la **passerelle** : la MAC utilisée est celle du routeur.
- Le **TTL** diminue de 1 à chaque routeur traversé.

## 🆘 En cas de problème

| Problème | Solution |
| -------- | -------- |
| `ping: connect: Network is unreachable` | Le client n'a plus d'IP ou de route. 🖥️ `docker compose restart client` |
| `ip neigh flush all` affiche une erreur | Sans gravité, continuez |
| `traceroute` affiche des `* * *` | Attendez la fin, ou ajoutez `-w 1` pour accélérer |
