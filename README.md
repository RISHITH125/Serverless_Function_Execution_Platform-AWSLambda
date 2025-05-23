# Serverless_Function_Execution_Platform-AWSLambda
This project tries to immetate AWS's lambda service on a small scale using docker containers.

## Requirements
- Host Linux operating system (for gvisor virtualization)
- Docker 

Can also run on windows but the gvisor virtualization is not natively supported

## To run backend server
change directory to /backend
```bash
uvicorn app.main:app --reload --port 8000
```
## To run frontend
change directory to /frontend
```bash
npm run dev
```


## To Install gVisor on Debian/Ubuntu/Mint

```bash
sudo apt-get update && \
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg
```

```bash
curl -fsSL https://gvisor.dev/archive.key | sudo gpg --dearmor -o /usr/share/keyrings/gvisor-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gvisor-archive-keyring.gpg] https://storage.googleapis.com/gvisor/releases release main" | sudo tee /etc/apt/sources.list.d/gvisor.list > /dev/null
```

```bash
sudo apt-get update && sudo apt-get install -y runsc
```

Then add the following to `/etc/docker/daemon.json`:

```json
{
  "runtimes": {
    "runsc": {
      "path": "runsc"
    }
  }
}
```

Then restart Docker:

```bash
sudo systemctl restart docker
```