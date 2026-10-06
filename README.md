# Personal AI Operator — Mobile-First Starter

This project is a starter implementation of a personal AI operator with three coordinated roles:

1. **Manager Agent** — receives your instruction, plans the work, delegates to specialists, and controls approvals.
2. **Opportunity Agent** — searches the live internet for legitimate earning/business opportunities and ranks them.
3. **Work Agent** — researches, drafts, organizes and prepares day-to-day work.

## Design goals

- Mobile-friendly web interface.
- A 4-hour active work window after you press **Start 4-hour session**.
- Research and drafting can happen without approval.
- Consequential actions require an explicit approval.
- The agent never promises guaranteed income.
- No automatic gambling, scams, spam, credential theft, deceptive activity, or unauthorized account access.
- Financial commitments, purchases, publishing, sending messages, applications, or account changes stay behind approval.

OpenAI's current agent stack supports web search, multi-agent orchestration, and human review/approval. See the official documentation:
- https://developers.openai.com/api/docs/guides/agents/sdk
- https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
- https://developers.openai.com/api/docs/guides/agents-api/tools/web-search

## What you need

- A computer/cloud server to run the backend (your phone can be the control panel).
- An OpenAI API key.
- Python 3.11+.

Your phone does **not** need to run the AI model itself.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Set your API key:
# Windows PowerShell:
$env:OPENAI_API_KEY="your-key"
# macOS/Linux:
export OPENAI_API_KEY="your-key"

uvicorn app:app --host 0.0.0.0 --port 8000
```

Then open `http://YOUR-SERVER-IP:8000` on your phone.

## Important production step

For real use, deploy this backend on a secure HTTPS host and put authentication in front of it. Do not expose an unauthenticated API to the public internet.

## Suggested first instructions

Try:

> Search for 10 legitimate online opportunities that could potentially generate income using a small starting budget. Rank them by startup cost, skill requirement, time to first customer, competition, and risk. Do not spend money or contact anyone. Prepare the top 3 action plans for my approval.

Then:

> Prepare everything needed to pursue opportunity #1, but stop before sending, buying, publishing, registering, or committing anything.

## Future upgrades

- Telegram/WhatsApp control channel.
- Gmail/Calendar integration.
- Google Drive/OneDrive file access.
- CRM and spreadsheet tools.
- Browser/computer-use actions behind approval.
- Persistent memory and opportunity database.
- Daily 4-hour operating schedule.
- Profit/expense tracking.
- Specialist agents for sales, research, documents, finance, travel, and administration.
