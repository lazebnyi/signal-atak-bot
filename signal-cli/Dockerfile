FROM eclipse-temurin:21-jre

RUN apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/*

ARG SIGNAL_CLI_VERSION=0.13.23
RUN wget -q "https://github.com/AsamK/signal-cli/releases/download/v${SIGNAL_CLI_VERSION}/signal-cli-${SIGNAL_CLI_VERSION}.tar.gz" \
    && tar xf "signal-cli-${SIGNAL_CLI_VERSION}.tar.gz" -C /opt \
    && ln -s "/opt/signal-cli-${SIGNAL_CLI_VERSION}/bin/signal-cli" /usr/local/bin/signal-cli \
    && rm "signal-cli-${SIGNAL_CLI_VERSION}.tar.gz"

ENTRYPOINT ["signal-cli"]