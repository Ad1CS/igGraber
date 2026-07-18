import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application, ContextTypes

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


async def poll_once(bot: Bot) -> None:
    config = load_config()
    target = config["target_username"]
    state = load_state()

    try:
        items = get_active_stories(get_ig_session(), target)
    except Exception:
        logger.exception("Failed to fetch stories for @%s", target)
        return

    current_ids = {item["id"] for item in items}

    if state.get("target_username") != target:
        # New target (first run, or switched via /watch) — baseline silently so
        # pre-existing stories don't get reported as "new".
        logger.info("Baselining @%s with %d existing stor%s (no notification)",
                    target, len(items), "y" if len(items) == 1 else "ies")
        save_state({"target_username": target, "notified_ids": list(current_ids)})
        return

    notified_ids = set(state.get("notified_ids", []))
    new_items = [item for item in items if item["id"] not in notified_ids]

    for item in new_items:
        msg = await send_story_notification(bot, target, item)
        logger.info("Notified about story %s from @%s (message_id=%s)", item["id"], target, msg.message_id)

    save_state({"target_username": target, "notified_ids": list(current_ids | notified_ids)})


async def scheduled_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
    await poll_once(context.bot)


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    config = load_config()
    interval_seconds = config["poll_interval_minutes"] * 60
    application.job_queue.run_repeating(scheduled_poll, interval=interval_seconds, first=5)

    logger.info("InstaGraber started, watching @%s every %d min",
                config["target_username"], config["poll_interval_minutes"])
    application.run_polling()


if __name__ == "__main__":
    main()
