# Multimodal Construction Intelligence Platform

A Skill Wallet capstone project built with Python and Streamlit. It includes PPE and safety audit, concrete crack diagnostics, construction budget and property valuation, weather scenario advisories, and an AI chatbot.

## Setup

1. Install Python 3.9 or newer.
2. Open a terminal in this folder.
3. Install dependencies: `pip install -r requirements.txt`
4. Launch: `streamlit run app.py`
5. Open the localhost URL shown in the terminal (usually `http://localhost:8501`).
6. Optionally enter a Google Gemini API key in the sidebar and set an available model name. API model access and pricing depend on your Google account.

## Demo mode

Without an API key, image analysis returns **explicitly illustrative sample output**, never a fabricated detection. Planning estimates and manually selected weather guidance work without an API key. The chatbot displays a demo limitation notice.

## Deployment

Push `app.py` and `requirements.txt` to a GitHub repository and deploy through Streamlit Community Cloud. Enter the Gemini API key into the app sidebar at runtime. Do not commit keys to source control. For a public production deployment, replace direct user-provided API key handling with a secure secrets/backend design and apply access controls.

## Limitations

This is an educational prototype. Image interpretation cannot certify OSHA/IS 456 compliance or structural safety. Crack width cannot be measured reliably without a calibrated scale. Valuation is based on entered rates, not live market feeds. Weather scenarios are selected manually, not pulled from a forecast service. A real architectural 3D rendering engine is not included; the app generates a rendering prompt. Verify engineering decisions with qualified professionals.
