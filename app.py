import os
import time
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Personal AI Operator")
client = OpenAI()

# In-memory state for the starter. Replace with a database in production.
sessions: dict[str, dict[str, Any]] = {}
approvals: dict[str, dict[str, Any]] = {}

SESSION_SECONDS = 4 * 60 * 60

MANAGER_PROMPT = """
You are the user's Personal AI Manager.

Your mission:
- Help the user discover legitimate ways to earn value/income.
- Help with ordinary day-to-day digital work.
- Coordinate two specialists: Opportunity Agent and Work Agent.
- Search the live internet when current information is needed.
- Never claim guaranteed income.
- Prefer legal, ethical, realistic opportunities.
- Be skeptical of scams, fake jobs, get-rich-quick claims, pyramid schemes,
  suspicious investment schemes, credential requests, and requests to bypass rules.

Four-hour operating model:
- The user can give instructions and approvals during a 4-hour active session.
- During the session, research, comparison, planning, drafting and preparation
  may proceed without approval.
- Any consequential external action requires approval.

Approval-required actions:
- Spending or transferring money.
- Buying something.
- Sending an email/message to an external person.
- Publishing or posting content.
- Applying for a job/program/business opportunity.
- Creating or changing an account.
- Signing a contract or accepting binding terms.
- Sharing private credentials or sensitive personal data.
- Any action with material legal, financial, reputational, or security consequences.

When approval is needed, create a clear proposal with:
1. What will happen
2. Why it is useful
3. Cost
4. Risk
5. Exact external action
Then stop and wait for the user's approval.

For normal research and preparation, return concise results with sources and a next action.
"""

OPPORTUNITY_PROMPT = """
You are the Opportunity Agent.

Find legitimate opportunities on the public internet that could reasonably
help the user earn income or create useful economic value.

For each opportunity:
- Name
- What the user would actually do
- Customer/buyer
- Revenue mechanism
- Estimated startup cost
- Skills needed
- Expected time to first result (estimate, not promise)
- Competition level
- Key risks
- Why it may fit
- Source URLs

Prioritize opportunities that can be started by one person, have low or moderate
startup cost, and do not require deceptive or prohibited activity.

Never fabricate listings, customers, earnings, or requirements.
"""

WORK_PROMPT = """
You are the Work Agent.

Help the user complete ordinary digital work:
- Research
- Writing and rewriting
- Reports
- Spreadsheet planning
- Checklists
- Business proposals
- Marketing drafts
- Document preparation
- Scheduling plans
- Comparison tables

You may prepare drafts and plans without approval.
Do not send, publish, purchase, register, apply, or make external commitments.
If such an action is requested, return an approval proposal for the Manager.
"""

class StartResponse(BaseModel):
    session_id: str
    expires_at: int

class TaskRequest(BaseModel):
    session_id: str
    instruction: str

class ApprovalRequest(BaseModel):
    approval_id: str
    decision: str  # approve / reject

def require_session(session_id: str):
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(404, "Session not found. Start a new 4-hour session.")
    if time.time() >= s["expires_at"]:
        raise HTTPException(403, "The 4-hour session has expired. Start a new session.")
    return s

def run_specialist(prompt: str, instruction: str) -> str:
    response = client.responses.create(
        model="gpt-5.5",
        instructions=prompt,
        tools=[{
            "type": "web_search",
            "external_web_access": True,
        }],
        input=instruction,
    )
    return response.output_text

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>My AI Operator</title>
<style>
body{font-family:system-ui;margin:0;background:#f4f6f8;color:#111}
main{max-width:720px;margin:auto;padding:18px}
.card{background:white;border-radius:16px;padding:18px;margin:12px 0;box-shadow:0 2px 12px #0001}
button{border:0;border-radius:12px;padding:13px 16px;font-weight:700;margin:4px}
input,textarea{width:100%;box-sizing:border-box;border:1px solid #ddd;border-radius:12px;padding:12px;font-size:16px}
textarea{min-height:120px}
#status{white-space:pre-wrap}
.small{color:#666;font-size:14px}
.approve{background:#111;color:white}
</style>
</head>
<body>
<main>
<h1>🤖 My AI Operator</h1>
<div class="card">
<h3>1. Start your 4-hour work session</h3>
<button class="approve" onclick="startSession()">Start 4-hour session</button>
<div id="timer" class="small"></div>
</div>
<div class="card">
<h3>2. Give your instruction</h3>
<textarea id="instruction" placeholder="Example: Find 10 realistic online earning opportunities for me and rank them by cost, effort, risk and potential."></textarea>
<button class="approve" onclick="sendTask()">Send to Manager</button>
</div>
<div class="card">
<h3>Result / approval requests</h3>
<div id="status">No active session.</div>
</div>
<script>
let sid = localStorage.getItem("ai_session");
let expires = Number(localStorage.getItem("ai_expires")||0);
function renderTimer(){
  if(!expires){return}
  const left=Math.max(0,expires-Date.now()/1000);
  if(left<=0){document.getElementById('timer').innerText='Session expired.';return}
  const h=Math.floor(left/3600),m=Math.floor(left%3600/60),s=Math.floor(left%60);
  document.getElementById('timer').innerText=`Active: ${h}h ${m}m ${s}s remaining`;
}
setInterval(renderTimer,1000); renderTimer();

async function startSession(){
 const r=await fetch('/session/start',{method:'POST'});
 const d=await r.json(); sid=d.session_id; expires=d.expires_at;
 localStorage.setItem("ai_session",sid); localStorage.setItem("ai_expires",expires);
 document.getElementById('status').innerText='4-hour session started.';
}
async function sendTask(){
 if(!sid){alert('Start a session first.');return}
 const instruction=document.getElementById('instruction').value;
 document.getElementById('status').innerText='Working...';
 const r=await fetch('/task',{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify({session_id:sid,instruction})});
 const d=await r.json();
 document.getElementById('status').innerText=d.result || JSON.stringify(d,null,2);
}
</script>
</main>
</body>
</html>
""")

@app.post("/session/start", response_model=StartResponse)
def start_session():
    sid = str(uuid.uuid4())
    expires = int(time.time() + SESSION_SECONDS)
    sessions[sid] = {"started_at": int(time.time()), "expires_at": expires}
    return StartResponse(session_id=sid, expires_at=expires)

@app.post("/task")
def task(req: TaskRequest):
    require_session(req.session_id)

    # First classify the user's instruction with the Manager.
    classification = client.responses.create(
        model="gpt-5.5",
        instructions=MANAGER_PROMPT + """
Return JSON with:
{
 "route": "opportunity" | "work" | "both" | "manager",
 "needs_approval_now": true | false,
 "approval_reason": "...",
 "task_for_specialist": "..."
}
Do not request approval merely for research, planning or drafting.
""",
        input=req.instruction,
    )

    # Keep this starter simple: ask the manager for a structured routing decision.
    raw = classification.output_text
    route = "manager"
    if "opportunity" in raw.lower() and "work" not in raw.lower():
        route = "opportunity"
    elif "work" in raw.lower() and "opportunity" not in raw.lower():
        route = "work"
    elif "opportunity" in raw.lower() and "work" in raw.lower():
        route = "both"

    results = []

    if route in ("opportunity", "both"):
        results.append("OPPORTUNITY AGENT:\n" + run_specialist(OPPORTUNITY_PROMPT, req.instruction))

    if route in ("work", "both"):
        results.append("WORK AGENT:\n" + run_specialist(WORK_PROMPT, req.instruction))

    if not results:
        results.append("MANAGER:\n" + client.responses.create(
            model="gpt-5.5",
            instructions=MANAGER_PROMPT,
            tools=[{"type":"web_search","external_web_access":True}],
            input=req.instruction,
        ).output_text)

    final = "\n\n".join(results)

    # A conservative keyword gate for this starter. Production should use
    # structured tool approvals rather than text matching.
    risky_words = [
        "send", "publish", "purchase", "buy", "pay", "transfer",
        "apply", "register", "sign", "post", "contact", "message"
    ]
    if any(w in req.instruction.lower() for w in risky_words):
        aid = str(uuid.uuid4())
        approvals[aid] = {
            "session_id": req.session_id,
            "instruction": req.instruction,
            "status": "pending",
            "created_at": int(time.time())
        }
        final += (
            "\n\n⚠️ APPROVAL REQUIRED\n"
            f"Approval ID: {aid}\n"
            "The requested task may create an external or consequential action. "
            "Review it before anything is sent, purchased, published, registered, "
            "or otherwise committed."
            f"\nApprove: POST /approval/{aid}/approve\n"
            f"Reject: POST /approval/{aid}/reject"
        )

    return {"result": final}

@app.post("/approval/{approval_id}/{decision}")
def approval(approval_id: str, decision: str):
    if approval_id not in approvals:
        raise HTTPException(404, "Approval not found")
    if decision not in ("approve", "reject"):
        raise HTTPException(400, "Decision must be approve or reject")
    approvals[approval_id]["status"] = decision
    return {
        "approval_id": approval_id,
        "status": decision,
        "message": "Approval recorded. A production implementation should resume the same run here."
    }
