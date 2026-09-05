# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Grore is a Django 5.2 image-archive/gallery site (French/English bilingual). It has two Django apps:

- **`images/`** — the core domain: the `Image` model (identifier, slug, translated `note` caption, `file`/`thumbnail`/`zoom` image fields, `high_res` flag), gallery browsing/search, a session-based image "selection" cart, and zip download of selected/high-res images.
- **`pages/`** — a minimal flat-page CMS (`Page` model: slug, title, rich-text `content` via django-ckeditor-5) plus a static contact page.

The `grore/` directory is the Django project package (settings, root urls, wsgi/asgi).

## Commands

Environment config lives in `.env` (copy from `scripts/sample.env`; see `doc/configuration.md` for every variable). **Never quote values in `.env`** — the Makefile parses it literally.

```bash
make up              # install deps, makemigrations, migrate, collectstatic
make runserver        # run the dev server (make init only, no upgrade)
make default-pages    # make up + load scripts/data/page_fixtures.json
make load-fixtures    # flush DB, migrate, load media_fixture.json + page_fixtures.json, generate embeddings, create admin user
make init-admin-user   # createsuperuser non-interactively from DJANGO_ADMIN_* env vars
```

There are no `-nix` suffix target variants — the Makefile's `ENVIRONMENT=nix` branch is commented-out dead code, so `ENVIRONMENT=Nix` (the `scripts/sample.env` default) currently behaves identically to bare-metal (empty `EXEC_CMD`). To work under Nix, enter the shell from `default.nix` yourself, then run the plain targets from inside it; the only real nix-specific targets are the one-time machine-setup `sys-install-nix*`.

Manual Django commands run through the venv at `${APP_CACHE_ROOT}/.venv` (created by `make init`), e.g.:

```bash
${APP_CACHE_ROOT}/.venv/bin/python manage.py runserver
${APP_CACHE_ROOT}/.venv/bin/python manage.py makemigrations
${APP_CACHE_ROOT}/.venv/bin/python manage.py migrate
```

Tests use Django's standard test runner (`django.test.TestCase`), per-app:

```bash
python manage.py test images
python manage.py test pages
python manage.py test images.tests.ImageFileTestCase
```

Note: `make test-uploaded-images` is currently broken (marked `"DOESN'T WORK"` in the Makefile).

After `migrate` (which enables the pgvector extension and creates `note_en_embedding`/`note_fr_embedding`), semantic search won't return anything for rows that don't have embeddings yet. `Image.save()` computes embeddings automatically for normal add/update (admin, forms) — see Architecture notes below — but that doesn't cover bulk fixture loading (`loaddata`), so both `make load-fixtures` and the Docker Compose `entrypoint.sh` backfill automatically via `generate_embeddings` after loading data. Run it manually after any other bulk `loaddata`/`bulk_update` you do outside those paths:

```bash
${APP_CACHE_ROOT}/.venv/bin/python manage.py generate_embeddings          # only rows missing an embedding
${APP_CACHE_ROOT}/.venv/bin/python manage.py generate_embeddings --force  # re-embed everything, e.g. after changing the embedding model
```

Production/deploy targets (`make production-prepare`, `make production-install`, `make restart`) render nginx/systemd unit files from templates in `scripts/production/` and install them via sudo — see `doc/architecture.md`, `doc/integration.md`, and `doc/dev.md` for the full deploy flow (SSH to `grore-images.com`, `sudo su - django`, run `./up.sh` for prod or `./integration.sh` for the integration environment).

The repo has four long-lived branches: `main` (default PR target on GitHub), `develop`, `integration`, and `production` — `production` is what `doc/continuous.md`'s deploy command actually pulls, so it's not just a naming convention. Don't assume standard single-default-branch GitHub flow; check which of these a change is meant to land on before opening a PR.

Docker Compose is available (`docker-compose.yaml`, `make docker-compose-up`) as an alternative to the bare-metal/Nix setup; set `ENVIRONMENT=docker` in `.env` to have `make` targets shell out through `docker-compose exec`. The `django` service's `entrypoint.sh` runs on every container start/restart — it only runs `migrate` and backfills embeddings, it does **not** seed data, so a container restart is safe and won't touch existing rows. A brand-new/empty `postgres_data` volume still needs an explicit one-time `make load-fixtures` (via `docker exec`) to get any data in at all.

## Architecture notes

- **i18n via URL prefix**: all `images` and `pages` routes are wrapped in `i18n_patterns()` in `grore/urls.py`, so every page is served under `/en/...` or `/fr/...`. `LocaleMiddleware` picks the language; `DJANGO_LANGUAGE_CODE` sets the default.
- **Translated fields via django-modeltranslation**: `Image.note` (and `Page` fields) are translated through `*/translation.py` registrations rather than explicit `_en`/`_fr` model fields you'd write by hand — migrations for the shadow fields are auto-generated by modeltranslation, don't hand-edit them.
- **Image derivatives**: `Image` stores three independent, optional `ImageField`s, each format-restricted via `FileExtensionValidator` — `file` (the TIFF archival master), `thumbnail` (low-res JPG preview, 600×600), and `zoom` (high-res JPG, browser-viewable stand-in for `file`). Admin preview and most public rendering prefer `thumbnail` over `file` since browsers can't render TIFF inline (see `images/admin.py: img_preview`). Any of the three can be uploaded alone; `Image.save()` fills in whichever JPG field is missing from the best available higher-quality source (`file` outranks `zoom`; `thumbnail` is never a valid source), and never overwrites a field that's already set: `file` only → generates both `zoom` and `thumbnail`; `zoom` only → generates `thumbnail`; `thumbnail` only → generates nothing (no usable source); `file`+`thumbnail` → generates `zoom`; `file`+`zoom` → generates `thumbnail`. As with the embeddings above, this only fires on normal `.save()` calls, not fixture loading/bulk updates — `scripts/data/generate_thumbnails.py` remains the bulk-backfill path for those (and doesn't currently generate `zoom`).
- **HTMX-driven gallery**: `HomeView` (`images/views.py`) swaps its template between the full page (`images/index.html`) and a partial (`images/htmx_partial.html`) based on `request.htmx`, for infinite-scroll/paginated search without full reloads. Search is hybrid: exact whole-word matches (regex, case-insensitive, AND across terms, bilingual stopwords stripped first via `images/stopwords.py`) rank first, then semantic nearest-neighbor matches (`pgvector` `CosineDistance` over `note_en_embedding`/`note_fr_embedding`) fill in the rest. Both branches are explicitly ordered (`pk` tiebreak) since `Image` has no default ordering — needed for pagination stability across HTMX's separate per-page requests. With no search query, results are shuffled randomly instead of ordered.
- **Semantic search / embeddings**: `Image.note_en_embedding`/`note_fr_embedding` (`pgvector.django.VectorField`, 384 dims, `HnswIndex` with `vector_cosine_ops`) hold sentence embeddings of the translated notules, computed via `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`, see `images/embeddings.py`). `Image.save()` recomputes an embedding synchronously (blocking the save) whenever its source `note_en`/`note_fr` text actually changes or on first creation — only the language that changed, not both, and not other rows; `embeddings` is imported lazily inside `save()` so `sentence-transformers`/`torch` isn't loaded at Django startup for commands that never touch an `Image`. This only fires on normal `.save()` calls (admin edits, `ModelForm`), not on fixture loading (`loaddata` uses `save_base` directly) or bulk `queryset.update()`/`bulk_update()` — those still need a `generate_embeddings` run afterward (see Commands above), which batches encoding instead of doing it one row at a time. Requires the `pgvector` Postgres extension (enabled by migration `0011_enable_pgvector`); `docker-compose.yaml`'s `db` service uses the `pgvector/pgvector:pg15` image for this.
- **Session-based selection cart**: there's no cart/basket model — selected image IDs live in `request.session['selected_images']` as a list, manipulated by `SelectionMixin` (`images/mixins.py`) and exposed through `SelectionView` (list/delete) and `ToggleSelectionView` (AJAX toggle). `download_images` zips the current session selection; `download_zip` zips a single image by ID regardless of selection state.
- **Navigation/context processor**: `images.context_processors.navigation_context` is registered globally in `TEMPLATES` so nav data is available in every template without each view passing it explicitly — check `images/navigation.py` when nav rendering seems to come from nowhere in a view.
- **Rich text**: `pages.Page.content` is edited via django-ckeditor-5 (`CKEDITOR_5_CONFIGS["default"]` in `grore/settings.py`); uploaded files go through `FileSystemStorage`.
- **Fixtures/data pipeline**: `scripts/data/` holds one-off ETL scripts (`csv_to_json.py`, `generate_fixtures.py`, `clear_classeur.py`) that turn `classeur.csv` (the original image catalog) into the `Image`/`Page` fixtures loaded by `make load-fixtures`/`make default-pages`. `media_fixture.json` at the repo root and `scripts/data/notules/` are related archival/description-recovery sources — check recent commit history before assuming a script here is still the current path for a given data task.
- Top-level `*.py` scripts (`collect_low_res_images.py`, `collect_names_images.py`, `compare_low_and_high_res_images.py`, `tiff_to_jpg.py`) are standalone image-processing utilities for the media pipeline, not part of the Django app.

## Documentation

Primary docs live in `doc/`: `configuration.md` (every `.env` variable, with format constraints), `dev.md`, `installation.md`, `integration.md`, `makefile.md`, `nixpkgs.md`. Secondary: `architecture.md` (production topology diagram), `continuous.md`, `docker.md`, `nixos4django.md`. Consult `doc/configuration.md` before changing anything `.env`-related — several variables have strict formatting rules (leading/trailing slashes, no quotes) that break the Makefile/nginx/systemd templates if violated.
