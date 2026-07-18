# igGraber (InstaGraber)

Telegram bot that pings you when a watched Instagram account posts a new story. The watched account is changeable at any time with a Telegram command.

- Watched account + poll interval live in `config.json`; change the account live with `/watch <username or profile URL>`.
- Polls faster during the day (`poll_interval_minutes`) and slower overnight, 00:00-06:00 (`night_poll_interval_minutes`) — quieter hours, less load on the login account.
- Requires a **logged-in Instagram session** (stories are not visible anonymously). Use a spare account — automated polling is against Instagram's ToS and aggressive use can get the login account blocked. Keep the interval modest; see `PROJECT_LOG.md` for a real incident where 1-minute polling got the account rate-limited within ~7 minutes.

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` → `.env` and fill it in. **Never commit `.env`.**
3. Telegram: talk to **@BotFather** → `/newbot` → put the token in `.env`. Then open your new bot and press **Start** once.
4. Instagram: `instaloader --login <your_secondary_account>` (interactive login, saves a reusable session).
5. `python bot.py` (or see **Run 24/7** below)

## Commands (from your Telegram chat with the bot)
- `/watch <username or instagram.com profile URL>` — switch the watched account
- `/status` — current target, poll intervals, sync state
- `/check` — poll immediately instead of waiting
- `/help` — list commands

## Run 24/7
A Windows Task Scheduler task named **InstaGraber** auto-starts the bot at logon (`run_bot.bat` → `pythonw bot.py`, windowless — all output goes to `logs/bot.log`), restarts it automatically up to 5× if it crashes, and has no execution time limit.
- Start now: `Start-ScheduledTask -TaskName InstaGraber`
- Stop: `Stop-ScheduledTask -TaskName InstaGraber`
- Remove: `Unregister-ScheduledTask -TaskName InstaGraber`
- Re-create it: see `PROJECT_LOG.md` (Session 3) for the exact `Register-ScheduledTask` command.

## Project docs
- [ROADMAP.md](ROADMAP.md) — build plan and progress
- [PROJECT_LOG.md](PROJECT_LOG.md) — session/decision log
- [CLAUDE.md](CLAUDE.md) — working rules for AI coding sessions
