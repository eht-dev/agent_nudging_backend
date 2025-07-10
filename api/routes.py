from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db, AgentConfiguration, AgentExecution, DatabaseConnection
from database.schema_discovery import SchemaDiscovery
from llm.ai_components import SchemaSemanticAnalyzer, QueryStrategyGenerator
from agents.scheduler import agent_scheduler
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from sqlalchemy import text

router = APIRouter()

# Pydantic models
class DatabaseConnectionRequest(BaseModel):
   connection_name: str
   database_type: str
   connection_string: str

class AgentConfigRequest(BaseModel):
   agent_name: str
   agent_type: str
   database_config: str
   query_config: str
   template_config: str
   schedule_config: str
   channel_config: str

class IntentAnalysisRequest(BaseModel):
   user_intent: str
   database_connection_id: int

# Database connection endpoints
@router.post("/database/connect")
async def connect_database(request: DatabaseConnectionRequest, db: Session = Depends(get_db)):
   """Connect to a new database and discover schema"""
   try:
       # Test connection
       discovery = SchemaDiscovery(request.connection_string)
       schema = discovery.get_complete_schema()
       
       # Save connection
       db_conn = DatabaseConnection(
           connection_name=request.connection_name,
           database_type=request.database_type,
           connection_string=request.connection_string,
           schema_cache=json.dumps(schema),
           last_schema_refresh=datetime.utcnow()
       )
       
       db.add(db_conn)
       db.commit()
       db.refresh(db_conn)
       
       return {
           "message": "Database connected successfully",
           "connection_id": db_conn.id,
           "schema": schema
       }
       
   except Exception as e:
       raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@router.get("/database/connections")
async def get_database_connections(db: Session = Depends(get_db)):
   """Get all database connections"""
   connections = db.query(DatabaseConnection).filter(DatabaseConnection.is_active == True).all()
   
   return [
       {
           "id": conn.id,
           "connection_name": conn.connection_name,
           "database_type": conn.database_type,
           "last_schema_refresh": conn.last_schema_refresh.isoformat() if conn.last_schema_refresh else None,
           "created_at": conn.created_at.isoformat()
       }
       for conn in connections
   ]

@router.get("/database/{connection_id}/schema")
async def get_database_schema(connection_id: int, db: Session = Depends(get_db)):
   """Get cached schema for a database connection"""
   connection = db.query(DatabaseConnection).filter(DatabaseConnection.id == connection_id).first()
   
   if not connection:
       raise HTTPException(status_code=404, detail="Database connection not found")
   
   schema = json.loads(connection.schema_cache or '{}')
   return schema

@router.post("/database/{connection_id}/refresh-schema")
async def refresh_database_schema(connection_id: int, db: Session = Depends(get_db)):
   """Refresh schema cache for a database connection"""
   connection = db.query(DatabaseConnection).filter(DatabaseConnection.id == connection_id).first()
   
   if not connection:
       raise HTTPException(status_code=404, detail="Database connection not found")
   
   try:
       discovery = SchemaDiscovery(connection.connection_string)
       schema = discovery.get_complete_schema()
       
       connection.schema_cache = json.dumps(schema)
       connection.last_schema_refresh = datetime.utcnow()
       db.commit()
       
       return {
           "message": "Schema refreshed successfully",
           "schema": schema
       }
       
   except Exception as e:
       raise HTTPException(status_code=400, detail=f"Schema refresh failed: {str(e)}")

# AI-powered analysis endpoints
@router.post("/ai/analyze-schema")
async def analyze_schema_with_ai(connection_id: int, db: Session = Depends(get_db)):
   """Analyze database schema using AI"""
   connection = db.query(DatabaseConnection).filter(DatabaseConnection.id == connection_id).first()
   
   if not connection:
       raise HTTPException(status_code=404, detail="Database connection not found")
   
   schema = json.loads(connection.schema_cache or '{}')
   
   try:
       analyzer = SchemaSemanticAnalyzer()
       analysis = analyzer.llm.analyze_schema(schema)
       
       return {
           "analysis": analysis,
           "schema_summary": {
               "table_count": len(schema.get('tables', {})),
               "total_columns": sum(len(table.get('columns', [])) for table in schema.get('tables', {}).values()),
               "relationships": sum(len(table.get('relationships', [])) for table in schema.get('tables', {}).values())
           }
       }
       
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/ai/parse-intent")
async def parse_user_intent(request: IntentAnalysisRequest, db: Session = Depends(get_db)):
    print("🚀 API: Starting intent parsing...")
    print(f"📝 Request: {request.user_intent}")
    print(f"🔗 Connection ID: {request.database_connection_id}")
    
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == request.database_connection_id
    ).first()
    
    if not connection:
        print("❌ Database connection not found")
        raise HTTPException(status_code=404, detail="Database connection not found")
    
    print(f"✅ Connection found: {connection.connection_name}")
    
    try:
        schema = json.loads(connection.schema_cache or '{}')
        print(f"📊 Schema loaded - Tables: {list(schema.get('tables', {}).keys())}")
        
        if not schema.get('tables'):
            print("❌ No tables in schema cache")
            raise HTTPException(status_code=400, detail="No schema found. Please refresh schema first.")
        
        # Use LLM for analysis
        from llm.llm_interface import create_llm
        llm = create_llm()
        
        print("🤖 Calling DuckDB-NSQL...")
        ai_result = llm.parse_intent(request.user_intent, schema)
        print(f"✅ AI Analysis complete")
        
        # Build response
        response = {
            "parsed_intent": {
                "parsed_intent": ai_result.get("parsed_intent"),
                "business_goal": ai_result.get("business_goal"),
                "target_entity": ai_result.get("target_entity")
            },
            "suggested_query_strategy": {
                "main_table": ai_result.get("main_table"),
                "required_joins": [
                    {
                        "table": join.get("table"),
                        "join_type": join.get("type", "INNER") + " JOIN",
                        "condition": join.get("condition")
                    }
                    for join in ai_result.get("joins", [])
                ],
                "where_conditions": ai_result.get("where_conditions", []),
                "select_fields": ai_result.get("select_fields", []),
                "expected_result_count": "unknown",
                "performance_notes": []
            },
            "confidence": "high" if ai_result.get("main_table") != "unknown" else "low"
        }
        
        print(f"📤 Sending response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

# Add debug endpoint
@router.get("/debug/schema/{connection_id}")
async def debug_schema(connection_id: int, db: Session = Depends(get_db)):
    connection = db.query(DatabaseConnection).filter(DatabaseConnection.id == connection_id).first()
    
    if not connection:
        return {"error": "Connection not found"}
    
    schema = json.loads(connection.schema_cache or '{}')
    
    return {
        "connection_name": connection.connection_name,
        "has_schema_cache": bool(connection.schema_cache),
        "schema_tables": list(schema.get('tables', {}).keys()),
        "table_count": len(schema.get('tables', {})),
        "sample_schema": {
            table_name: {
                "columns": [col['name'] for col in table_info.get('columns', [])[:5]],
                "column_count": len(table_info.get('columns', []))
            }
            for table_name, table_info in list(schema.get('tables', {}).items())[:3]
        }
    }

@router.post("/ai/suggest-joins")
async def suggest_table_joins(connection_id: int, tables: List[str], db: Session = Depends(get_db)):
   """Suggest optimal joins between selected tables"""
   connection = db.query(DatabaseConnection).filter(DatabaseConnection.id == connection_id).first()
   
   if not connection:
       raise HTTPException(status_code=404, detail="Database connection not found")
   
   try:
       discovery = SchemaDiscovery(connection.connection_string)
       suggested_joins = discovery.suggest_joins_for_tables(tables)
       
       return {
           "suggested_joins": suggested_joins,
           "tables": tables
       }
       
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Join suggestion failed: {str(e)}")

# Agent management endpoints
@router.post("/agents/create")
async def create_agent(request: AgentConfigRequest, db: Session = Depends(get_db)):
   """Create new dynamic agent"""
   try:
       agent_config = AgentConfiguration(
           agent_name=request.agent_name,
           agent_type=request.agent_type,
           database_config=request.database_config,
           query_config=request.query_config,
           template_config=request.template_config,
           schedule_config=request.schedule_config,
           channel_config=request.channel_config
       )
       
       db.add(agent_config)
       db.commit()
       db.refresh(agent_config)
       
       # Add to scheduler if active
       if agent_config.is_active:
           agent_scheduler.add_agent(agent_config.id)
       
       return {
           "message": "Agent created successfully",
           "agent_id": agent_config.id
       }
       
   except Exception as e:
       raise HTTPException(status_code=400, detail=f"Agent creation failed: {str(e)}")

@router.get("/agents")
async def get_agents(db: Session = Depends(get_db)):
   """Get all agents"""
   agents = db.query(AgentConfiguration).all()
   
   return [
       {
           "id": agent.id,
           "agent_name": agent.agent_name,
           "agent_type": agent.agent_type,
           "is_active": agent.is_active,
           "last_run": agent.last_run.isoformat() if agent.last_run else None,
            "created_at": agent.created_at.isoformat() if agent.created_at else None

       }
       for agent in agents
   ]

@router.get("/agents/{agent_id}")
async def get_agent_details(agent_id: int, db: Session = Depends(get_db)):
   """Get detailed agent information"""
   agent = db.query(AgentConfiguration).filter(AgentConfiguration.id == agent_id).first()
   
   if not agent:
       raise HTTPException(status_code=404, detail="Agent not found")
   
   # Get recent executions
   recent_executions = db.query(AgentExecution).filter(
       AgentExecution.agent_config_id == agent_id
   ).order_by(AgentExecution.started_at.desc()).limit(10).all()
   
   return {
       "agent": {
           "id": agent.id,
           "agent_name": agent.agent_name,
           "agent_type": agent.agent_type,
           "database_config": json.loads(agent.database_config or '{}'),
           "query_config": json.loads(agent.query_config or '{}'),
           "template_config": json.loads(agent.template_config or '{}'),
           "schedule_config": json.loads(agent.schedule_config or '{}'),
           "channel_config": json.loads(agent.channel_config or '{}'),
           "is_active": agent.is_active,
           "last_run": agent.last_run.isoformat() if agent.last_run else None,
           "created_at": agent.created_at.isoformat()
       },
       "recent_executions": [
           {
               "id": execution.id,
               "started_at": execution.started_at.isoformat(),
               "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
               "status": execution.status,
               "items_processed": execution.items_processed,
               "actions_taken": execution.actions_taken
           }
           for execution in recent_executions
       ]
   }

@router.post("/agents/{agent_id}/execute")
async def execute_agent_manually(agent_id: int, db: Session = Depends(get_db)):
   """Manually execute an agent"""
   agent_config = db.query(AgentConfiguration).filter(AgentConfiguration.id == agent_id).first()
   
   if not agent_config:
       raise HTTPException(status_code=404, detail="Agent not found")
   
   try:
       from agents.dynamic_agent import DynamicAgent
       
       agent = DynamicAgent(agent_config.__dict__)
       result = agent.execute()
       
       return {
           "message": "Agent executed successfully",
           "result": result
       }
       
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@router.post("/agents/{agent_id}/toggle")
async def toggle_agent_status(agent_id: int, db: Session = Depends(get_db)):
   """Toggle agent active status"""
   agent = db.query(AgentConfiguration).filter(AgentConfiguration.id == agent_id).first()
   
   if not agent:
       raise HTTPException(status_code=404, detail="Agent not found")
   
   agent.is_active = not agent.is_active
   db.commit()
   
   if agent.is_active:
       agent_scheduler.add_agent(agent_id)
   else:
       agent_scheduler.remove_agent(agent_id)
   
   return {
       "message": f"Agent {'activated' if agent.is_active else 'deactivated'}",
       "is_active": agent.is_active
   }

# Scheduler management
@router.get("/scheduler/status")
async def get_scheduler_status():
   """Get scheduler status"""
   return agent_scheduler.get_status()

@router.post("/scheduler/start")
async def start_scheduler():
   """Start the agent scheduler"""
   agent_scheduler.start()
   return {"message": "Scheduler started"}

@router.post("/scheduler/stop")
async def stop_scheduler():
   """Stop the agent scheduler"""
   agent_scheduler.stop()
   return {"message": "Scheduler stopped"}

# Test query endpoint
class QueryTestRequest(BaseModel):
    connection_id: int
    query: str

@router.post("/query/test")
async def test_query(request: QueryTestRequest, db: Session = Depends(get_db)):
    """Test a SQL query"""
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == request.connection_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Database connection not found")
    
    try:
        discovery = SchemaDiscovery(connection.connection_string)
        
        with discovery.engine.connect() as conn:
            result = conn.execute(text(request.query))
            columns = list(result.keys())
            rows = result.fetchmany(10)  # Limit to 10 rows for testing
            
            return {
                "columns": columns,
                "rows": [list(row) for row in rows],
                "row_count": len(rows)
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query failed: {str(e)}")