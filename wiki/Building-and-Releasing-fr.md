[[English|Building-and-Releasing]]

# Compilation et publication

## Le workflow de l'instance

Votre dépôt d'instance contient un seul workflow, `.github/workflows/build.yml`. Il appelle le workflow réutilisable du générateur.

```yaml
name: Build client

on:
  workflow_dispatch:
    inputs:
      targets:
        description: Platforms to build (windows, linux, macos)
        default: "windows,linux,macos"
  push:
    tags: ["v*"]

permissions:
  contents: write

jobs:
  build:
    # Keep the ref after "@" and `generator-ref` identical.
    uses: rbsinfo/rustdesk-client/.github/workflows/build.yml@v1
    with:
      generator-ref: v1
      rustdesk-version: "1.5.3"
      targets: ${{ inputs.targets || 'windows,linux,macos' }}
      release-tag: ${{ startsWith(github.ref, 'refs/tags/') && github.ref_name || '' }}
    secrets: inherit
```

Deux déclencheurs :

| Déclencheur | Résultat |
| --- | --- |
| Lancement manuel (**Actions > Build client > Run workflow**) | Des binaires de test, conservés comme artefacts de l'exécution. Pas de release. |
| Push d'un tag qui commence par `v` | Toutes les plateformes sont compilées et une release GitHub est publiée sous ce tag. |

## Paramètres du workflow réutilisable

| Paramètre | Valeur par défaut | Signification |
| --- | --- | --- |
| `rustdesk-version` | `"1.5.3"` | Tag RustDesk à compiler. Seule la valeur par défaut est testée. |
| `targets` | `"windows,linux,macos"` | Liste séparée par des virgules parmi `windows`, `linux`, `macos`. |
| `instance-path` | `"."` | Dossier de l'instance dans le dépôt appelant. |
| `release-tag` | `""` | Si renseigné, les binaires sont publiés dans une release GitHub portant ce tag. |
| `generator-repository` | `"rbsinfo/rustdesk-client"` | Dépôt qui fournit `scripts/apply.py`. À modifier uniquement si vous appelez un fork. |
| `generator-ref` | `"v1"` | Référence du générateur. Elle doit rester identique à celle placée après `@` dans `uses:`. |

La référence après `@` choisit le fichier de workflow. `generator-ref` choisit les scripts et les patchs. Si elles diffèrent, le workflow et les scripts risquent de ne pas aller ensemble.

## Secrets

Tous les secrets sont facultatifs. Ils ne concernent que la signature macOS. Voir [[Signature de code|Code-Signing-fr]].

| Secret | Contenu |
| --- | --- |
| `MACOS_P12_BASE64` | Certificat Developer ID (`.p12`), encodé en base64 |
| `MACOS_P12_PASSWORD` | Mot de passe du fichier `.p12` |
| `MACOS_CODESIGN_IDENTITY` | Identité de signature |
| `MACOS_NOTARIZE_JSON` | Clé d'API App Store Connect pour `rcodesign`, encodée en base64 |

`secrets: inherit` transmet les secrets de votre dépôt au workflow du générateur.

## Jobs

| Job | Runner | Exécuté quand |
| --- | --- | --- |
| `bridge` | `ubuntu-22.04` | Toujours. Génère le pont Dart/Rust et archive les sources modifiées. |
| `windows privacy window` | `windows-2022` | `targets` contient `windows` |
| `windows x86_64` | `windows-2022` | `targets` contient `windows` |
| `macos x86_64` | `macos-15-intel` | `targets` contient `macos` |
| `macos aarch64` | `macos-15` | `targets` contient `macos` |
| `linux x86_64` | `ubuntu-22.04` | `targets` contient `linux` |
| `release` | `ubuntu-22.04` | `release-tag` est renseigné et aucun job n'a échoué ni été annulé |

Chaque job de compilation récupère RustDesk au tag demandé, le générateur et votre instance, puis lance `scripts/apply.py` avant de compiler.

Les compilations tournent sur les runners hébergés par GitHub et durent environ 30 à 60 minutes.

## Fichiers produits

`<slug>` est `APP_NAME` en minuscules avec des tirets : `Remote Support` donne `remote-support`. `<version>` est la version de RustDesk, par exemple `1.5.3`.

| Fichier | Plateforme | Contenu |
| --- | --- | --- |
| `<slug>-<version>-windows-x86_64.exe` | Windows x86_64 | Exécutable auto-extractible. Se lance sans installation et peut installer le client. |
| `<slug>-<version>-windows-x86_64.msi` | Windows x86_64 | Paquet MSI, pour les outils de déploiement. |
| `<slug>-<version>-macos-x86_64.dmg` | macOS, Intel | Image disque. |
| `<slug>-<version>-macos-aarch64.dmg` | macOS, Apple Silicon | Image disque. |
| `<slug>-<version>-linux-x86_64.deb` | Linux x86_64 | Paquet Debian/Ubuntu. |
| `<slug>-<version>-linux-x86_64.rpm` | Linux x86_64 | Paquet RPM. |
| `<slug>-<version>-source.tar.gz` | toutes | Les sources de RustDesk telles que modifiées pour votre client. |
| `SHA256SUMS` | toutes | Sommes de contrôle des fichiers ci-dessus. Uniquement dans les releases. |

Lors d'un lancement manuel, les fichiers sont regroupés dans ces artefacts :

| Artefact | Contenu |
| --- | --- |
| `client-windows-x86_64` | `.exe` et `.msi` |
| `client-macos-x86_64` | `.dmg` |
| `client-macos-aarch64` | `.dmg` |
| `client-linux-x86_64` | `.deb` et `.rpm` |
| `client-source` | `-source.tar.gz` |

Les autres artefacts d'une exécution (`bridge-artifact`, `bridge-artifact-flutter-3.44`, `topmostwindow-artifacts-x64`) sont des fichiers intermédiaires.

## Compiler à la demande

Depuis l'onglet Actions, ou avec la CLI GitHub :

```sh
gh workflow run "Build client" -f targets=windows
gh run watch
gh run download --name client-windows-x86_64
```

## Publier une version

```sh
git tag v1.0.0
git push origin v1.0.0
```

La release est créée dans votre dépôt d'instance avec :

- tous les binaires,
- l'archive des sources,
- `SHA256SUMS`,
- une description qui indique la version de RustDesk, le commit de votre configuration et la licence.

Le tag est votre propre numéro de version. Il nomme la release, pas les fichiers : les noms de fichiers portent la version de RustDesk. Deux releases compilées à partir de la même version de RustDesk contiennent des fichiers de même nom.

Pour contrôler un téléchargement :

```sh
sha256sum --check --ignore-missing SHA256SUMS
```

## Coût

- Dépôt d'instance public : les runners hébergés par GitHub sont gratuits.
- Dépôt d'instance privé : les compilations consomment vos minutes Actions. Les runners macOS comptent dix fois. Limitez-vous aux plateformes utiles avec `targets`.

## Figer le générateur

`@v1` suit la ligne `v1` du générateur. Pour une compilation qui ne change pas tant que vous ne l'avez pas décidé, indiquez le SHA complet d'un commit du générateur aux deux endroits :

```yaml
    uses: rbsinfo/rustdesk-client/.github/workflows/build.yml@0123456789abcdef0123456789abcdef01234567
    with:
      generator-ref: 0123456789abcdef0123456789abcdef01234567
```

## Plusieurs clients

Créez un dépôt d'instance par client. Les releases, les tags et les sources publiées de chaque client restent ainsi séparés.
