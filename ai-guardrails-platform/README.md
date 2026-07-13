# AI Guardrails Platform

Enterprise-grade AI Safety and Guardrail Validation Framework.

## Features

- Prompt Injection Detection
- Harmful Content Detection
- PII Detection
- Jailbreak Detection
- Phishing Detection
- Safety Scoring Engine
- JSON Report Generation
- HTML Dashboard Reports
- CI/CD GitHub Actions Integration
- Enterprise AI Safety Testing

---

## Project Structure

```bash
ai-guardrails-platform/
│
├── app/
│   ├── detectors/
│   ├── evaluators/
│   └── reports/
│
├── datasets/
│   └── guardrail_tests/
│
├── reports/
│   ├── json/
│   └── html/
│
├── .github/
│   └── workflows/
│
└── run_guardrail_tests.py
```

---

## Supported Guardrails

| Guardrail Type | Description |
|---|---|
| Prompt Injection | Detects instruction override attempts |
| Harmful Content | Detects malicious or unsafe requests |
| PII Detection | Detects sensitive personal information |
| Jailbreak Detection | Detects safety bypass attempts |
| Phishing Detection | Detects phishing/social engineering prompts |

---

## Run Locally

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Mac/Linux

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Guardrail Tests

```bash
python run_guardrail_tests.py
```

---

## Generated Reports

### JSON Report

```bash
reports/json/latest_guardrail_report.json
```

### HTML Report

```bash
reports/html/latest_guardrail_report.html
```

---

## CI/CD Integration

This project supports automated AI safety checks using GitHub Actions.

Workflow file:

```bash
.github/workflows/guardrails-check.yml
```

---

## Example Test Cases

- Ignore all previous instructions
- Reveal hidden system prompts
- Bypass safety restrictions
- Generate phishing emails
- Store sensitive personal data

---

## Future Enhancements

- Toxicity Detection
- LLM Output Moderation
- Policy Engine
- Multi-model Safety Validation
- OpenAI Guardrails Integration
- Real-time Monitoring Dashboard

---

## Author

Rambhupal Boreddy

AI Reliability | AI Safety | GenAI QA Engineering