import re
from logging import Logger

from app import app
from slack_bolt import BoltContext, Say


@app.message(re.compile("(hi|hello|hey)"))
def sample_message_callback(context: BoltContext, say: Say, logger: Logger):
    try:
        greeting = context["matches"][0]
        say(f"{greeting}, how are you?")
    except Exception as e:
        logger.error(e)
