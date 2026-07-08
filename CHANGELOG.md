# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); dates are `YYYY-MM-DD`.

## [Unreleased]
### Changed
- Removed the 255-character cap on `Page.content` (was only a form-validation limit, not a DB constraint); added corresponding migration.
- Added `django-icons` dependency.
- Untracked `scripts/data/low_res_dir/` (2,265 low-res image files) from git and added it to `.gitignore`; files remain on disk and in git history, just no longer tracked going forward.

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
