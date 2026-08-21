# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); dates are `YYYY-MM-DD`.

## 2026-08-21
### Added
- "Delete all" button on the selection page, clearing the whole session-based selection in one action instead of removing images one at a time.
- Dismissible usage-hint banner on the homepage: "Tap or click on any text to see its image." always, plus "For a better view on mobile, turn your phone sideways." on narrow/portrait screens only. Dismissal is remembered via `localStorage` so it doesn't reappear once closed. Prompted by tester feedback that the floating-text gallery has no visual affordance suggesting the text is clickable.
### Fixed
- Infinite-scroll "load more" trigger fired twice for the same next page: `hx-trigger="revealed"` on the trigger div made htmx set up its own native intersection observer, alongside a separate custom `IntersectionObserver` in `index.js` that also manually fired the same `revealed` event (to get a 200px preload margin htmx's native trigger doesn't support). Both fired independently, so every "next page" was requested and appended twice, showing each of its images twice — most noticeable when scrolling through search results (e.g. searching "nude"). The trigger now listens for a dedicated `load-more` event that only the custom observer dispatches, so htmx no longer double-observes it; the observer is also now re-attached to each new page's trigger (previously only the first page's), guarded by a `WeakSet` so an already-fired trigger is never re-observed.

## 2026-08-16
### Added
- Semantic (embedding-based) notule search alongside the existing exact-word search. `Image` gained `note_en_embedding`/`note_fr_embedding` (`pgvector` `VectorField`, 384 dims, `paraphrase-multilingual-MiniLM-L12-v2` via `sentence-transformers`), backed by an `HnswIndex` (`vector_cosine_ops`) on each column. `manage.py generate_embeddings` (`--force`, `--batch-size`) backfills them for existing rows. Homepage search now ranks exact whole-word matches first, then fills in the rest with nearest-neighbor semantic matches (cosine distance < `0.5`) for images that don't literally contain the search words.
- `pgvector/pgvector:pg15` Postgres image (was `postgres:15`) and `pgvector`/`sentence-transformers` dependencies, to support the above.
- Bilingual (EN/FR) stopword lists (`images/stopwords.py`), selected by `request.LANGUAGE_CODE`.
### Changed
- Multi-word exact search now requires all (non-stopword) terms to match (AND), not just one (OR) — a query like "church and garden" no longer matches any row containing just "and". A query that's entirely stopwords (e.g. "a", "and the") falls back to the normal shuffled browse view instead of matching everything.
- Homepage floating-caption font size is now derived deterministically from the image id instead of `Math.random()`, so a given notule renders at the same size across reloads/rescrolls instead of visibly changing size each time; also widened the size range from `1.2–2rem` to `1–2.8rem`. (The old random version also had a range bug that collapsed it to two fixed sizes instead of a continuous range.)
- `HomeView.get_queryset` now defers the two embedding columns on the base queryset — fetching and deserializing ~768 floats per row for ~2,926 rows on every plain homepage load (never used for browsing) was adding noticeable latency.
- Both search result branches (`exact_matches`, `semantic_matches`) are now explicitly ordered by primary key, since `Image` has no default ordering; previously, HTMX's separate per-page infinite-scroll requests could each re-run the unordered query and get rows back in a different order, causing the same image to land in more than one page and appear as a duplicate/triplicate while scrolling.
- `paginate_by` reduced from 15 to 10.

## 2026-08-03
### Added
- `Image.ai_gen` boolean field (default `False`) marking whether an image's description was AI-generated, for future filtering/reporting.
- Zoom modal now has a back button that returns to the thumbnail view it was opened from, instead of the only option being to close the zoom view entirely.
### Changed
- Generated `note_fr`/`note_en` captions for all 813 images that previously had the "Pas de description" / "No description" placeholder, matching the style and established damage vocabulary (`Fragment déchiré.`, `Image avec déchirure, reconstituée.`, `Image très abîmée.`, etc.) of the existing human-written entries. Each generated caption is marked with a trailing ᴬᴵ superscript and `ai_gen=True` to distinguish it from human-written descriptions.
- Fixed `make load-fixtures` pointing at `scripts/data/classeur.json`, a file that hasn't existed since commit `64d50b6`; it now loads `media_fixture.json`, the fixture that's actually been maintained (notule descriptions, zoom/high_res fields).
### Fixed
- Zoom modal was stretching every high-res image to 100% of the screen width regardless of its actual resolution, making lower-res images look blurry when enlarged. The image now renders at its native size (capped by `max-width: 100%`), so it only fills the screen when its resolution is at least screen-width, and otherwise displays at its own max resolution instead of being upscaled.
- Stripped a stray leading `: ` parser artifact from 7 notule descriptions (`X1151X`, `X1350X`, `X1354X`, `X2285X`, `X2311`, `X4722X`, `X6292`).
- The floating scroll up/down buttons sat above the zoom modal (higher `z-index`) and stayed visible/clickable over the fullscreen zoomed image; they're now hidden while the zoom modal is open and reappear when it closes.
- Corrected 31 French/English spelling errors across 26 notule descriptions, found by running the full corpus through a spellchecker and manually reviewing every flagged word in context (missing/wrong accents, letter transpositions, a missing space, and "Renaud 5" → "Renault 5").

## 2026-07-08 – 2026-07-21
### Changed
- Removed the 255-character cap on `Page.content` (was only a form-validation limit, not a DB constraint); added corresponding migration.
- Added `django-icons` dependency.
- Untracked `scripts/data/low_res_dir/` (2,265 low-res image files) from git and added it to `.gitignore`; files remain on disk and in git history, just no longer tracked going forward. Broadened this to ignore all of `scripts/data/`.
- Populated `media_fixture.json` with real notes: parsed the `scripts/data/notules/Notules_*.doc` archive documents (2,139 unique image descriptions in French) and applied them to `note_fr` for 2,089 matching entries, with `note_en` generated via machine translation. The remaining 837 entries without a matching notule now read "Pas de description" / "No description" instead of the old `test_fr`/`test_en` placeholders. 50 notule identifiers had typos in the source docs and didn't match any fixture entry; 8 identifiers had conflicting duplicate descriptions in the source and kept only the first occurrence — see conversation history for the flagged lists.
- Resolved 6 of the 8 conflicting-description identifiers above by visually inspecting the actual image: `A4323` needed correcting (was mismatched to a swimsuit-woman description, actually a portrait of a brown-haired boy); the other 5 already had the right text. `A6555XX6556` and `X3814X` remain ambiguous and unresolved.
- Recovered descriptions for 24 more `low_res_dir` images (79 → 55 still missing out of 2,165): fixed 14 more typo'd file extensions in the notules docs; fixed a parser bug where 3 bullet lines merged two image entries onto one line, silently dropping the second (`X3371X`/`X3370X`, `X1379X`/`X1378X`, `A3252X`); and visually matched 5 identifiers (`A1266`, `A3433`, `X1162`, `X2216`, `X1340`) whose notules description referenced a nonexistent "X"-suffixed sibling file. The remaining 55 have no notules text anywhere in the corpus, except 4 (`A6162jpg`/`A6165jpg`/`A6214jpg`/`A6215jpg`) whose clean-named siblings already have descriptions but whose actual disk filenames have a doubled `.jpg` typo — a file-reference issue, not a missing-description one.
### Added
- Rich text editing for `Page.content` in the Django admin via `django-ckeditor-5` (widget swapped in on the existing `TextField`, kept translation-compatible with `django-modeltranslation`); page template now renders content as HTML.
- Double-clicking the picture in the thumbnail modal now also opens the high-res zoom view, in addition to the existing zoom button. The image only shows a zoom-in cursor (and only responds to double-click) when it actually has a high-res version; removed the blanket pointer cursor the whole modal used to inherit, which made non-zoomable images look clickable when only the buttons actually were.
### Fixed
- Homepage zoom modal now opens fullscreen and fits the high-res image to the screen width (no more horizontal scrolling); height still scrolls vertically if taller than the viewport. Native browser pinch-to-zoom / Ctrl+scroll (never disabled by this site's viewport meta) already lets users zoom in further for detail, so no custom zoom/pan JS was needed.
- Homepage floating-caption text no longer flickers/vibrates in place after resizing the window: the drift animation cached container/item bounds once and never refreshed them, trapping a resized item between stale limits. Positions are now recalculated on resize and movement is driven by `transform` instead of `left`/`top`.
- Zoom images appearing black/blank: the click handler for the zoom button was only wired up for images present at initial page load, so images loaded later via infinite scroll opened an empty zoom modal; also fixed stacked modal backdrops (thumbnail modal not closing before the zoom modal opened) compounding the effect. Switched to a single delegated click handler and explicit modal hand-off.
- Admin image preview showing broken for high-res images: `img_preview` rendered `obj.file` directly, which for `high_res=True` entries is the original `.tiff` (not renderable inline by browsers). Now prefers `obj.thumbnail` (a browser-safe JPG).

## 2026-02-08
### Added
- High-resolution file download management alongside existing low-res downloads.
- New media fixtures.

## 2026-01-10 – 2026-01-11
### Added
- Thumbnail generation, image zoom view, and high-resolution image handling.
### Changed
- Redesign of UI buttons.

## 2025-09-21 – 2025-10-07
### Added
- Scroll-down button and new up/down navigation buttons on the homepage.
### Changed
- Homepage text animation (speed/direction), general CSS polish.
- Split documentation into separate files under `doc/`.
- Updated Python dependencies; minor Dockerfile and template fixes.
### Docs
- Added server update/deployment documentation (French).

## 2024-12-12 – 2024-12-22
### Added
- `gettext`-based translations and a navigation menu via context processors.
### Changed
- Improved selection page styling; active nav-link highlighting.
### Fixed
- Reduced overly verbose log level from error to info.

## 2024-11-18 – 2024-11-29
### Added
- Release `0.0.2`.
### Fixed
- Homepage text-movement animation.
- Selection toggle button behavior in modals.
- Special-character handling in image notes.
### Changed
- Makefile venv caching adjustment.

## 2024-11-03 – 2024-11-08
### Added
- Nix flake packaging for Grore (`getgrore` install command), including a `0.1.2-alpha` release.
- `default.nix`, `make sys-install-nix` target.
### Changed
- Extensive Docker/Docker Compose setup and hardening (user/group permissions, entrypoint, Postgres startup ordering, static files).
- Consolidated environment variables (`APP_DJANGO_USER_*`, database variable renaming).
- Reorganized fixtures into `scripts/data/`.
### Docs
- Split and expanded project documentation (installation, architecture diagram, Makefile).
### Fixed
- Flickering menu/modal in mobile view; apostrophe-escaping bug.

## 2024-10-01 – 2024-10-30
### Added
- `SelectionMixin` / `SelectionView` for selecting and managing multiple images (AJAX/HTMX-based toggle, removal from selection page and table).
- Initial Dockerfile and `docker-compose.yaml` for preprod/prod.
- Production branch with centralized `.env` configuration.
- README.
### Changed
- Homepage layout/design overhaul; smoother infinite loading and scrolling.
- Randomized image order on the homepage.
- CSRF trusted origins, allowed hosts, static file settings for production.
### Fixed
- Full-word-only search matching.

## 2024-02-13 – 2024-05-16
### Added
- Initial Django project scaffold and `Image` model.
- Homepage, image detail page, and search.
- Flatpages, later replaced by a dedicated `pages` app with translatable content.
- Language switcher with locale-prefixed URLs and translated templates.
- Slugs for images; infinite scroll; CSV-to-JSON import script.
### Fixed
- Routing for pages; duplicate entries in imported CSV data.
