# Signal-ATAK Bot

A bot that listens for Signal messages containing coordinates and target descriptions, 
converts them to Cursor on Target (CoT) XML, and sends them to a TAK server. 
Markers appear in real-time on ATAK/iTAK client maps.

**Message format:** `LAT LON target`
**Example:** `48.567123 37.87897 tank`

## Tools

- [**taky**](https://github.com/tkuester/taky) — lightweight TAK server in Python, speaks Cursor on Target (CoT) over SSL
- [**signal-cli**](https://github.com/AsamK/signal-cli) — command-line client for the Signal messenger, exposes a JSON-RPC daemon over TCP
- [**iTAK / ATAK**](https://tak.gov) — tactical map clients that display CoT markers in real-time

## Architecture
Three Docker services on a shared bridge network:

| Service      | Description                        | Port |
|--------------|------------------------------------|------|
| `taky`       | TAK server (taky v0.10)            | 8089 |
| `signal-cli` | Signal daemon (signal-cli v0.13.23)| 7583 |
| `bot`        | Python bot (main application)      | --   |

## Quick Start

### 1. Clone and install dependencies

```bash
git clone git@github.com:lazebnyi/signal-atak-bot.git
cd signal-atak-bot
cd bot
uv sync --group setup
```

### 2. Register Signal account

Before running the bot, install signal-cli and register a Signal account.

Install signal-cli:

```bash
# macOS
brew install signal-cli

# Linux (download from GitHub releases)
wget https://github.com/AsamK/signal-cli/releases/download/v0.13.23/signal-cli-0.13.23.tar.gz
tar xf signal-cli-0.13.23.tar.gz -C /opt
ln -s /opt/signal-cli-0.13.23/bin/signal-cli /usr/local/bin/signal-cli
```

Register a number:

```bash
# Register a new number (you'll receive an SMS verification code)
signal-cli -u +YOUR_NUMBER register

# Registration requires a captcha, open https://signalcaptchas.org/registration/generate.html
# in your browser, solve it, and copy the URL without signalcaptcha:// from the redirect, then:
signal-cli -u +YOUR_NUMBER register --captcha "signal-recaptcha-v2.6..."

# Verify with the code you received via SMS
signal-cli -u +YOUR_NUMBER verify CODE
```

The signal-cli data directory (default `~/.local/share/signal-cli`) is mounted into the Docker container,
so registration only needs to happen once on the host.

### 3. Configure environment

Copy the example and fill in your values:

```bash
cp .env.example .env
```

```env
SIGNAL_NUMBER=+38073_______        # Your registered Signal phone number
SIGNAL_CLI_HOST=signal-cli        # Docker service name (don't change for Docker)
SIGNAL_CLI_PORT=7583              # signal-cli daemon port

TAK_HOST=taky                     # Docker service name (don't change for Docker)
TAK_PORT=8089                     # TAK server CoT port

COT_STALE_MINUTES=1               # How long markers persist on the map

SIGNAL_DATA_PATH=~/.local/share/signal-cli  # Path to signal-cli data on host
```

### 4. Generate TAK certificates

Generate SSL certificates for the server, bot, and iTAK client:

```bash
# Initialize taky configuration
cd taky/config
taky --setup

# Generate server certificates
taky_cert -c ssl setup

# Generate bot client certificate
taky_cert -c ssl makeclient bot

# Generate iTAK client certificate package
taky_cert -c ssl makeclient iTAK
```

This generates `iTAK.zip` in `taky/config/` — you'll import it into iTAK in step 6.

Copy the bot PEM files to the `certs/` directory:

```bash
cp taky/config/bot-certs/bot-cert.pem certs/
cp taky/config/bot-certs/bot-key.pem certs/
cp taky/config/bot-certs/ca.pem certs/
```

### 5. Start all services

```bash
docker compose up -d
```

This builds and starts all three services. The bot waits for `taky` and `signal-cli` to pass their healthchecks before starting.

### 6. Connect iTAK / ATAK

Import the generated certificate package into your TAK client:

1. Copy `taky/config/iTAK.zip` to your device
2. In iTAK: **Settings → Servers → Import** → select `iTAK.zip`
3. Configure the server connection:
   - **Host:** your machine's IP (e.g. `192.168.2.33`)
   - **Port:** `8089`
   - **Protocol:** SSL
4. Verify the connection — the server should show as connected

After this, the bot is ready to accept messages. Send a Signal message to the bot's number:

```
48.567123 37.87897 tank
```

The marker should appear on your map within seconds.

### 7. Verify services

Check that all services are running:

```bash
docker compose ps
```

View bot logs:

```bash
docker compose logs -f bot
```

## Supported Target Types

| Category        | Keywords                                   |
|-----------------|--------------------------------------------|
| Ground vehicles | `tank`, `apc`, `truck`, `vehicle`          |
| Personnel       | `infantry`, `sniper`, `soldiers`           |
| Weapons         | `artillery`, `mortar`, `mlrs`, `sam`, `aa` |
| Air             | `helicopter`, `drone`, `jet`, `aircraft`   |
| Naval           | `ship`, `boat`                             |
| Structures      | `bunker`, `camp`, `hq`, `depot`            |

Unknown target types are mapped to a generic marker (`a-u-G`).

## Common Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Rebuild after code changes
docker compose up -d --build

# View logs (all services)
docker compose logs -f

# View logs (bot only)
docker compose logs -f bot
```

## Running Tests

```bash
cd bot

# Install dev dependencies (using uv)
uv sync

# Run tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Or with pip/pytest directly
pip install pytest
pytest
```

## Possible Next Steps

- Add message validation (reject malformed or suspicious input)
- Health endpoint for bot container monitoring
- Add CI/CD pipeline with automated tests
- Add altitude support (parse optional third coordinate)
- Validate sender: only accept messages from allowed Signal numbers
- Add persistent connection to TAK server instead of connect-per-message
- Reverse direction: forward TAK events back to Signal
