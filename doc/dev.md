# GRORE Development

Repository: https://github.com/SViarbitskaya/grore-django-app

Production: https://grore-images.com
Integration/staging (demarchic): https://grore-images.demarchic.com

## Local development

See `doc/installation.md` for the Nix setup, `doc/makefile.md` for the `make` targets, and `doc/docker.md` for the Docker Compose alternative. In short:

```bash
cp scripts/sample.env .env    # then edit .env — see doc/configuration.md
make up                       # installs deps, makemigrations, migrate, collectstatic
make runserver
```

or, via Docker Compose:

```bash
docker compose up -d
docker compose exec django python manage.py test
```

## Server access (integration/production)

See `doc/integration.md` for how deploys work, and `doc/continuous.md` for the GitHub Actions CI/CD pipeline that drives them.

```bash
ssh django@grore-images.com
```

Django runs as the `grore-images.demarchic.com.service` (integration) / `grore.service` (production) systemd units — check with `systemctl status <unit>`.
