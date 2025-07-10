from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from .dynamic_agent import DynamicAgent
from database.connection import get_db, AgentConfiguration
import threading
import json
from datetime import datetime

class AgentScheduler:
   """Scheduler that manages all dynamic agents"""
   
   def __init__(self):
       self.scheduler = BackgroundScheduler()
       self.is_running = False
       self.lock = threading.Lock()
   
   def start(self):
       """Start the agent scheduler"""
       with self.lock:
           if self.is_running:
               return
           
           # Load all active agents and schedule them
           self._load_and_schedule_agents()
           
           self.scheduler.start()
           self.is_running = True
           print("🚀 Agent scheduler started")
   
   def stop(self):
       """Stop the agent scheduler"""
       with self.lock:
           if not self.is_running:
               return
           
           self.scheduler.shutdown()
           self.is_running = False
           print("⏹️  Agent scheduler stopped")
   
   def _load_and_schedule_agents(self):
       """Load active agents from database and schedule them"""
       db = next(get_db())
       try:
           active_agents = db.query(AgentConfiguration).filter(
               AgentConfiguration.is_active == True
           ).all()
           
           for agent_config in active_agents:
               self._schedule_agent(agent_config)
               
       finally:
           db.close()
   
   def _schedule_agent(self, agent_config):
       """Schedule individual agent based on its configuration"""
       schedule_config = json.loads(agent_config.schedule_config or '{}')
       schedule_type = schedule_config.get('type', 'interval')
       
       job_id = f"agent_{agent_config.id}"
       
       if schedule_type == 'interval':
           minutes = schedule_config.get('minutes', 60)
           self.scheduler.add_job(
               self._execute_agent,
               IntervalTrigger(minutes=minutes),
               args=[agent_config.id],
               id=job_id,
               max_instances=1,
               replace_existing=True
           )
       elif schedule_type == 'cron':
           cron_expr = schedule_config.get('cron', '0 9 * * *')  # Default: 9 AM daily
           self.scheduler.add_job(
               self._execute_agent,
               CronTrigger.from_crontab(cron_expr),
               args=[agent_config.id],
               id=job_id,
               max_instances=1,
               replace_existing=True
           )
       
       print(f"📅 Scheduled agent: {agent_config.agent_name}")
   
   def _execute_agent(self, agent_config_id: int):
       """Execute a specific agent"""
       db = next(get_db())
       try:
           agent_config = db.query(AgentConfiguration).filter(
               AgentConfiguration.id == agent_config_id
           ).first()
           
           if not agent_config or not agent_config.is_active:
               return
           
           print(f"🤖 Executing agent: {agent_config.agent_name}")
           
           # Create and execute agent
           agent = DynamicAgent(agent_config.__dict__)
           result = agent.execute()
           
           # Update last run time
           agent_config.last_run = datetime.utcnow()
           db.commit()
           
           print(f"✅ Agent completed: {result}")
           
       except Exception as e:
           print(f"❌ Agent execution error: {e}")
       finally:
           db.close()
   
   def add_agent(self, agent_config_id: int):
       """Add new agent to scheduler"""
       db = next(get_db())
       try:
           agent_config = db.query(AgentConfiguration).filter(
               AgentConfiguration.id == agent_config_id
           ).first()
           
           if agent_config:
               self._schedule_agent(agent_config)
       finally:
           db.close()
   
   def remove_agent(self, agent_config_id: int):
       """Remove agent from scheduler"""
       job_id = f"agent_{agent_config_id}"
       try:
           self.scheduler.remove_job(job_id)
       except:
           pass
   
   def get_status(self):
       """Get current scheduler status"""
       jobs = []
       for job in self.scheduler.get_jobs():
           jobs.append({
               'id': job.id,
               'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
               'name': str(job.func)
           })
       
       return {
           'is_running': self.is_running,
           'jobs': jobs,
           'job_count': len(jobs)
       }

# Global scheduler instance
agent_scheduler = AgentScheduler()
