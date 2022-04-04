PRVRbot - Slackbot that does some helpful things for PRVR

```bash
docker run -d \
  --name=prvrbot \
  -e SLACK_APP_TOKEN= `APP_TOKEN` \
  -e SLACK_BOT_TOKEN=cloudflare `BOT_TOKEN` \
  --restart unless-stopped \
  Docker.io/PRVRbot
```

## Parameters

Container images are configured using parameters passed at runtime (such as those above). These parameters are separated by a colon and indicate `<external>:<internal>` respectively. For example, `-p 8080:80` would expose port `80` from inside the container to be accessible from the host's IP on port `8080` outside the container.

|       Parameter       | Function                     |
|:---------------------:|------------------------------|
| `-e SLACK_APP_TOKEN=` | App token provided by Slack. |
| `-e SLACK_BOT_TOKEN`  | Bot token provided by Slack. |

## Building locally

If you want to make local modifications to these images for development purposes or just to customize the logic:

```bash
git clone https://github.com/FastQuack/PRVRbot.git
cd PRVRbot-main
docker build -t prvrbot:latest .
```

## Versions

* **04.02.22:** - Removed unused files.
* **04.02.22:** - Initial release.