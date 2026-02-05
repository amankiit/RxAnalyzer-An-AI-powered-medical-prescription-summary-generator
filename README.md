# Prescription analyzer

A lightweight web app that uses Perplexity Sonar vision to read English prescription images, extract key fields, and generate an abstractive clinical-style summary.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (or copy `.env.example`) and set your Perplexity API key:

```bash
cp .env.example .env
```

Then edit `.env` and set values (model is optional, defaults to `sonar-pro`):

```bash
PERPLEXITY_API_KEY="your-key-here"
PERPLEXITY_MODEL="sonar-pro"
```

Run the app:

```bash
uvicorn app.main:app --reload
```

Open the UI at:

```
http://127.0.0.1:8000
```

## Notes

- Images are sent to Perplexity for processing. Ensure this aligns with your privacy requirements.
- The output is for prototyping only and must be reviewed by a licensed clinician.
