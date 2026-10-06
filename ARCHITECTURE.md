# Agent architecture

```text
                         YOU (mobile)
                            |
                     4-hour work session
                            |
                            v
                    +----------------+
                    |  MANAGER AGENT |
                    +----------------+
                      /            \
                     /              \
                    v                v
        +------------------+   +----------------+
        | OPPORTUNITY      |   | WORK AGENT     |
        | AGENT            |   |                |
        | web research     |   | daily work     |
        | opportunity rank |   | drafting       |
        | risk screening   |   | research       |
        +------------------+   +----------------+
                    \              /
                     \            /
                      v          v
                    approval gate
                          |
                +---------+---------+
                |                   |
             approve             reject
                |                   |
                v                   v
       external action        stop / revise
```

## Approval policy

No approval needed:
- Search
- Research
- Compare
- Summarize
- Draft
- Calculate
- Prepare a proposal
- Prepare a message but do not send it

Approval needed:
- Spend money
- Transfer money
- Purchase
- Send messages/emails
- Publish
- Apply
- Register an account
- Sign/accept binding terms
- Change account settings
- Share sensitive information
- Any material legal/financial/reputational action

## 4-hour operating model

The user starts a session from the phone. The session remains active for four hours.
The production version should store state in a database so the user can close the
phone and return later without losing work.

## Recommended production upgrades

1. Authentication
2. PostgreSQL/SQLite state store
3. Structured approval tool with resumable run state
4. Telegram/WhatsApp front end
5. Gmail and calendar integration
6. Browser/computer-use agent for approved website actions
7. Opportunity database and deduplication
8. Daily report
9. Audit log
10. Budget and action limits

The OpenAI Agents SDK supports tools, agents-as-tools/handoffs, sessions,
guardrails, tracing and human-in-the-loop workflows.
