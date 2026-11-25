[[English|Configuration-Reference]]

# Référence de configuration

Une instance se configure avec deux fichiers placés à sa racine :

| Fichier | Rôle |
| --- | --- |
| `client.env` | Identité du client et adresse du serveur. |
| `custom.json` | Réglages RustDesk compilés dans le client. |

Les deux sont lus par `scripts/apply.py` au moment de la compilation. Aucun ne contient de secret : tout leur contenu se lit dans le client distribué.

## client.env

### Format

- Une ligne `CLÉ=VALEUR` par réglage. Le fichier est analysé, jamais exécuté.
- Les lignes vides et celles qui commencent par `#` sont ignorées.
- Une valeur peut être entourée de guillemets simples ou doubles. Ils sont retirés.
- Un commentaire en fin de ligne n'est pas géré : il ferait partie de la valeur.
- Une clé inconnue arrête la compilation.

### Clés

| Clé | Obligatoire | Règles | Exemple |
| --- | --- | --- | --- |
| `APP_NAME` | oui | 1 à 40 caractères parmi lettres, chiffres, espace, point, tiret et tiret bas. Commence par une lettre ou un chiffre. Ne finit pas par une espace. Ne doit pas valoir `RustDesk`, quelle que soit la casse. | `Remote Support` |
| `COMPANY` | oui | 1 à 80 caractères parmi lettres, chiffres, espace, point, virgule, `&`, tiret et tiret bas. Commence par une lettre ou un chiffre. | `Example Org` |
| `BUNDLE_ID` | oui | Identifiant en DNS inversé d'au moins trois éléments. Chaque élément commence par une lettre et contient des lettres, des chiffres et des tirets. | `org.example.remotesupport` |
| `SERVER_HOST` | oui | Nom d'hôte ou adresse IP de votre serveur `hbbs`. Ajoutez `:port` seulement si le port n'est pas 21116. | `rustdesk.example.com` |
| `SERVER_KEY` | oui | Clé publique du serveur : le contenu de `id_ed25519.pub`. 44 caractères base64 qui décodent 32 octets. | `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=` |
| `API_URL` | non | URL `http://` ou `https://` du serveur d'API ou de la console web. À laisser vide si vous n'exploitez que `hbbs` et `hbbr`. | `https://rustdesk.example.com` |
| `WEBSITE_URL` | non | URL `http://` ou `https://` ouverte par le lien vers le site dans la page À propos. | `https://www.example.com` |
| `SOURCE_URL` | non, recommandé | URL `http://` ou `https://` où le code source de votre client est publié. Affichée dans la page À propos. | `https://github.com/example-org/remote-support` |
| `ACCENT_COLOR` | non | Couleur d'accent de l'interface, au format `#RRGGBB`. | `#1A2B3C` |

Les lettres acceptées sont les lettres ASCII, sans accent.

### Effet de chaque clé

| Clé | Effet |
| --- | --- |
| `APP_NAME` | Nom affiché à l'utilisateur, nom de l'exécutable Windows et propriétés du fichier, nom du bundle macOS, nom de l'entrée de menu Linux. Sa forme en minuscules avec tirets (`remote-support`) préfixe le nom des fichiers produits. |
| `COMPANY` | Éditeur dans les propriétés du fichier Windows et dans le MSI. Cité dans la mention de la page À propos. |
| `BUNDLE_ID` | Identifiant de l'application macOS. |
| `SERVER_HOST`, `SERVER_KEY` | Imposés comme `custom-rendezvous-server` et `key` dans `override-settings`. Ils remplacent aussi le serveur et la clé par défaut intégrés à RustDesk. |
| `API_URL` | Si renseignée : imposée comme `api-server` dans `override-settings`, et remplace l'adresse d'API par défaut intégrée. |
| `WEBSITE_URL` | Si renseignée : cible du lien vers le site dans la page À propos. |
| `SOURCE_URL` | Si renseignée : ajoutée à la page À propos sous la forme `Source code: <url>`. |
| `ACCENT_COLOR` | Si renseignée : remplace la couleur d'accent de l'interface RustDesk. |

La page À propos indique toujours : `Built by <COMPANY>. Modified version of RustDesk (AGPL-3.0).` La mention de copyright d'origine est conservée.

### Exemple

```ini
# Nom affiché à l'utilisateur.
APP_NAME=Remote Support

# Éditeur.
COMPANY=Example Org

# Identifiant macOS.
BUNDLE_ID=org.example.remotesupport

# Serveur et sa clé publique.
SERVER_HOST=rustdesk.example.com
SERVER_KEY=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=

# Facultatif.
API_URL=https://rustdesk.example.com
WEBSITE_URL=https://www.example.com
SOURCE_URL=https://github.com/example-org/remote-support
ACCENT_COLOR=#1A2B3C
```

## custom.json

RustDesk lit normalement les réglages d'un client personnalisé dans un fichier `custom.txt` signé avec une clé détenue par RustDesk. Ce générateur compile les réglages dans le binaire à la place. Aucun fichier posé à côté de l'exécutable ne peut les modifier.

### Structure

```json
{
  "conn-type": "incoming",
  "override-settings": {
    "hide-powered-by-me": "Y",
    "allow-auto-update": "N",
    "verification-method": "use-both-passwords"
  },
  "default-settings": {}
}
```

| Section | Signification |
| --- | --- |
| `override-settings` | Réglages imposés au client. L'utilisateur ne peut pas les modifier. |
| `default-settings` | Valeurs initiales. L'utilisateur peut les modifier. |
| Toute autre clé de premier niveau | Un réglage figé, valable pour tout le client. |
| `app-name` | Écrit par la compilation à partir de `APP_NAME`. Une valeur saisie ici est remplacée. |

### Règles vérifiées à la compilation

- Le fichier doit contenir un objet JSON.
- `override-settings` et `default-settings` doivent être des objets. Une section absente est considérée comme vide.
- Toute valeur de ces deux sections doit être une chaîne : écrivez `"Y"`, pas `true`.
- Les clés de premier niveau `password` et `salt` sont refusées. Le binaire est public : un mot de passe prédéfini serait lisible par quiconque détient le client.
- `custom-rendezvous-server`, `key` et `api-server` dans `override-settings` sont toujours écrasés par `client.env`.

Le fichier est facultatif. Sans lui, le client ne reçoit que les réglages serveur de `client.env`.

### Réglages figés (premier niveau)

| Clé | Valeur | Effet |
| --- | --- | --- |
| `conn-type` | `"incoming"` | Connexions entrantes uniquement. On peut prendre le contrôle du client, mais il ne peut pas se connecter à d'autres postes. |
| `disable-settings` | `"Y"` | L'utilisateur ne peut pas ouvrir les paramètres. |
| `disable-installation` | `"Y"` | Le client ne peut pas être installé. Il ne sert qu'en session ponctuelle. |
| `disable-ab` | `"Y"` | Pas de carnet d'adresses. |
| `disable-account` | `"Y"` | Pas de connexion à un compte. |
| `disable-tcp-listen` | `"Y"` | Le client n'écoute pas les connexions TCP directes. |

### Réglages pour `override-settings` ou `default-settings`

| Clé | Valeurs | Effet |
| --- | --- | --- |
| `approve-mode` | `password`, `click`, ou vide | Mode d'acceptation d'une session entrante : par mot de passe, par un clic de l'utilisateur, ou l'un ou l'autre si la valeur est vide. |
| `verification-method` | `use-temporary-password`, `use-permanent-password`, `use-both-passwords` | Mots de passe acceptés. |
| `hide-powered-by-me` | `Y` | Présent dans le modèle. Masque la mention « Powered by RustDesk ». |
| `allow-auto-update` | `N` | Présent dans le modèle. Les mises à jour automatiques restent désactivées. |

`apply.py` vérifie la structure du fichier, pas le nom des réglages. Un nom mal orthographié est compilé tel quel, et le client l'ignore sans rien dire. Contrôlez le résultat sur un poste de test.

La recherche de mises à jour auprès de RustDesk est déjà désactivée pour les clients personnalisés : RustDesk le fait de lui-même dès que le nom de l'application n'est pas `RustDesk`.

### Exemples

Assistance en présence de l'utilisateur uniquement. Il accepte chaque session d'un clic, et le client ne peut pas être installé :

```json
{
  "conn-type": "incoming",
  "disable-installation": "Y",
  "override-settings": {
    "approve-mode": "click"
  },
  "default-settings": {}
}
```

Accès sans surveillance, avec un mot de passe permanent que chaque utilisateur définit après l'installation :

```json
{
  "conn-type": "incoming",
  "override-settings": {
    "approve-mode": "password",
    "verification-method": "use-permanent-password"
  },
  "default-settings": {}
}
```

### Ce qui est compilé

Avec l'exemple de `client.env` ci-dessus et le `custom.json` du modèle, la compilation embarque :

```json
{
  "app-name": "Remote Support",
  "conn-type": "incoming",
  "default-settings": {},
  "override-settings": {
    "allow-auto-update": "N",
    "api-server": "https://rustdesk.example.com",
    "custom-rendezvous-server": "rustdesk.example.com",
    "hide-powered-by-me": "Y",
    "key": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
    "verification-method": "use-both-passwords"
  }
}
```

## Vérifier une configuration en local

Vous pouvez valider une instance sans attendre une compilation complète. Il faut Python 3 avec Pillow, et `git`.

```sh
git clone --branch 1.5.3 --recurse-submodules https://github.com/rustdesk/rustdesk
git clone https://github.com/rbsinfo/rustdesk-client
python3 -m pip install pillow
python3 rustdesk-client/scripts/apply.py --instance chemin/vers/instance --source rustdesk --check
```

`--check` vérifie que tout s'applique et n'écrit rien.
