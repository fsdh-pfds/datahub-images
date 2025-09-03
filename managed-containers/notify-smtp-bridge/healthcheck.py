import socket
import sys
import os

SMTP_HOST_HEALTHCHECK = os.getenv("SMTP_HOST_HEALTHCHECK", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", 2525))

try:
    with socket.create_connection((SMTP_HOST_HEALTHCHECK, SMTP_PORT), timeout=3) as sock:
        banner = sock.recv(1024).decode(errors="ignore")
        if banner.startswith("220"):
            print("SMTP server is healthy")
            sys.exit(0)  # healthy
        else:
            print(f"SMTP server is unhealthy: unexpected banner - {banner}")
            sys.exit(1)  # unhealthy
except Exception as e:
    print(f"SMTP server is unhealthy: {e}")
    sys.exit(1)
