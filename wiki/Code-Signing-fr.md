[[English|Code-Signing]]

# Signature de code

| Plateforme | Par défaut | Avec votre certificat |
| --- | --- | --- |
| Windows | Non signé. SmartScreen avertit. | Pas encore intégré. Prévu. |
| macOS | Signature ad hoc. Gatekeeper bloque le premier lancement. | Signature Developer ID et notarisation, avec quatre secrets. |
| Linux | Paquets non signés. | Non intégré. |

Chaque release contient `SHA256SUMS` : l'utilisateur peut au moins vérifier l'intégrité d'un téléchargement.

## Windows

Les fichiers `.exe` et `.msi` ne sont pas encore signés. Au premier lancement, Windows SmartScreen peut afficher « Windows a protégé votre ordinateur ».

Côté utilisateur : **Informations complémentaires > Exécuter quand même**.

Ce que vous pouvez faire en attendant :

- Prévenir vos utilisateurs de l'avertissement et publier la somme de contrôle à côté du lien de téléchargement.
- Déployer le `.msi` avec votre outil de gestion de parc plutôt que de le faire télécharger.
- Signer vous-même les fichiers téléchargés avec votre certificat et `signtool`. Les fichiers contenus dans l'exécutable auto-extractible restent non signés, et les sommes de `SHA256SUMS` ne correspondent plus aux fichiers signés.

La signature dans le workflow est prévue.

## macOS sans certificat

Sans secrets, l'application reçoit une signature ad hoc. Elle fonctionne, mais macOS n'en connaît pas l'éditeur.

Premier lancement :

1. Ouvrez l'image disque et glissez l'application dans **Applications**.
2. Ouvrez l'application. macOS refuse.
3. Ouvrez **Réglages Système > Confidentialité et sécurité**, descendez jusqu'au message concernant l'application et cliquez sur **Ouvrir quand même**.

Autorisations :

1. À la première utilisation, accordez **Enregistrement de l'écran** et **Accessibilité** dans **Réglages Système > Confidentialité et sécurité**.
2. Après chaque mise à jour du client, accordez-les de nouveau. Une signature ad hoc change à chaque compilation : pour macOS, la mise à jour est une autre application. Si les interrupteurs semblent activés mais que le client redemande l'autorisation, retirez l'entrée de la liste puis ajoutez-la de nouveau.

C'est acceptable pour quelques postes administrés. Pour une diffusion plus large, signez avec un Developer ID.

## macOS avec un Developer ID

Il faut une adhésion payante à l'Apple Developer Program.

Le workflow signe alors l'application avec votre identité, construit l'image disque, la signe, la soumet à Apple pour notarisation et y agrafe le ticket. Gatekeeper ouvre l'application sans avertissement, et les autorisations sont conservées d'une mise à jour à l'autre.

### Secrets

Ajoutez ces quatre secrets à votre dépôt d'instance (**Settings > Secrets and variables > Actions**), ou au niveau de l'organisation.

| Secret | Contenu |
| --- | --- |
| `MACOS_P12_BASE64` | Votre certificat « Developer ID Application » avec sa clé privée, exporté en `.p12`, encodé en base64 |
| `MACOS_P12_PASSWORD` | Mot de passe choisi à l'export du `.p12` |
| `MACOS_CODESIGN_IDENTITY` | Nom de l'identité, par exemple `Developer ID Application: Example Org (ABCDE12345)` |
| `MACOS_NOTARIZE_JSON` | Clé d'API App Store Connect au format JSON de `rcodesign`, encodée en base64 |

La signature s'active dès que `MACOS_P12_BASE64` existe. Fournissez les quatre secrets : s'il en manque, les jobs macOS échouent.

### Préparer les valeurs

Exportez le certificat depuis Trousseaux d'accès sous le nom `developer-id.p12`, puis :

```sh
base64 -i developer-id.p12 -o developer-id.p12.b64
security find-identity -v -p codesigning
```

La seconde commande affiche le nom de l'identité à utiliser pour `MACOS_CODESIGN_IDENTITY`.

Créez une clé d'API App Store Connect (App Store Connect > Utilisateurs et accès > Intégrations). Notez l'identifiant de l'émetteur (issuer ID) et l'identifiant de la clé, puis téléchargez le fichier `.p8`. Convertissez-le avec `rcodesign` :

```sh
rcodesign encode-app-store-connect-api-key -o notarize.json <issuer-id> <key-id> AuthKey_<key-id>.p8
base64 -i notarize.json -o notarize.json.b64
```

Enregistrez les secrets avec la CLI GitHub, depuis votre dépôt d'instance :

```sh
gh secret set MACOS_P12_BASE64 < developer-id.p12.b64
gh secret set MACOS_P12_PASSWORD
gh secret set MACOS_CODESIGN_IDENTITY --body "Developer ID Application: Example Org (ABCDE12345)"
gh secret set MACOS_NOTARIZE_JSON < notarize.json.b64
```

Supprimez ensuite les fichiers `.p12`, `.b64` et `.json` restés sur votre poste.

### Contrôler

Après une compilation, sur un Mac :

```sh
spctl --assess --type open --context context:primary-signature -v remote-support-1.5.3-macos-aarch64.dmg
```

La réponse doit contenir `accepted` et `Notarized Developer ID`.

### Remarques

- Le workflow de l'instance doit conserver `secrets: inherit`. Sans cette ligne, les secrets n'arrivent pas jusqu'au workflow du générateur.
- Gardez le même Developer ID et le même `BUNDLE_ID` d'une version à l'autre. Si l'un des deux change, macOS redemande les autorisations.
- Les secrets ne servent qu'aux jobs macOS.
