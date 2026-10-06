# Mobile setup

The easiest first version is a small web app.

1. Put the project on a cloud server.
2. Set OPENAI_API_KEY as a server-side secret.
3. Run:
   uvicorn app:app --host 0.0.0.0 --port 8000
4. Put HTTPS/authentication in front of it.
5. Open the web address on your Android phone.
6. Press "Start 4-hour session".
7. Give the Manager instructions.
8. Approve or reject consequential actions.

Do not put your OpenAI API key inside the mobile browser JavaScript.
