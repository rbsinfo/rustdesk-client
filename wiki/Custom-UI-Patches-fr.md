[[English|Custom-UI-Patches]]

# Patchs d'interface

`client.env`, `custom.json` et `branding/` couvrent le nom, les icônes, la couleur d'accent et les réglages. Pour tout le reste (masquer un bouton, reformuler un libellé, modifier un écran), il faut écrire des patchs sur les sources de RustDesk.

Le cœur de RustDesk est écrit en Rust (`src/`, `libs/`). Son interface est écrite en Flutter/Dart (`flutter/lib/`).

## Application des patchs

- Déposez des fichiers `*.patch` dans le dossier `patches/` de votre instance.
- Ils sont appliqués avec `git apply`, dans l'ordre alphabétique des noms de fichiers.
- Ils passent en dernier : après le patch du générateur, le serveur, les noms, la page À propos, la couleur d'accent et les icônes.
- Seuls les fichiers placés directement dans `patches/` et portant l'extension `.patch` sont lus.
- Un patch qui ne s'applique pas arrête la compilation, avec une erreur qui le nomme.

Comme vos patchs passent en dernier, écrivez-les sur des sources déjà traitées par `apply.py`.

## Écrire un patch

### 1. Récupérer les sources à la version compilée

Reprenez la valeur de `rustdesk-version` dans votre `.github/workflows/build.yml`.

```sh
git clone --branch 1.5.3 --recurse-submodules https://github.com/rustdesk/rustdesk
git clone https://github.com/rbsinfo/rustdesk-client
```

### 2. Appliquer votre configuration et valider

```sh
python3 -m pip install pillow
python3 rustdesk-client/scripts/apply.py --instance chemin/vers/instance --source rustdesk
git -C rustdesk add -A
git -C rustdesk commit -m "Instance configuration applied"
```

Ce commit est votre point de départ. Il reste sur votre poste.

Si votre instance contient déjà des patchs, ils sont appliqués à cette étape et font partie du point de départ.

### 3. Faire la modification

Modifiez les fichiers dans `rustdesk/`. Restez sur un changement court et localisé : un petit patch résiste mieux aux mises à niveau.

### 4. Exporter le patch

```sh
git -C rustdesk diff > chemin/vers/instance/patches/0001-hide-something.patch
```

Numérotez les fichiers (`0001-`, `0002-`) pour maîtriser l'ordre.

Deux choses échappent à `git diff` :

- Un fichier que vous avez créé. Déclarez-le d'abord avec `git -C rustdesk add -N chemin/du/nouveau_fichier`.
- Une modification dans un sous-module, comme `libs/hbb_common`. Limitez vos patchs aux fichiers du dépôt principal de RustDesk.

Pour ajouter un autre patch, validez d'abord la modification précédente dans `rustdesk/`. Le `git diff` suivant ne contiendra ainsi que le nouveau changement.

### 5. Vérifier

Lancez la vérification sur des sources propres :

```sh
git -C rustdesk reset --hard
git -C rustdesk checkout 1.5.3
git -C rustdesk submodule update --init --recursive
python3 rustdesk-client/scripts/apply.py --instance chemin/vers/instance --source rustdesk --check
```

La sortie liste chaque élément qui serait modifié, dont `patch 0001-hide-something.patch`.

Validez ensuite le patch dans votre dépôt d'instance et lancez la compilation.

## Conseils

- Un seul objectif par patch. Celui qui échoue est alors facile à repérer et à refaire.
- Évitez les lignes que `apply.py` réécrit, comme le nom de l'application ou la couleur d'accent. Un patch dont le contexte contient votre `APP_NAME` ne s'applique plus le jour où vous renommez le client.
- N'utilisez pas un patch pour ce que `custom.json` sait faire. Les réglages survivent aux mises à niveau. Les patchs, pas toujours.
- Un patch qui compile n'est pas forcément un patch qui fonctionne. Testez le client sur chaque plateforme distribuée.
- Vos patchs font partie des sources que vous devez publier. Voir [[Licence et AGPL|License-and-AGPL-fr]].

## Après une mise à niveau de RustDesk

Un patch écrit pour une version de RustDesk peut ne plus s'appliquer à la suivante. La compilation s'arrête alors :

```text
error: patch 0001-hide-something.patch does not apply:
error: patch failed: flutter/lib/desktop/pages/connection_page.dart:120
```

Refaites le patch sur la nouvelle version en reprenant les étapes ci-dessus. Voir [[Mise à niveau de RustDesk|Upgrading-RustDesk-fr]].
