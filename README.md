PRVRbot - Slackbot that does some helpful things for PRVR

```bash
docker run -d \
  --name=prvrbot \
  -v /path/to/data:/config \
  --restart unless-stopped \
  Docker.io/PRVRbot
```

## Building locally

If you want to make local modifications to these images for development purposes or just to customize the logic:

```bash
git clone https://github.com/FastQuack/PRVRbot.git
cd PRVRbot
docker build -t prvrbot:latest .
docker run -dit \
  --name=prvrbot \
  --restart unless-stopped \
  prvrbot
```