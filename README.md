---
title: Email Triage Environment
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---

# Email Triage Environment

OpenEnv compliant email triage simulation with 3 difficulty levels.

## API Endpoints
- GET /health - Health check
- POST /reset?task_id=easy_triage - Reset environment
- POST /step - Execute action
- GET /state - Get current state
