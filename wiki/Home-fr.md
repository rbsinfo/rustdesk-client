[[English|Home]]

# rustdesk-client

`rustdesk-client` compile, avec GitHub Actions, un client d'assistance à distance RustDesk à votre nom et déjà configuré, pour Windows, macOS et Linux. Il remplace les générateurs de clients tiers : la compilation se fait dans votre propre dépôt GitHub, à partir des sources officielles de RustDesk.

> Ce projet n'est pas affilié à RustDesk ni à Purslane. « RustDesk » est une marque de son propriétaire. Les clients produits sont des versions modifiées de RustDesk, distribuées sous licence AGPL-3.0.

## Principe

Il y a deux dépôts.

| Dépôt | Propriétaire | Contenu |
| --- | --- | --- |
| Générateur (`sadjo/rustdesk-client`) | Ce projet | `scripts/apply.py`, le workflow de compilation réutilisable, le modèle d'instance. Rien de propre à une organisation. |
| Instance | Vous | Le nom de l'application, l'adresse du serveur, sa clé publique, les icônes et d'éventuels patchs, plus un court workflow qui appelle le générateur. |

Le workflow de l'instance appelle le générateur à une référence fixe :

```yaml
jobs:
  build:
    uses: sadjo/rustdesk-client/.github/workflows/build.yml@v1
    with:
      generator-ref: v1
      rustdesk-version: "1.5.3"
```

Il n'y a aucun fork à tenir à jour. Pour passer à une version plus récente du générateur, modifiez `@v1` et `generator-ref`.

Pour chaque plateforme, la compilation :

1. Récupère les sources officielles de RustDesk au tag fixé (`1.5.3` par défaut).
2. Lance `scripts/apply.py`, qui applique votre configuration à ces sources. Chaque modification est vérifiée. Si les sources de RustDesk ont changé et qu'un motif ne correspond plus, la compilation s'arrête avec une erreur.
3. Compile le client et dépose les binaires, accompagnés d'une archive des sources modifiées.

## Ce que vous obtenez

- Un client à votre nom, avec votre icône et votre couleur d'accent.
- L'adresse et la clé publique de votre serveur compilées dans le binaire. L'utilisateur n'a rien à saisir.
- Des réglages compilés dans le binaire à partir de `custom.json`, par exemple les connexions entrantes uniquement.
- Un client qui se lance sans installation pour une session ponctuelle, et qui peut être installé en service pour l'accès sans surveillance.
- Avec un serveur d'API (RustDesk Server Pro ou une console compatible), des postes qui apparaissent dans la console avec leur ID, leur nom d'hôte, le nom d'utilisateur, le système et la version.

## Pages

| Page | À lire quand |
| --- | --- |
| [Démarrage rapide](Quick-Start-fr) | Vous voulez une première compilation. |
| [Référence de configuration](Configuration-Reference-fr) | Vous modifiez `client.env` ou `custom.json`. |
| [Identité visuelle](Branding-fr) | Vous préparez les icônes et les logos. |
| [Patchs d'interface](Custom-UI-Patches-fr) | Vous devez modifier l'interface au-delà du nom, des icônes et de la couleur. |
| [Compilation et publication](Building-and-Releasing-fr) | Vous cherchez les paramètres du workflow, les noms des fichiers produits, ou vous publiez une version. |
| [Signature de code](Code-Signing-fr) | Vous voulez signer et notariser l'application macOS, ou comprendre l'avertissement Windows. |
| [Serveur](Server-Setup-fr) | Vous voulez savoir ce que le client attend de votre serveur. |
| [Mise à niveau de RustDesk](Upgrading-RustDesk-fr) | Vous changez de version de RustDesk. |
| [Dépannage](Troubleshooting-fr) | Une compilation ou un client ne se comporte pas comme prévu. |
| [Licence et AGPL](License-and-AGPL-fr) | Vous distribuez le client. |

## Limites connues

- Windows x86_64, macOS x86_64 et Apple Silicon, Linux x86_64 uniquement. Ni Android, ni iOS.
- Le paquet et le binaire Linux gardent le nom d'origine `rustdesk`. Le paquet ne peut pas cohabiter avec le paquet RustDesk officiel.
- Les binaires Windows ne sont pas encore signés. SmartScreen affiche un avertissement. L'intégration de la signature est prévue.
- Les applications macOS reçoivent une signature ad hoc, sauf si vous fournissez un certificat Developer ID. Voir [Signature de code](Code-Signing-fr).
- L'image de l'écran de confidentialité n'est pas encore personnalisable.
- Seule la version de RustDesk par défaut est testée.
