# GitHub Actions CI/CD

Three workflows, `.github/workflows/`:

- `ci.yml` — runs the test suite on every push/PR.
- `deploy-integration.yml` — triggered by `workflow_run` when `ci.yml` succeeds on the `integration` branch. SSHes into `grore-images.com` and runs `/home/django/integration.sh`. No approval gate: `integration` (demarchic) is the staging environment clients test against, so it's meant to update as soon as `integration` gets new, tested commits.
- `deploy-production.yml` — same trigger, but on the `production` branch, and targets the `production` GitHub Environment (Settings > Environments > production), which has a required-reviewer rule. The job pauses until someone with write access clicks "Approve" in the Actions tab before it SSHes in and runs `/home/django/up.sh`.

Both deploy scripts do the same thing on the server: sync the branch (`git fetch` + `git reset --hard @{u}`), enter the Nix shell from `default.nix` (`nix develop --extra-experimental-features "nix-command flakes"`), run `make up`, then restart the relevant systemd unit. `integration.sh` additionally recomputes `LD_LIBRARY_PATH` from the Nix shell and writes it into `.env` (consumed by the unit's `EnvironmentFile=` directive), since gunicorn as launched by systemd doesn't inherit the Nix shell's environment.

## Setting up the deploy key

Both deploy workflows authenticate via the `GRORE_DEPLOY_KEY` repository secret (Settings > Secrets and variables > Actions):

```bash
ssh-keygen -t ed25519 -f grore_deploy_key    # use a distinct name, not your default key
```

- Private key (`cat grore_deploy_key`) → paste as the `GRORE_DEPLOY_KEY` repo secret.
- Public key (`cat grore_deploy_key.pub`) → append to `django@grore-images.com:~/.ssh/authorized_keys`.

The workflows also pin `grore-images.com`'s host key in `known_hosts` at connect time (fetched directly from the server) rather than trusting whatever answers on first connect.
