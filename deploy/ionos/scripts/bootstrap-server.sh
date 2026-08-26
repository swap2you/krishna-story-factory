#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root from the IONOS console or an initial root SSH session." >&2
  exit 1
fi

DEPLOY_USER="${DEPLOY_USER:-bhava-deploy}"
DEPLOY_PUBLIC_KEY="${DEPLOY_PUBLIC_KEY:-}"

if [[ -z "${DEPLOY_PUBLIC_KEY}" ]]; then
  echo "DEPLOY_PUBLIC_KEY is required. Use a dedicated SSH public key." >&2
  exit 1
fi

. /etc/os-release
if [[ "${ID}" != "ubuntu" || "${VERSION_ID}" != "24.04" ]]; then
  echo "Expected Ubuntu 24.04 LTS. Found ${PRETTY_NAME:-unknown}." >&2
  exit 1
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates curl gnupg jq unzip rsync ufw fail2ban unattended-upgrades

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

cat >/etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${UBUNTU_CODENAME}
Components: stable
Signed-By: /etc/apt/keyrings/docker.gpg
EOF

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

if ! id "${DEPLOY_USER}" >/dev/null 2>&1; then
  adduser --disabled-password --gecos "" "${DEPLOY_USER}"
fi
usermod -aG docker "${DEPLOY_USER}"

install -d -m 0700 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" "/home/${DEPLOY_USER}/.ssh"
printf '%s\n' "${DEPLOY_PUBLIC_KEY}" \
  >"/home/${DEPLOY_USER}/.ssh/authorized_keys"
chown "${DEPLOY_USER}:${DEPLOY_USER}" "/home/${DEPLOY_USER}/.ssh/authorized_keys"
chmod 0600 "/home/${DEPLOY_USER}/.ssh/authorized_keys"

cat >/etc/ssh/sshd_config.d/99-bhava-hardening.conf <<EOF
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AllowUsers ${DEPLOY_USER}
MaxAuthTries 3
LoginGraceTime 30
X11Forwarding no
AllowTcpForwarding no
PermitTunnel no
ClientAliveInterval 300
ClientAliveCountMax 2
EOF
sshd -t
systemctl reload ssh

cat >/etc/fail2ban/jail.d/sshd.local <<EOF
[sshd]
enabled = true
bantime = 1h
findtime = 10m
maxretry = 5
EOF
systemctl enable --now fail2ban

ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

install -d -m 0750 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" \
  /opt/bhava \
  /opt/bhava/config \
  /opt/bhava/incoming \
  /opt/bhava/releases \
  /opt/bhava/releases/production \
  /opt/bhava/releases/staging \
  /opt/bhava/content \
  /opt/bhava/content/releases \
  /opt/bhava/content/releases/vani-kb-dictations \
  /opt/bhava/backups
# install -d leaves intermediate parents root-owned; normalize the tree.
chown -R "${DEPLOY_USER}:${DEPLOY_USER}" /opt/bhava

cat >/etc/docker/daemon.json <<EOF
{
  "live-restore": true,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  },
  "no-new-privileges": true
}
EOF
systemctl enable docker
systemctl restart docker

dpkg-reconfigure -f noninteractive unattended-upgrades

echo
echo "Bootstrap complete."
echo "Before closing this session:"
echo "1. Verify login as ${DEPLOY_USER} using the dedicated key."
echo "2. In IONOS firewall, leave only TCP 22, 80 and 443."
echo "3. Remove default 8443 and 8447 rules because Plesk is not used."
echo "4. Record the SSH host-key fingerprint from the IONOS console."
echo "5. Do not enable automatic reboot."
