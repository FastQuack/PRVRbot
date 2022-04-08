#  Base image
FROM python:3.10.3-slim-buster
RUN pip install --upgrade pip

# Create user
RUN adduser --disabled-login prvrbot
USER prvrbot
WORKDIR /home/prvrbot

# Install dependencies
COPY --chown=prvrbot:prvrbot requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

ENV PATH="/home/prvrbot/.local/bin:${PATH}"

COPY --chown=prvrbot:prvrbot . .

CMD ["python3", "main.py"]
