[[English|Troubleshooting]]

# Dépannage

## Trouver l'erreur

1. Ouvrez l'exécution en échec dans l'onglet **Actions** de votre dépôt d'instance.
2. Ouvrez le premier job marqué en échec.
3. Les erreurs de configuration se trouvent dans l'étape **Apply the instance configuration**. Elles commencent par `error:`.

Ces erreurs se reproduisent sur votre poste en quelques minutes. Voir « Vérifier une configuration en local » dans la [[Référence de configuration|Configuration-Reference-fr]].

Les messages sont en anglais. Ils sont repris ici tels quels pour que vous puissiez les rechercher.

## Erreurs liées à client.env

| Message | Cause | Correction |
| --- | --- | --- |
| `missing configuration file: .../client.env` | Pas de `client.env` à la racine de l'instance, ou `instance-path` erroné. | Ajoutez le fichier, ou corrigez `instance-path`. |
| `client.env:12: expected KEY=VALUE, got: ...` | Une ligne n'est pas de la forme `CLÉ=VALEUR`. Les clés sont en majuscules. `export CLÉ=...` n'est pas accepté. | Corrigez la ligne. |
| `client.env:12: unknown key ...` | La clé ne fait pas partie des neuf clés connues. | Supprimez-la ou corrigez son orthographe. |
| `client.env: missing value for ...` | Une clé obligatoire est absente ou vide. | Renseignez `APP_NAME`, `COMPANY`, `BUNDLE_ID`, `SERVER_HOST` et `SERVER_KEY`. |
| `APP_NAME must be 1 to 40 characters among ...` | Caractère non accepté (accent, apostrophe) ou nom trop long. | Lettres ASCII, chiffres, espace, point, tiret, tiret bas. |
| `APP_NAME must differ from 'RustDesk'` | Le nom vaut `RustDesk`. | Choisissez votre propre nom. |
| `COMPANY contains unsupported characters` | Accent, apostrophe, parenthèse ou autre caractère hors de la liste acceptée. | Lettres ASCII, chiffres, espace, `.`, `,`, `&`, `-`, `_`. |
| `BUNDLE_ID must look like org.example.remotesupport` | Moins de trois éléments, un élément qui commence par un chiffre, ou un tiret bas. | Trois éléments ou plus, chacun commençant par une lettre. |
| `SERVER_HOST must be a host name, optionally with :port` | Un préfixe d'URL, un chemin ou une espace dans la valeur. | Écrivez `rustdesk.example.com`, sans `https://`. |
| `SERVER_KEY must be the server public key ...` | La valeur ne fait pas 44 caractères base64. Souvent une copie tronquée ou le `=` final oublié. | Recopiez le contenu de `id_ed25519.pub`. |
| `API_URL must be an http(s) URL` (idem `WEBSITE_URL`, `SOURCE_URL`) | `http://` ou `https://` manquant, ou caractère non accepté. | Indiquez une URL complète. |
| `ACCENT_COLOR must look like #1A2B3C` | `#` manquant, forme courte `#abc`, ou nom de couleur. | Six chiffres hexadécimaux. |

## Erreurs liées à custom.json

| Message | Cause | Correction |
| --- | --- | --- |
| `custom.json is not valid JSON: ...` | Erreur de syntaxe : virgule finale, commentaire, guillemets simples. | Validez le fichier : `python3 -m json.tool custom.json`. |
| `custom.json must contain a JSON object` | Le fichier contient une liste ou une valeur seule. | Entourez le contenu de `{ }`. |
| `custom.json: override-settings must be an object` | La section n'est pas de la forme `{ ... }`. | Corrigez la section. |
| `custom.json: override-settings.xyz must be a string` | Une valeur vaut `true`, `false` ou un nombre. | Écrivez `"Y"`, `"N"` ou `"123"`. |
| `custom.json: 'password' is not allowed ...` | `password` ou `salt` au premier niveau. | Supprimez la clé. Un mot de passe compilé dans un binaire public n'est pas un secret. |

## Erreurs liées aux visuels

| Message | Correction |
| --- | --- |
| `branding/icon.png is missing (square PNG, 1024x1024 recommended)` | Ajoutez le fichier. Son nom est en minuscules. |
| `branding/icon.png must be square and at least 256x256` | Exportez une image carrée en 1024x1024. |

## Erreurs liées aux sources de RustDesk

| Message | Cause | Correction |
| --- | --- | --- |
| `...: expected 1 occurrence(s) of '...', found 0. The RustDesk sources changed: scripts/apply.py needs an update.` | `rustdesk-version` n'est pas la version testée, et la ligne a changé côté RustDesk. | Revenez à la version par défaut. Voir [Mise à niveau de RustDesk](Upgrading-RustDesk-fr). |
| `...: file not found in the RustDesk sources` | Même cause : un fichier a été déplacé côté RustDesk. | Même correction. |
| `patch ... does not apply:` | Un de vos patchs ne correspond pas aux sources. Il touche peut-être une ligne qui dépend de `APP_NAME` ou de `ACCENT_COLOR`. | Refaites le patch. Voir [Patchs d'interface](Custom-UI-Patches-fr). |
| `... is not a RustDesk checkout with its submodules` | En local uniquement : le clone n'a pas ses sous-modules. | `git submodule update --init --recursive` |

## Problèmes de workflow

| Symptôme | Cause | Correction |
| --- | --- | --- |
| Le workflow n'apparaît pas dans l'onglet Actions. | `.github/` n'a pas été copié, ou Actions est désactivé sur le dépôt. | Vérifiez que `.github/workflows/build.yml` existe. Activez Actions dans **Settings > Actions**. |
| L'exécution échoue immédiatement : workflow réutilisable introuvable. | Référence erronée après `@`, ou votre organisation restreint les actions et workflows réutilisables autorisés. | Vérifiez la référence. Autorisez `rbsinfo/rustdesk-client` et les actions qu'il utilise dans les paramètres de l'organisation. |
| Le comportement ne correspond pas à cette documentation. | La référence après `@` et `generator-ref` sont différentes. | Rendez-les identiques. |
| Pas de release après une compilation. | L'exécution a été lancée à la main, le tag ne commence pas par `v`, ou un job de compilation a échoué. | Poussez un tag comme `v1.0.0`. Corrigez le job en échec. |
| L'étape de publication échoue sur une erreur de droits. | `permissions: contents: write` manque dans le workflow de l'instance. | Reprenez-le du modèle. |
| Une plateforme n'a pas été compilée. | Elle n'est pas dans `targets`. | Utilisez `windows`, `linux`, `macos`, séparés par des virgules. |
| Les jobs macOS échouent dans une étape de signature. | Certains des quatre secrets `MACOS_*` manquent ou sont faux. | Voir [Signature de code](Code-Signing-fr). |
| Les minutes Actions sont épuisées. | Dépôt privé. Les runners macOS comptent dix fois. | Compilez moins de plateformes, ou rendez le dépôt d'instance public. Il ne contient aucun secret. |

## Problèmes côté client

| Symptôme | Cause | Correction |
| --- | --- | --- |
| Windows affiche « Windows a protégé votre ordinateur ». | Le binaire n'est pas encore signé. | **Informations complémentaires > Exécuter quand même**. Voir [Signature de code](Code-Signing-fr). |
| macOS refuse d'ouvrir l'application. | Signature ad hoc. | **Réglages Système > Confidentialité et sécurité > Ouvrir quand même**. |
| macOS redemande Enregistrement de l'écran ou Accessibilité après une mise à jour. | Signature ad hoc : pour macOS, chaque compilation est une autre application. | Accordez-les de nouveau, ou signez avec un Developer ID. |
| Le paquet Linux refuse de s'installer ou remplace RustDesk. | Le paquet garde le nom `rustdesk`. | Désinstallez d'abord le paquet officiel. Les deux ne peuvent pas cohabiter. |
| Le client ne passe jamais à l'état prêt. | `SERVER_HOST` n'est pas résolu, ou les ports 21115 à 21117 sont bloqués. | Voir [Serveur](Server-Setup-fr). |
| Les connexions échouent sur une erreur de clé. | `SERVER_KEY` n'est pas la clé de ce serveur, ou le client du technicien utilise une autre clé. | Comparez avec `id_ed25519.pub`. Recompilez si elle était fausse. |
| Le client affiche encore l'ancien serveur après une recompilation. | Une ancienne version est toujours installée. | Désinstallez-la, puis installez la nouvelle. |
| L'utilisateur ne peut pas se connecter à un autre poste. | `"conn-type": "incoming"` est défini. | C'est le comportement voulu du modèle. Retirez la clé pour un client de technicien. |
| Le poste n'apparaît pas dans la console. | `API_URL` est vide ou fausse, ou vous n'exploitez que le serveur OSS. | Renseignez `API_URL`. Vérifiez que l'URL s'ouvre depuis le poste. |
| Tous les postes se ressemblent dans la console. | Le client n'envoie pas le nom de l'application. | Regroupez les postes côté serveur. |
| Un réglage de `custom.json` reste sans effet. | Nom mal orthographié, ou réglage placé dans la mauvaise section. | Vérifiez le nom et la section dans la [Référence de configuration](Configuration-Reference-fr). |
| Le logo RustDesk apparaît encore quelque part. | Un fichier de logo facultatif n'est pas fourni, ou l'écran le dessine autrement. | Ajoutez les fichiers listés dans [Identité visuelle](Branding-fr), ou écrivez un patch. |

## Demander de l'aide

Ouvrez un ticket sur le dépôt du générateur en indiquant :

- la référence du générateur et la version de RustDesk,
- le nom du job et de l'étape en échec,
- le message `error:` complet,
- vos fichiers `client.env` et `custom.json`. Ils ne contiennent aucun secret.

Les problèmes propres à RustDesk, sans rapport avec la personnalisation, relèvent du projet RustDesk. Reproduisez-les d'abord avec un client officiel.
