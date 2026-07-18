import functools
import json
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import instaloader
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from ig_watcher import get_active_stories, load_session

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
STATE_PATH = BASE_DIR / "state.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("instagraber")

load_dotenv()
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])
IG_LOGIN_USERNAME = os.environ["IG_LOGIN_USERNAME"]

_ig_session = None


def get_ig_session():
    global _ig_session
    if _ig_session is None:
        _ig_session = load_session(IG_LOGIN_USERNAME)
    return _ig_session


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"target_username": None, "notified_ids": []}


def save_state(state: dict) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


async def send_story_notification(bot: Bot, target: str, item: dict):
    caption = f"New story from @{target}"
    try:
        if item["is_video"]:
            return await bot.send_video(chat_id=TELEGRAM_CHAT_ID, video=item["url"], caption=caption)
        return await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=item["url"], caption=caption)
    except Exception:
        # Instagram's CDN occasionally rejects Telegram's server-side fetch (hotlink block);
        # fall back to downloading with our authenticated session and uploading the bytes.
        logger.warning("Direct media send failed for story %s, retrying via download", item["id"])
        data = get_ig_session().context._session.get(item["url"]).content
        if item["is_video"]:
            return await bot.send_video(chat_id=TELEGRAM_CHAT_ID, video=data, caption=caption)
        return await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=data, caption=caption)


async def poll_once(bot: Bot) -> dict:
    """Fetch, diff, and notify. Returns {baselined, active_count, notified_count}."""
    config = load_config()
    target = config["target_username"]
    state = load_state()

    try:
        items = get_active_stories(get_ig_session(), target)
    except Exception:
        logger.exception("Failed to fetch stories for @%s", target)
        return {"baselined": False, "active_count": 0, "notified_count": 0, "error": True}

    current_ids = {item["id"] for item in items}

    if state.get("target_username") != target:
        # New target (first run, or switched via /watch) — baseline silently so
        # pre-existing stories don't get reported as "new".
        logger.info("Baselining @%s with %d existing stor%s (no notification)",
                    target, len(items), "y" if len(items) == 1 else "ies")
        save_state({"target_username": target, "notified_ids": list(current_ids)})
        return {"baselined": True, "active_count": len(items), "notified_count": 0, "error": False}

    notified_ids = set(state.get("notified_ids", []))
    new_items = [item for item in items if item["id"] not in notified_ids]

    for item in new_items:
        msg = await send_story_notification(bot, target, item)
        logger.info("Notified about story %s from @%s (message_id=%s)", item["id"], target, msg.message_id)

    save_state({"target_username": target, "notified_ids": list(current_ids | notified_ids)})
    return {"baselined": False, "active_count": len(items), "notified_count": len(new_items), "error": False}


async def scheduled_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
    await poll_once(context.bot)


def parse_ig_username(raw: str) -> str:
    """Accept a bare username (with optional @) or an instagram.com profile URL."""
    raw = raw.strip()
    if "instagram.com" in raw:
        if "://" not in raw:
            raw = "https://" + raw
        segments = [s for s in urlparse(raw).path.split("/") if s]
        return segments[0] if segments else ""
    return raw.lstrip("@")


def owner_only(handler):
    @functools.wraps(handler)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != TELEGRAM_CHAT_ID:
            return
        return await handler(update, context)
    return wrapper


@owner_only
async def cmd_watch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /watch <username or instagram.com profile URL>")
        return
    username = parse_ig_username(context.args[0])
    if not username:
        logger.info("/watch: couldn't parse a username from %r", context.args[0])
        await update.message.reply_text("Couldn't find a username in that link. Usage: /watch <username or instagram.com profile URL>")
        return

    try:
        instaloader.Profile.from_username(get_ig_session().context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        logger.info("/watch: @%s doesn't exist", username)
        await update.message.reply_text(f"@{username} doesn't seem to exist on Instagram.")
        return

    logger.info("/watch: switching target to @%s", username)
    config = load_config()
    config["target_username"] = username
    save_config(config)

    result = await poll_once(context.bot)
    await update.message.reply_text(
        f"Now watching @{username} ({result['active_count']} active story item(s) right now — "
        f"not notifying for those, only new ones from here on)."
    )


@owner_only
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config = load_config()
    state = load_state()
    in_sync = state.get("target_username") == config["target_username"]
    await update.message.reply_text(
        f"Watching: @{config['target_username']}\n"
        f"Poll interval: {config['poll_interval_minutes']} min\n"
        f"State: {'in sync' if in_sync else 'will baseline on next poll'}\n"
        f"Known story ids: {len(state.get('notified_ids', []))}"
    )


@owner_only
async def cmd_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = await poll_once(context.bot)
    if result["error"]:
        await update.message.reply_text("Check failed — see logs.")
    elif result["baselined"]:
        await update.message.reply_text(f"Baselined ({result['active_count']} existing story item(s), not notified).")
    elif result["notified_count"]:
        await update.message.reply_text(f"Sent {result['notified_count']} new notification(s).")
    else:
        await update.message.reply_text("Checked — nothing new.")


@owner_only
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/watch <username or instagram.com profile URL> — switch the watched Instagram account\n"
        "/status — show current target, interval, state\n"
        "/check — poll right now instead of waiting\n"
        "/help — this message"
    )


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("watch", cmd_watch))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("check", cmd_check))
    application.add_handler(CommandHandler("help", cmd_help))

    config = load_config()
    interval_seconds = config["poll_interval_minutes"] * 60
    application.job_queue.run_repeating(scheduled_poll, interval=interval_seconds, first=5)

    logger.info("InstaGraber started, watching @%s every %d min",
                config["target_username"], config["poll_interval_minutes"])
    application.run_polling()


if __name__ == "__main__":
    main()
