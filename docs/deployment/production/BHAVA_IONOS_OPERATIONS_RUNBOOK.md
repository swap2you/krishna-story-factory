# Bhāva IONOS Production Operations Runbook

## Normal release

1. Feature PR into `develop`.
2. Production CI passes.
3. Automatic staging deployment.
4. Staging UAT.
5. Release PR from `develop` into `main`.
6. Run `Deploy Production` from GitHub Actions.
7. Approve the protected production environment.
8. Verify deployed SHA and smoke evidence.

## Content release

Code and content are separate.

A content release must:

- contain exact-eight Stories 001 through the approved maximum;
- include the generated SHA-256 manifest;
- be uploaded as an immutable GitHub Release asset;
- be installed into a versioned VPS directory;
- switch the `current` symlink only after validation.

## Update window

Monthly, or earlier for critical security issues:

- test updated base images in staging;
- run dependency and container scans;
- apply Ubuntu security updates;
- review `/var/run/reboot-required`;
- schedule a reboot only with a tested rollback and maintenance notice.

## Logs

- Caddy access logs: named Docker volume `caddy_logs`
- Docker logs: rotated at 10 MB, five files
- Never log secrets, cookies, private file paths or email body content.

## Backup

Run `deploy/ionos/scripts/backup.sh` daily.

The Git repository and GitHub content release are the authoritative off-site backups
for code and immutable public assets. The local VPS backup is operational convenience,
not the only copy.

## Incident sequence

1. Confirm health and deployed SHA.
2. Check Caddy, web and API container status.
3. Check disk, memory and inode pressure.
4. If the last deployment caused the incident, rollback.
5. If TLS failed, inspect DNS and Caddy logs; do not paste private keys.
6. If compromise is suspected, isolate the VPS in IONOS firewall, preserve evidence,
   rotate deployment keys and rebuild from a clean image.

## Two-gigabyte VPS memory policy

Staging is an on-demand validation environment. It may run beside production for
short UAT windows, but the production deployment stops staging automatically.
Do not keep both environments active indefinitely on the entry-level VPS.

Escalate the VPS size if production plus temporary staging cannot maintain at
least 25–30% free memory during audio playback and page-navigation tests.
