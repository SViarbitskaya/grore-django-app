# Image management

Il y a trois dossiers :

- thumbs
- file
- zoom

Il s'agit d'un jeu de données cohérent avec media_fixture.json

## Les trois champs image et leur génération automatique

`file`, `thumbnail` et `zoom` sont indépendants : chacun peut être ajouté seul, aucun n'est requis. Chaque champ n'accepte qu'un format précis (validé automatiquement) :

- `file` : le master archival, **TIFF uniquement** (`.tif`/`.tiff`)
- `thumbnail` : aperçu basse résolution, **JPG uniquement**, 600×600
- `zoom` : haute résolution consultable dans le navigateur (le TIFF ne l'est pas), **JPG uniquement**

Quand une image est ajoutée ou modifiée via l'admin (ou tout formulaire normal), `Image.save()` génère automatiquement le champ JPG manquant à partir de la meilleure source disponible (`file` prime sur `zoom` ; `thumbnail` ne sert jamais de source) — sans jamais écraser un champ déjà renseigné :

| Champ(s) fourni(s) | Résultat |
| --- | --- |
| `file` seul | `zoom` et `thumbnail` générés à partir de `file` |
| `zoom` seul | `thumbnail` généré à partir de `zoom` |
| `thumbnail` seul | rien (aucune source utilisable) |
| `file` + `thumbnail` | `zoom` généré à partir de `file` |
| `file` + `zoom` | `thumbnail` généré à partir de `file` |

Comme pour les embeddings ci-dessous, ceci ne se déclenche que sur un `.save()` normal, pas lors d'un chargement en masse (`loaddata`, fixtures) — `scripts/data/generate_thumbnails.py` reste l'outil pour ce cas (il ne génère pas `zoom` actuellement).

## Recherche sémantique (embeddings)

La recherche associe deux méthodes : correspondance de mots exacts, puis résultats sémantiques (proches en sens) via des embeddings stockés dans `note_en_embedding` / `note_fr_embedding` (pgvector).

**Ajout ou modification d'une image via l'admin (ou tout formulaire normal)** : `Image.save()` calcule automatiquement l'embedding de la note qui vient de changer (`note_en` et/ou `note_fr`, selon celle qui a été modifiée), immédiatement, dans la même sauvegarde. Rien à faire manuellement dans ce cas.

**Chargement en masse (fixtures, `loaddata`, `queryset.update()`, `bulk_update()`)** : ce calcul automatique ne se déclenche pas, car ces chemins ne passent pas par `Image.save()`. Il faut alors relancer :

```bash
python manage.py generate_embeddings
```

Utiliser `--force` pour régénérer tous les embeddings existants, sans condition (par exemple après un changement de modèle d'embedding). Tant que cette commande n'a pas été lancée après un chargement en masse, les notules concernées n'apparaîtront que dans les résultats de correspondance exacte, jamais dans les résultats sémantiques.

