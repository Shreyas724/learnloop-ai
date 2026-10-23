# LearnLoop AI V2 — beginner setup

## Windows (VS Code)
1. Unzip this folder and open `learnloop-ai-v2` in VS Code.
2. Make sure Python 3.11+ is installed. Open the VS Code terminal and run `py -3 --version`.
3. Double-click `start_windows.bat`. It installs dependencies and starts the server.
4. Open http://localhost:8501 if your browser does not open automatically.
5. Try Demo mode first. It needs no API key.

## Enable Gemini AI (optional)
1. Go to https://aistudio.google.com/apikey and check if the free tier is available for your account and region. An account/API key may have age restrictions; follow the provider's rules and do not bypass them.
2. In the project, create `.streamlit/secrets.toml` (copy `.streamlit/secrets.toml.example`).
3. Replace `PASTE_YOUR_KEY_HERE` with your key; save the file. Do NOT paste your key into chat or GitHub.
4. Restart the app. Choose `Gemini AI (API key required)` in the sidebar.
5. If you see a quota/model error, verify your API access, free-tier quota, and available models. The model used is `gemini-2.5-flash` in app.py; change it if your account requires another supported model.

**Note:** Free-tier availability and rate limits vary and can change. Do not enable billing unless you understand the charges and have the required authorization.

## Mac/Linux
Run `sh start_mac_linux.sh` from a terminal inside the project folder.

## Deploy to Streamlit Community Cloud
1. Upload the files to a GitHub repository, excluding `secrets.toml`.
2. Visit https://share.streamlit.io and deploy the repository with entry point `app.py`.
3. In Streamlit app settings > Secrets, add `GEMINI_API_KEY = "your-key"` if using AI mode.
4. Test your public URL. The app defaults to Demo mode for safe first-run behavior.

## Troubleshooting
- `py` not found: install Python from python.org and enable the launcher, or use `python -m pip install -r requirements.txt` then `python -m streamlit run app.py`.
- `ModuleNotFoundError`: install requirements in the same Python interpreter running Streamlit.
- Port busy: run `python -m streamlit run app.py --server.port 8502`.
- AI key missing: create `.streamlit/secrets.toml`, then restart.
- API quota/model error: check the API dashboard and model availability; Demo mode always works without an API key.

## Limitations
- Alexa+-inspired simulation, not official Alexa+ integration.
- No AWS integration or MCP server in this version.
- Learning progress is in memory and resets when the session resets. Export JSON to keep a copy.
- AI-generated quizzes can contain mistakes; verify important facts.
