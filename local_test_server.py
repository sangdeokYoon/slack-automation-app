#!/usr/bin/env python3

import os
import sys
import logging


def main() -> int:
    import dotenv
    dotenv.load_dotenv()

    logging.basicConfig(level=logging.INFO)

    import app

    from slack_bolt.adapter.socket_mode import SocketModeHandler
    SocketModeHandler(app.app, os.environ.get("SLACK_APP_TOKEN")).start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
