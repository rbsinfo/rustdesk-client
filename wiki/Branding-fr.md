[[English|Branding]]

# Identité visuelle

L'identité visuelle d'un client vient de trois endroits :

| Élément | Emplacement |
| --- | --- |
| Nom de l'application | `APP_NAME` dans `client.env` |
| Couleur d'accent | `ACCENT_COLOR` dans `client.env` |
| Icônes et logos | Fichiers PNG du dossier `branding/` de l'instance |

Tout le reste de l'interface se modifie avec des patchs. Voir [[Patchs d'interface|Custom-UI-Patches-fr]].

## Fichiers

```text
branding/
  icon.png                 obligatoire
  logo.png                 facultatif
  logo_light.png           facultatif
  logo_dark.png            facultatif
  mac-tray-dark-x2.png     facultatif
  mac-tray-light-x2.png    facultatif
```

| Fichier | Obligatoire | Règles | Usage |
| --- | --- | --- | --- |
| `icon.png` | oui | PNG carré, 256x256 au minimum. 1024x1024 recommandé. | Source de toutes les icônes de l'application. |
| `logo.png` | non | Copié tel quel. | Remplace la ressource RustDesk `flutter/assets/logo.png`. |
| `logo_light.png` | non | Copié tel quel. | Remplace `flutter/assets/logo_light.png`. |
| `logo_dark.png` | non | Copié tel quel. | Remplace `flutter/assets/logo_dark.png`. |
| `mac-tray-dark-x2.png` | non | Copié tel quel. | Remplace l'icône de barre des menus macOS `res/mac-tray-dark-x2.png`. |
| `mac-tray-light-x2.png` | non | Copié tel quel. | Remplace l'icône de barre des menus macOS `res/mac-tray-light-x2.png`. |

Les autres fichiers de `branding/` sont ignorés.

## icon.png

La compilation s'arrête si `icon.png` est absent, n'est pas carré ou mesure moins de 256x256.

Toutes les icônes livrées par RustDesk sont générées à partir de ce seul fichier :

| Fichier généré | Contenu |
| --- | --- |
| `res/icon.ico`, `flutter/windows/runner/resources/app_icon.ico` | Icône Windows aux tailles 16, 20, 24, 32, 40, 48, 64, 96, 128 et 256 |
| `res/tray-icon.ico` | Icône de zone de notification Windows aux tailles 16, 24, 32 et 48 |
| `res/icon.png`, `res/mac-icon.png` | 1024x1024 |
| `res/32x32.png`, `res/64x64.png`, `res/128x128.png`, `res/128x128@2x.png` | Icônes Linux et d'empaquetage |
| `res/scalable.svg`, `flutter/assets/icon.svg` | Le PNG 256x256 encapsulé dans un fichier SVG |
| `flutter/assets/icon.png` | 256x256 |
| `flutter/macos/Runner/AppIcon.icns` et les images de `AppIcon.appiconset` | Icône de l'application macOS |

Conseils :

- Fournissez du 1024x1024. Une icône plus petite est agrandie pour les grandes tailles et paraît floue.
- Gardez un dessin lisible en 16x16 : c'est aussi l'icône de la zone de notification.
- Utilisez un fond transparent si l'icône n'occupe pas tout le carré. La transparence est conservée.
- Les fichiers SVG ne font qu'encapsuler une image bitmap. Une source vectorielle n'apporte rien : exportez-la en PNG.

## Fichiers facultatifs

Les fichiers facultatifs sont copiés sans conversion ni contrôle. Chacun remplace le fichier d'origine du même nom. Ouvrez ce fichier dans les sources de RustDesk, à la version que vous compilez, et reprenez les mêmes dimensions et le même type de fond.

Quand un fichier facultatif est absent, l'image d'origine reste dans le client. Parcourez les écrans de votre client et ajoutez les fichiers de logo si le logo RustDesk apparaît encore quelque part.

## Pas encore personnalisable

- L'image de l'écran de confidentialité, affichée sur l'écran distant quand le mode confidentialité est actif.
- Le nom du paquet et du binaire Linux, qui restent `rustdesk`.

## Ne réutilisez pas le logo RustDesk

« RustDesk » et son logo appartiennent à leur propriétaire. Utilisez votre propre nom et vos propres visuels. `APP_NAME` ne peut pas valoir `RustDesk`.
