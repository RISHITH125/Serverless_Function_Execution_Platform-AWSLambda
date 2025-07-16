###### **1)downloading containerd: (The container runtime engine)**

*# sudo apt-get install containerd*

**starting containerd:**

*# sudo systemctl start containerd*

<b>stopping containerd:</b>

*# sudo systemctl stop containerd*

<b>diasabling it from the starting on boot(optional)</b>

*# sudo systemctl disable containerd*





###### <b>2)installing nerctl binaries: (CLI to talk with containerd) </b>

*# Step 1: Download the archive (no extraction yet)*

*curl -LO https://github.com/containerd/nerdctl/releases/download/v1.7.5/nerdctl-1.7.5-linux-amd64.tar.gz*



*# Step 2: Extract it to a local folder*

*tar -xzf nerdctl-1.7.5-linux-amd64.tar.gz*



*# Step 3: Move the binaries to /usr/local/bin with sudo*

*sudo mv nerdctl\* /usr/local/bin/*



###### <b>3)installing CNI plugins (Container Network Interface) : (Lets containerd setup networking)</b>

*# Step 1: Make the directory nerdctl expects*

*sudo mkdir -p /opt/cni/bin*



*# Step 2: Download the CNI plugins release*

*curl -LO https://github.com/containernetworking/plugins/releases/download/v1.4.1/cni-plugins-linux-amd64-v1.4.1.tgz*



*# Step 3: Extract it into the correct path*

*sudo tar -xzvf cni-plugins-linux-amd64-v1.4.1.tgz -C /opt/cni/bin*


<b>4)installing iptables : (Helps the CNI to setup networking by configuring the firewall rules and NAT)</b>
---

*# sudo apt update*

*# sudo apt install iptables*



*for covering the bases*

*# sudo apt install iptables iproute2*





###### <b>Now try running </b>

\# sudo nerdctl run -it --rm alpine sh (opens a minimal alpine bash shell)



**5)installing BuildKit (required for nerdctl builds) : (this helps building images from normal Dockerfile)**
---

*# sudo apt update*

*# export BUILDKIT\_VERSION=v0.22.0 (check* [*https://docs.docker.com/build/buildkit/*](https://docs.docker.com/build/buildkit/) *this docks to get the latest release )*

*# curl -LO https://github.com/moby/buildkit/releases/download/${BUILDKIT\_VERSION}/buildkit-${BUILDKIT\_VERSION}.linux-amd64.tar.gz*

*# sudo tar -C /usr/local -xzf buildkit-${BUILDKIT\_VERSION}.linux-amd64.tar.gz

running the daemon:-*

*# sudo buildkitd \& (this needs to be running in the background for the image to built using dockerfile)*








