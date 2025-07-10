from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import json

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('agent_name', 'Unknown Agent')
        self.agent_type = config.get('agent_type', 'custom')
        self.agent_id = config.get('id')
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Main execution logic - must be implemented by each agent"""
        pass
    
    def log_execution(self, result: Dict[str, Any]):
        """Log agent execution results"""
        from database.connection import get_db, AgentExecution
        
        db = next(get_db())
        try:
            execution = AgentExecution(
                agent_config_id=self.agent_id,
                completed_at=datetime.utcnow(),
                status='completed' if result.get('success') else 'failed',
                items_processed=result.get('items_processed', 0),
                actions_taken=result.get('actions_taken', 0),
                execution_log=json.dumps(result)
            )
            db.add(execution)
            db.commit()
        except Exception as e:
            print(f"Failed to log execution: {e}")
        finally:
            db.close()
    
    def get_database_connection(self):
        """Get database connection from config"""
        from database.schema_discovery import SchemaDiscovery
        
        db_config = json.loads(self.config.get('database_config', '{}'))
        connection_string = db_config.get('connection_string')
        
        if connection_string:
            return SchemaDiscovery(connection_string)
        else:
            # Use default connection
            from database.connection import engine
            return SchemaDiscovery(str(engine.url))
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute database query and return results"""
        db_discovery = self.get_database_connection()
        
        try:
            with db_discovery.engine.connect() as conn:
                result = conn.execute(query)
                columns = result.keys()
                rows = result.fetchall()
                
                return [
                    {col: value for col, value in zip(columns, row)}
                    for row in rows
                ]
        except Exception as e:
            print(f"Query execution error: {e}")
            return []
