PRVRbot - Slackbot that does some helpful things for PRVR

```bash
docker run -d \
  --name=prvrbot \
  -e SLACK_APP_TOKEN= `APP_TOKEN` \
  -e SLACK_BOT_TOKEN= `BOT_TOKEN` \
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