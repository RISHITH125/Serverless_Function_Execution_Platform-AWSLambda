
# 🐳 Installing & Running Non-Docker Containers (Using containerd + nerdctl)

This guide walks through installing and setting up `containerd`, `nerdctl`, CNI plugins, and BuildKit — the components needed to run containers without Docker.

---

## 1️⃣ Installing `containerd` (Container Runtime Engine)

```bash
# Install containerd
sudo apt-get install containerd

# Start the containerd service
sudo systemctl start containerd

# Stop containerd
sudo systemctl stop containerd

# (Optional) Disable containerd from auto-starting on boot
sudo systemctl disable containerd
```

---

## 2️⃣ Installing `nerdctl` (CLI to interact with containerd)

```bash
# Download nerdctl binary archive
curl -LO https://github.com/containerd/nerdctl/releases/download/v1.7.5/nerdctl-1.7.5-linux-amd64.tar.gz

# Extract the archive
tar -xzf nerdctl-1.7.5-linux-amd64.tar.gz

# Move binaries to your PATH
sudo mv nerdctl* /usr/local/bin/
```

> `nerdctl` acts like Docker CLI but talks to `containerd` underneath.

---

## 3️⃣ Installing CNI Plugins (for container networking)

```bash
# Create the directory nerdctl expects CNI plugins to live in
sudo mkdir -p /opt/cni/bin

# Download the CNI plugins release
curl -LO https://github.com/containernetworking/plugins/releases/download/v1.4.1/cni-plugins-linux-amd64-v1.4.1.tgz

# Extract plugins to correct path
sudo tar -xzvf cni-plugins-linux-amd64-v1.4.1.tgz -C /opt/cni/bin
```

> These plugins let `containerd` manage networking (bridge, NAT, etc).

---

## 4️⃣ Installing `iptables` (required for CNI networking)

```bash
# Update package list
sudo apt update

# Install iptables and related tools
sudo apt install iptables iproute2
```

> `iptables` is used under the hood by CNI to configure NAT, forwarding, and firewall rules.

---

## ✅ Quick Test: Run a Container!

```bash
sudo nerdctl run -it --rm alpine sh
```

> Launches an ephemeral Alpine shell. If this works, nerdctl & CNI setup is done 

---

## 5️⃣ Installing BuildKit (to build images from Dockerfiles)

```bash
# Set BuildKit version (check for latest at: https://docs.docker.com/build/buildkit/)
export BUILDKIT_VERSION=v0.22.0

# Download BuildKit archive
curl -LO https://github.com/moby/buildkit/releases/download/${BUILDKIT_VERSION}/buildkit-${BUILDKIT_VERSION}.linux-amd64.tar.gz

# Extract to /usr/local
sudo tar -C /usr/local -xzf buildkit-${BUILDKIT_VERSION}.linux-amd64.tar.gz
```

### 🔧 Run the BuildKit daemon

```bash
# Run in background
sudo buildkitd &
```

> ⚠️ The `buildkitd` daemon must be running for `nerdctl build` to work.

For production: Consider using `systemd` or `nohup` to run `buildkitd` persistently.

---
