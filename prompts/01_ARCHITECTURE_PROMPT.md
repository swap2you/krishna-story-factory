# 01 Architecture Prompt

Review the current repository and keep the architecture lightweight.

Required design:
- CLI-first local Python project.
- CSV queue and logs.
- Modular generators for text, audio, image, PDF, quality, and senders.
- Streamlit dashboard as optional UI only.
- Sender interface with WhatsApp Business Cloud as the preferred WhatsApp path.
- Telegram, Slack, Discord as fallback senders.
- Windows Task Scheduler for automation.

Reject overengineering:
- No FastAPI unless explicitly requested later.
- No React.
- No PostgreSQL.
- No Celery/Redis.
- No Docker unless explicitly requested later.
- No Notion.

Deliverable: update or create `docs/ARCHITECTURE.md` and confirm code structure matches it.
