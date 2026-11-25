[[English|Upgrading-RustDesk]]

# Mise à niveau de RustDesk

Un client est compilé à partir des sources officielles de RustDesk, à un tag fixé. La valeur par défaut est `1.5.3`. Rien ne bouge tant que vous ne la changez pas.

Le workflow de votre instance porte deux numéros de version :

```yaml
    uses: sadjo/rustdesk-client/.github/workflows/build.yml@v1
    with:
      generator-ref: v1
      rustdesk-version: "1.5.3"
```

| Valeur | Ce qu'elle désigne |
| --- | --- |
| `@v1` et `generator-ref` | La version du générateur : workflow, `apply.py`, patch du cœur. |
| `rustdesk-version` | Le tag RustDesk compilé. |

Seule la version de RustDesk par défaut d'une version du générateur est testée. Les autres peuvent fonctionner. Rien ne le garantit.

## Recommandé : suivre le générateur

1. Attendez une version du générateur qui relève la version de RustDesk par défaut.
2. Lisez ses notes de version.
3. Mettez à jour `@<ref>` et `generator-ref` si la version le demande. Les deux doivent rester identiques.
4. Passez `rustdesk-version` à la nouvelle valeur par défaut.
5. Lancez une compilation manuelle et testez le client avant de publier un tag.

## Essayer soi-même une version plus récente

Une seule ligne à changer :

```yaml
      rustdesk-version: "1.5.4"
```

Vérifiez d'abord en local. C'est l'affaire de quelques minutes, contre une compilation complète sinon.

```sh
git clone --branch 1.5.4 --recurse-submodules https://github.com/rustdesk/rustdesk rustdesk-1.5.4
git clone https://github.com/sadjo/rustdesk-client
python3 -m pip install pillow
python3 rustdesk-client/scripts/apply.py --instance chemin/vers/instance --source rustdesk-1.5.4 --check
```

`--check` n'écrit rien. La commande se termine par la liste des éléments qui seraient modifiés, ou par une erreur.

## Ce qui peut échouer

### Un motif d'apply.py ne correspond plus

`apply.py` modifie les sources de RustDesk par remplacement exact. Chaque motif doit être trouvé le nombre de fois attendu. Si la ligne a changé côté RustDesk, le script s'arrête et nomme le fichier et le motif :

```text
error: flutter/lib/common.dart: expected 1 occurrence(s) of 'Color(0xFF0071FF)', found 0. The RustDesk sources changed: scripts/apply.py needs an update.
```

C'est voulu. Mieux vaut une compilation qui s'arrête qu'un client à moitié personnalisé ou qui pointe vers le mauvais serveur.

Que faire : rester sur la version testée, et ouvrir un ticket sur le générateur avec la version de RustDesk et le message complet.

### Le patch du cœur ne s'applique plus

Le générateur applique son propre patch, `patches/core/0001-embedded-custom-client.patch`, qui compile les réglages dans le binaire.

```text
error: patch 0001-embedded-custom-client.patch does not apply:
```

Même réponse : rester sur la version testée et signaler le problème.

### Un de vos patchs ne s'applique plus

```text
error: patch 0001-hide-something.patch does not apply:
```

Le message nomme un fichier de votre dossier `patches/`. Refaites ce patch sur la nouvelle version. Voir [[Patchs d'interface|Custom-UI-Patches-fr]].

### La compilation échoue

Le workflow réutilisable installe une chaîne de compilation (Rust, Flutter, vcpkg, etc.) choisie pour la version de RustDesk par défaut. Une version plus récente de RustDesk peut en exiger une plus récente. `apply.py` passe alors, et la compilation échoue plus loin.

Cela ne se corrige pas depuis une instance. Attendez une version du générateur qui prend en charge cette version de RustDesk.

## Après une mise à niveau

1. Lancez une compilation manuelle pour chaque plateforme distribuée.
2. Testez sur de vrais postes : session ponctuelle, installation, accès sans surveillance, écrans modifiés par vos patchs.
3. Sur macOS avec une signature ad hoc, accordez de nouveau Enregistrement de l'écran et Accessibilité. Voir [[Signature de code|Code-Signing-fr]].
4. Publiez un nouveau tag. Chaque release embarque sa propre archive de sources : les sources publiées suivent la mise à niveau.

## Revenir en arrière

La configuration est dans Git. Annulez le commit qui a modifié `rustdesk-version` et recompilez.

Les clients personnalisés ne recherchent pas de mises à jour auprès de RustDesk. Vos utilisateurs ne reçoivent une nouvelle version que si vous la distribuez.
