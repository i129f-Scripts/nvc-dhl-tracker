import os

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "i129f.nvc_dhl_tracker",
    "admin_autoregister",
    "django_better_repr",
]

DISCORD_PY_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "SET_THIS")
DISCORD_PY_COMMAND_PREFEX = "?"
DISCORD_BOT_PATH = "i129f.nvc_dhl_tracker.bot:bot"
DISCORD_BOT_RECONNECT = True
DISCORD_BOT_LOG_LEVEL = "DEBUG"
DISCORD_BOT_PLUGINS = [
    "django_discord.py.example_bot.bot_plugins",
]
