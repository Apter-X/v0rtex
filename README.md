# <Project Template Name>

> A clean, professional boilerplate with built-in docs, CI, and GitHub hygiene—ready for Cursor.

![Build](https://img.shields.io/badge/build-passing-success)
![License](https://img.shields.io/badge/license-MIT-informational)
<!-- Add more badges as needed (coverage, version, etc.) -->

---

## ✨ What’s inside
- **Docs**: `/docs/logbook.md` (devblog), `/docs/todo.md`, `/docs/architecture.md`, ADRs
- **Quality**: Editor config, git attributes/ignore, PR/issue templates
- **Automation**: CI workflow (`.github/workflows/ci.yml`)
- **Standards**: Conventional Commits, clean branching model, changelog

---

## 🚀 Getting started

### 1) Use this as a template
- Click **Use this template** on GitHub → **Create a new repository**
- Or: `gh repo create <your-repo> --template <org/your-template>`

### 2) Initialize your stack
```bash
# Example (Node)
npm i
npm run dev

# Example (Python)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt