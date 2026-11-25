[[English|License-and-AGPL]]

# Licence et AGPL

Cette page est un résumé pratique. Ce n'est pas un avis juridique. Le texte de la licence fait foi : voir le fichier `LICENSE` du générateur et celui de RustDesk.

## Qui détient quoi

| Élément | Licence | Titulaire |
| --- | --- | --- |
| RustDesk | AGPL-3.0 | Ses auteurs. « RustDesk » est une marque de son propriétaire. |
| `rustdesk-client` (ce générateur) | AGPL-3.0 | Ses contributeurs |
| Votre dépôt d'instance | Votre configuration, vos icônes et vos patchs | Vous |
| Le client que vous compilez | AGPL-3.0, en tant que version modifiée de RustDesk | Les auteurs de RustDesk pour le code d'origine, vous pour vos modifications |

`rustdesk-client` est un projet indépendant. Il n'est ni affilié à RustDesk ou Purslane, ni approuvé ou pris en charge par eux. Les clients que vous compilez ne sont pas des produits officiels RustDesk.

## Ce que l'AGPL vous demande

Vous distribuez un client dès qu'une personne extérieure à votre organisation le reçoit : un client, un partenaire, un utilisateur qui le télécharge sur votre site.

Quand vous distribuez un client, vous devez :

1. **Proposer le code source correspondant complet** à toute personne qui reçoit le client. Il s'agit des sources de RustDesk telles que modifiées pour votre compilation, vos patchs compris.
2. **Conserver les mentions** : mentions de copyright, texte de la licence, indication que le programme est sous AGPL-3.0.
3. **Indiquer que le programme a été modifié.**
4. **Transmettre les mêmes droits.** Les destinataires peuvent utiliser, étudier, modifier et redistribuer le client sous AGPL-3.0. Vous ne pouvez pas ajouter de restriction.

## Ce que le générateur fait pour vous

| Obligation | Comment elle est couverte |
| --- | --- |
| Code source correspondant complet | Chaque compilation archive les sources de RustDesk après application de `apply.py` et de vos patchs. Chaque release les joint sous le nom `<slug>-<version>-source.tar.gz`. |
| Mentions | La mention de copyright et la licence d'origine sont conservées dans les sources et dans la page À propos. |
| Indication de modification | La page À propos affiche `Built by <COMPANY>. Modified version of RustDesk (AGPL-3.0).` |
| Où trouver les sources | La page À propos affiche `Source code: <SOURCE_URL>` quand `SOURCE_URL` est renseignée. |
| Texte de la release | La description de la release indique que le client est une version modifiée de RustDesk sous AGPL-3.0 et que les sources sont jointes. |

## Ce qui reste à votre charge

- **Renseigner `SOURCE_URL`** dans `client.env`. L'adresse doit mener à un endroit où les destinataires peuvent obtenir les sources : votre dépôt d'instance s'il est public, ou une page qui propose l'archive.
- **Rendre les sources accessibles.** Si votre dépôt d'instance est privé, ses releases le sont aussi. Publiez le `-source.tar.gz` de chaque version distribuée à un endroit accessible à vos utilisateurs, sans frais.
- **Conserver les sources de chaque version distribuée**, pas seulement de la dernière.
- **Distribuer l'archive correspondante.** L'archive de sources d'une release correspond aux binaires de cette même release.
- **Ne pas retirer les mentions** avec un patch. Ne pas présenter le client comme un logiciel officiel RustDesk.

```ini
SOURCE_URL=https://github.com/example-org/remote-support
```

## Marque

« RustDesk » est une marque de son propriétaire. L'AGPL vous donne des droits sur le code, pas sur le nom ni sur le logo.

- `APP_NAME` ne peut pas valoir `RustDesk`. La compilation le refuse.
- Utilisez votre propre icône et vos propres logos. Voir [[Identité visuelle|Branding-fr]].
- Vous pouvez indiquer, comme un fait, que votre client est basé sur RustDesk. La page À propos le fait.

## Questions

**Ma configuration est-elle secrète ?** Non. L'hôte du serveur, la clé publique et tous les réglages se lisent dans le client. Un dépôt d'instance privé ne cache rien que le binaire ne révèle déjà.

**Dois-je publier mon dépôt d'instance ?** Non. Vous devez proposer les sources correspondant à ce que vous distribuez. L'archive de sources y répond. Un dépôt d'instance public reste le moyen le plus simple.

**Nous n'utilisons le client qu'en interne.** L'usage interne n'est en général pas considéré comme une distribution, mais la frontière dépend de votre situation : prestataires, filiales, clients. Interrogez votre conseil juridique. Publier l'archive de sources règle la question.

**Puis-je faire payer le client ou le support ?** L'AGPL ne l'interdit pas. Elle interdit de restreindre les droits des destinataires.
