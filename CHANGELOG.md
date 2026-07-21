# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); dates are `YYYY-MM-DD`.

## [Unreleased]
### Changed
- Removed the 255-character cap on `Page.content` (was only a form-validation limit, not a DB constraint); added corresponding migration.
- Added `django-icons` dependency.
- Untracked `scripts/data/low_res_dir/` (2,265 low-res image files) from git and added it to `.gitignore`; files remain on disk and in git history, just no longer tracked going forward. Broadened this to ignore all of `scripts/data/`.
- Populated `media_fixture.json` with real notes: parsed the `scripts/data/notules/Notules_*.doc` archive documents (2,139 unique image descriptions in French) and applied them to `note_fr` for 2,089 matching entries, with `note_en` generated via machine translation. The remaining 837 entries without a matching notule now read "Pas de description" / "No description" instead of the old `test_fr`/`test_en` placeholders. 50 notule identifiers had typos in the source docs and didn't match any fixture entry; 8 identifiers had conflicting duplicate descriptions in the source and kept only the first occurrence — see conversation history for the flagged lists.
- Resolved 6 of the 8 conflicting-description identifiers above by visually inspecting the actual image: `A4323` needed correcting (was mismatched to a swimsuit-woman description, actually a portrait of a brown-haired boy); the other 5 already had the right text. `A6555XX6556` and `X3814X` remain ambiguous and unresolved.
- Recovered descriptions for 24 more `low_res_dir` images (79 → 55 still missing out of 2,165): fixed 14 more typo'd file extensions in the notules docs; fixed a parser bug where 3 bullet lines merged two image entries onto one line, silently dropping the second (`X3371X`/`X3370X`, `X1379X`/`X1378X`, `A3252X`); and visually matched 5 identifiers (`A1266`, `A3433`, `X1162`, `X2216`, `X1340`) whose notules description referenced a nonexistent "X"-suffixed sibling file. The remaining 55 have no notules text anywhere in the corpus, except 4 (`A6162jpg`/`A6165jpg`/`A6214jpg`/`A6215jpg`) whose clean-named siblings already have descriptions but whose actual disk filenames have a doubled `.jpg` typo — a file-reference issue, not a missing-description one.
### Added
- Rich text editing for `Page.content` in the Django admin via `django-ckeditor-5` (widget swapped in on the existing `TextField`, kept translation-compatible with `django-modeltranslation`); page template now renders content as HTML.
- Double-clicking the picture in the thumbnail modal now also opens the high-res zoom view, in addition to the existing zoom button. The image only shows a zoom-in cursor (and only responds to double-click) when it actually has a high-res version.
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
