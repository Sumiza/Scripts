#!/bin/sh

echo "Downloading cloudflared..."
ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then ARCH="amd64";
    elif [ "$ARCH" = "aarch64" ]; then ARCH="arm64";
    elif [ "$ARCH" = "armv7l" ]; then ARCH="arm";
    elif [ "$ARCH" = "armv6l" ]; then ARCH="armhf";
    elif [ "$ARCH" = "i386" ] || [ "$ARCH" = "i686" ]; then ARCH="386";
fi
wget -O /cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-"${ARCH}"
chmod +x /cloudflared

echo "Waiting for wget to return HTTP 200 from $URL_BEFORE_START"

while true; do
    if wget --spider --quiet "$URL_BEFORE_START"; then
        echo "Found $URL_BEFORE_START starting..."
        break
    else
        echo "Can't find server $URL_BEFORE_START... Retrying in 2 seconds."
        sleep 2
    fi
done

echo "Starting tunnel"
# using $TUNNEL_TOKEN otherwise use --token 3qh43qh43t4tt4er3wqt
/cloudflared tunnel run
