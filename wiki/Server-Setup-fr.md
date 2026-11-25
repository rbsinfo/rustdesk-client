[[English|Server-Setup]]

# Serveur

Cette page liste ce que le client attend de votre serveur. Elle ne remplace pas le guide d'installation du serveur que vous choisissez.

## Ce dont le client a besoin

| Besoin | Où le renseigner |
| --- | --- |
| Nom d'hôte du serveur d'ID (`hbbs`) | `SERVER_HOST` dans `client.env` |
| Clé publique du serveur (`id_ed25519.pub`) | `SERVER_KEY` dans `client.env` |
| Un serveur relais (`hbbr`) joignable par les clients | Rien à configurer dans l'instance. Faites tourner `hbbr` sur le même hôte, ou déclarez le relais au niveau de `hbbs`. |
| Facultatif : URL d'un serveur d'API ou d'une console web | `API_URL` dans `client.env` |

Ces valeurs sont compilées dans le client et l'utilisateur ne peut pas les modifier. Changer d'hôte ou de clé par la suite impose de recompiler et de redistribuer le client.

Pour `SERVER_HOST`, préférez un nom DNS à une adresse IP. Vous pourrez ainsi déplacer le serveur sans recompiler.

## Ports

Ouvrez ces ports depuis les clients vers le serveur :

| Port | Protocole | Service | Usage |
| --- | --- | --- | --- |
| 21115 | TCP | `hbbs` | Test du type de NAT |
| 21116 | TCP et UDP | `hbbs` | Enregistrement de l'ID, heartbeat, établissement des connexions |
| 21117 | TCP | `hbbr` | Relais |

Si `hbbs` écoute sur un autre port que 21116, ajoutez-le à l'hôte :

```ini
SERVER_HOST=rustdesk.example.com:31116
```

Le serveur d'API ou la console a sa propre adresse et son propre port. Indiquez l'URL complète dans `API_URL`.

## Clé publique

`hbbs` crée une paire de clés à son premier démarrage, dans son répertoire de travail :

| Fichier | Conservation |
| --- | --- |
| `id_ed25519` | Privée. Elle reste sur le serveur. Ne la placez jamais dans un dépôt. |
| `id_ed25519.pub` | Publique. Son contenu est la valeur de `SERVER_KEY`. |

```sh
cat id_ed25519.pub
```

La valeur fait 44 caractères base64 et se termine par `=`.

Sauvegardez les deux fichiers. Si le serveur perd sa paire de clés, tous les clients déjà distribués refusent la nouvelle clé : il faut recompiler et redistribuer.

## RustDesk Server OSS ou une console

| Serveur | Ce que vous obtenez | `API_URL` |
| --- | --- | --- |
| RustDesk Server OSS (`hbbs` + `hbbr`) | Des sessions à distance qui passent par votre serveur. Pas de liste des postes. | À laisser vide |
| RustDesk Server Pro, ou une console compatible comme CortenDesk | La même chose, plus une console web qui liste les postes | URL de l'API de la console |

Quand `API_URL` est renseignée, le client se déclare auprès de la console : il envoie des requêtes à `/api/sysinfo` et `/api/heartbeat`. Le poste apparaît avec :

- son ID,
- son nom d'hôte,
- le nom d'utilisateur,
- le système d'exploitation,
- la version du client.

Le client n'envoie pas le nom de l'application. Si plusieurs clients issus d'instances différentes se déclarent auprès de la même console, celle-ci ne peut pas les distinguer par leur nom. Regroupez les postes côté serveur.

## Côté technicien

Le modèle produit un client en réception seule : c'est celui qu'on installe sur les postes à dépanner. Pour prendre la main, le technicien utilise un client capable d'ouvrir des connexions sortantes et configuré avec le même serveur et la même clé. Deux possibilités :

- un client RustDesk standard, configuré à la main avec votre serveur et votre clé ;
- une seconde instance sans `"conn-type": "incoming"` dans `custom.json`.

## Liste de contrôle

1. `hbbs` et `hbbr` tournent, et les ports 21115 à 21117 sont joignables de l'extérieur.
2. `SERVER_HOST` est résolu depuis les réseaux de vos utilisateurs.
3. `SERVER_KEY` est le contenu exact de `id_ed25519.pub`.
4. Si vous utilisez une console, `API_URL` s'ouvre dans un navigateur depuis un poste utilisateur.
5. Un client de test affiche un état prêt et répond quand on appelle son ID.
