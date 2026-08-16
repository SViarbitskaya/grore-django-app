# Image management

Il y a trois dossiers :

- thumbs
- file
- zoom

Il s'agit d'un jeu de données cohérent avec media_fixture.json

## Recherche sémantique (embeddings)

La recherche associe deux méthodes : correspondance de mots exacts, puis résultats sémantiques (proches en sens) via des embeddings stockés dans `note_en_embedding` / `note_fr_embedding` (pgvector).

Ces embeddings ne sont **pas** générés automatiquement à la sauvegarde d'une image. Après une migration ou l'ajout de nouvelles images (nouvelles fixtures, etc.), il faut lancer :

```bash
python manage.py generate_embeddings
```

Utiliser `--force` pour régénérer tous les embeddings existants (par exemple après un changement de modèle d'embedding). Sans cette étape, les notules concernées n'apparaîtront que dans les résultats de correspondance exacte, jamais dans les résultats sémantiques.

