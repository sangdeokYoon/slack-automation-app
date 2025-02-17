import os
import slack_bolt


# Initialization
app = slack_bolt.App(
    ssl_check_enabled=os.environ.get("TEST_SLACK_SSL_CHECK_ENABLED", "true") == "true",
    request_verification_enabled=os.environ.get("TEST_SLACK_REQUEST_VERIFICATION_ENABLED", "true") == "true",
)


__import__("app.listeners.events")
