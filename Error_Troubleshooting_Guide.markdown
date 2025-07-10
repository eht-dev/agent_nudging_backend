# Error Troubleshooting Guide

## Where to Look for Different Errors

| Errorව| **Check These Files** | **Common Issues** |
|--------|-----------------------|-------------------|
| Server won't start | main.py, .env | Missing dependencies, wrong ports |
| Database errors | database/connection.py, .env | Wrong credentials, MySQL not running |
| Import errors | requirements.txt, file structure | Missing packages, wrong file paths |
| API errors | api/routes.py | Endpoint issues, validation errors |
| Agent errors | agents/ folder | Logic errors, scheduling issues |
| LLM/AI errors | llm/llm_interface.py | Ollama not running, API issues |
| Schema errors | database/schema_discovery.py | Database connection, table access |

## 🔄 Complete Application Flow

### 1. Startup Flow
- **main.py**
  - Loads environment (.env)
  - Creates database tables
  - Starts agent scheduler
  - Includes API routes
  - Starts FastAPI server (port 8000)

### 2. Agent Creation Flow
- **Frontend Request**
  - api/routes.py (/agents/create)
  - database/connection.py (saves config)
  - agents/scheduler.py (schedules agent)
  - agents/dynamic_agent.py (executes logic)

### 3. Database Connection Flow
- **Database Connect Request**
  - api/routes.py (/database/connect)
  - database/schema_discovery.py (discovers tables)
  - database/connection.py (saves schema cache)
  - Returns schema to frontend

### 4. AI Analysis Flow
- **User Intent Request**
  - api/routes.py (/ai/parse-intent)
  - llm/ai_components.py (AI analysis)
  - llm/llm_interface.py (LLM calls)
  - Returns suggestions to frontend

### 5. Agent Execution Flow
- **Scheduled Agent Run**
  - agents/scheduler.py (triggers execution)
  - agents/dynamic_agent.py (main logic)
  - database/schema_discovery.py (query execution)
  - llm/llm_interface.py (message generation)
  - Mock delivery (print statements)

## 🚨 Quick Error Diagnosis
- **Can't start server?**
  - Check main.py, .env, requirements.txt
- **Database issues?**
  - Check database/connection.py, MySQL running, .env credentials
- **Agent not working?**
  - Check agents/dynamic_agent.py, agent configuration
- **AI not responding?**
  - Check llm/llm_interface.py, Ollama running
- **API errors?**
  - Check api/routes.py, request format