from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from agents.scheduler import agent_scheduler
from database.connection import create_tables
import uvicorn
import os

app = FastAPI(
   title="Universal Multi-Agent Automation Platform",
   description="AI-powered database automation for any business use case",
   version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
   """Initialize application on startup"""
   print("🚀 Starting Universal Multi-Agent Platform")
   
   # Create database tables
   try:
       create_tables()
       print("✅ Database tables created/verified")
   except Exception as e:
       print(f"⚠️  Database setup warning: {e}")
   
   # Start agent scheduler
   try:
       agent_scheduler.start()
       print("✅ Agent scheduler started")
   except Exception as e:
       print(f"⚠️  Scheduler warning: {e}")

@app.on_event("shutdown")
async def shutdown_event():
   """Cleanup on application shutdown"""
   print("⏹️  Stopping Universal Multi-Agent Platform")
   agent_scheduler.stop()

@app.get("/")
async def root():
   return {
       "message": "Universal Multi-Agent Automation Platform",
       "status": "running",
       "version": "1.0.0",
       "features": [
           "Universal database connectivity",
           "AI-powered query building", 
           "Multi-channel communication",
           "Dynamic agent creation",
           "Real-time monitoring"
       ]
   }

@app.get("/health")
async def health_check():
   return {
       "status": "healthy",
       "scheduler": agent_scheduler.get_status(),
       "timestamp": "2024-07-09T12:00:00Z"
   }

if __name__ == "__main__":
   port = int(os.getenv('API_PORT', 8000))
   host = os.getenv('API_HOST', '0.0.0.0')
   
   uvicorn.run(
       "main:app",
       host=host,
       port=port,
       reload=True,
       log_level="info"
   )
