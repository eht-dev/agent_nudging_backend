from .base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime

class DynamicAgent(BaseAgent):
    """Configurable agent that can be customized for any use case"""
    
    def execute(self) -> Dict[str, Any]:
        """Execute agent based on configuration"""
        try:
            # Parse configuration
            query_config = json.loads(self.config.get('query_config', '{}'))
            template_config = json.loads(self.config.get('template_config', '{}'))
            channel_config = json.loads(self.config.get('channel_config', '{}'))
            
            # Execute query
            query = self._build_query(query_config)
            results = self.execute_query(query)
            
            # Process results and send notifications
            actions_taken = 0
            for row in results:
                if self._check_conditions(row, query_config.get('conditions', [])):
                    self._send_notifications(row, template_config, channel_config)
                    actions_taken += 1
            
            result = {
                'success': True,
                'items_processed': len(results),
                'actions_taken': actions_taken,
                'execution_time': datetime.utcnow().isoformat()
            }
            
            self.log_execution(result)
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'items_processed': 0,
                'actions_taken': 0
            }
            self.log_execution(error_result)
            return error_result
    
    def _build_query(self, query_config: Dict[str, Any]) -> str:
        """Build SQL query from configuration"""
        main_table = query_config.get('main_table', '')
        joins = query_config.get('joins', [])
        conditions = query_config.get('conditions', [])
        where_conditions = query_config.get('where_conditions', [])  # Add this
        select_fields = query_config.get('select_fields', ['*'])
        
        # Build SELECT clause
        query = f"SELECT {', '.join(select_fields)} FROM {main_table}"
        
        # Add JOINs
        for join in joins:
            query += f" {join['join_type']} JOIN {join['table']} ON {join['condition']}"
        
        # Add WHERE clause - FIX THIS PART
        all_conditions = []
        
        # Add where_conditions from AI analysis
        for condition in where_conditions:
            all_conditions.append(f"{condition['field']} {condition['operator']} '{condition['value']}'")
        
        # Add legacy conditions
        for condition in conditions:
            all_conditions.append(f"{condition['field']} {condition['operator']} '{condition['value']}'")
        
        if all_conditions:
            query += f" WHERE {' AND '.join(all_conditions)}"
        
        # Add LIMIT for safety
        query += " LIMIT 1000"
        
        return query
    
    def _check_conditions(self, row: Dict[str, Any], conditions: List[Dict[str, Any]]) -> bool:
        """Check if row meets additional conditions"""
        # Additional runtime conditions can be checked here
        return True
    
    def _send_notifications(self, row: Dict[str, Any], template_config: Dict[str, Any], channel_config: Dict[str, Any]):
        """Send notifications based on configuration"""
        # Replace template variables
        message = self._process_template(template_config.get('template', ''), row)
        
        # Send via configured channels
        channels = channel_config.get('channels', ['email'])
        
        for channel in channels:
            if channel == 'email':
                self._send_email(row, message, template_config)
            elif channel == 'sms':
                self._send_sms(row, message)
            elif channel == 'push':
                self._send_push_notification(row, message)
    
    def _process_template(self, template: str, row_data: Dict[str, Any]) -> str:
        """Replace template variables with actual data"""
        processed = template
        for key, value in row_data.items():
            processed = processed.replace(f"{{{{{key}}}}}", str(value))
        return processed
    
    def _send_email(self, row: Dict[str, Any], message: str, template_config: Dict[str, Any]):
        """Send email notification (mock implementation)"""
        email = row.get('email', 'unknown@example.com')
        subject = template_config.get('subject', 'Notification')
        
        print(f"📧 EMAIL to {email}")
        print(f"   Subject: {subject}")
        print(f"   Message: {message}")
        print("-" * 50)
   
    def _send_sms(self, row: Dict[str, Any], message: str):
       """Send SMS notification (mock implementation)"""
       phone = row.get('phone', 'unknown')
       
       print(f"📱 SMS to {phone}")
       print(f"   Message: {message}")
       print("-" * 50)
   
    def _send_push_notification(self, row: Dict[str, Any], message: str):
       """Send push notification (mock implementation)"""
       user_id = row.get('id', 'unknown')
       
       print(f"🔔 PUSH notification to user {user_id}")
       print(f"   Message: {message}")
       print("-" * 50)
