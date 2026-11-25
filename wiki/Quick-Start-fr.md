[[English|Quick-Start]]

# Démarrage rapide

Cette page vous mène jusqu'à une première compilation. Les compilations tournent sur les runners hébergés par GitHub et durent environ 30 à 60 minutes.

## Prérequis

Il vous faut :

- Un compte GitHub. Un compte d'organisation convient aussi.
- Un serveur RustDesk en service : son nom d'hôte et sa clé publique (le contenu de `id_ed25519.pub`). Voir [[Serveur|Server-Setup-fr]].
- Une icône PNG carrée, de préférence en 1024x1024.
- Pour la méthode par script uniquement : `git` et la CLI GitHub `gh`, authentifiée (`gh auth login`).

Un dépôt d'instance ne contient aucun secret. L'adresse du serveur et la clé publique se lisent dans n'importe quel client distribué. Un dépôt public dispose gratuitement des runners hébergés par GitHub. Un dépôt privé consomme des minutes Actions, et les runners macOS comptent dix fois.

## Méthode A : le script

Clonez le générateur, puis lancez le script avec le nom du dépôt à créer.

```sh
git clone https://github.com/sadjo/rustdesk-client
cd rustdesk-client
scripts/new-instance.sh example-org/remote-support --private
```

Sans `--private`, le dépôt créé est public.

Le script demande :

| Question | Exemple |
| --- | --- |
| Nom de l'application | `Remote Support` |
| Société | `Example Org` |
| Identifiant de bundle | `org.example.remotesupport` |
| Hôte du serveur | `rustdesk.example.com` |
| Clé publique du serveur | contenu de `id_ed25519.pub` |
| URL de l'API (facultatif) | `https://rustdesk.example.com` |

Il crée ensuite le dépôt GitHub à partir de `template/` et affiche les étapes suivantes.

## Méthode B : à la main

Copiez le modèle dans un nouveau dépôt.

```sh
git clone https://github.com/sadjo/rustdesk-client
mkdir remote-support
cp -R rustdesk-client/template/. remote-support/
cd remote-support
git init -b main
```

Le `/.` final compte : il copie aussi `.github/` et `.gitignore`.

Modifiez `client.env` :

```ini
APP_NAME=Remote Support
COMPANY=Example Org
BUNDLE_ID=org.example.remotesupport
SERVER_HOST=rustdesk.example.com
SERVER_KEY=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
API_URL=
WEBSITE_URL=
SOURCE_URL=https://github.com/example-org/remote-support
ACCENT_COLOR=
```

Puis validez et poussez :

```sh
git add -A
git commit -m "Initial configuration"
gh repo create example-org/remote-support --private --source . --push
```

## Ensuite, dans les deux cas

1. Remplacez `branding/icon.png` par votre icône. Voir [[Identité visuelle|Branding-fr]].
2. Relisez `custom.json`. Le modèle produit un client en réception seule : on peut en prendre le contrôle, mais il ne peut pas se connecter à d'autres postes. Voir [[Référence de configuration|Configuration-Reference-fr]].
3. Renseignez `SOURCE_URL` dans `client.env` avec l'adresse où le code source de votre client est publié. Voir [[Licence et AGPL|License-and-AGPL-fr]].
4. Validez et poussez.

## Première compilation

Dans votre dépôt d'instance, sur GitHub : **Actions > Build client > Run workflow**.

Ou depuis un terminal :

```sh
gh workflow run "Build client" -f targets=windows
```

Compiler une seule plateforme va plus vite quand il s'agit seulement de vérifier la configuration. Une fois l'exécution terminée, téléchargez les binaires dans la section **Artifacts** de la page de l'exécution.

## Première version publiée

Poussez un tag qui commence par `v` :

```sh
git tag v1.0.0
git push origin v1.0.0
```

Le workflow compile toutes les plateformes et publie une release GitHub avec les binaires, `SHA256SUMS` et l'archive des sources. Voir [[Compilation et publication|Building-and-Releasing-fr]].

## Vérifier le client

1. Lancez le client sur un poste de test. Il affiche votre nom et votre icône.
2. La ligne d'état en bas de la fenêtre indique que le client est prêt. Sinon, voir [[Dépannage|Troubleshooting-fr]].
3. Connectez-vous à son ID depuis un client RustDesk standard configuré sur le même serveur.
4. Si vous avez renseigné `API_URL`, vérifiez que le poste apparaît dans votre console.
