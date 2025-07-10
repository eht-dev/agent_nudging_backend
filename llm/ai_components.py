from typing import Dict, Any, List
from .llm_interface import create_llm
import json
import re

class SchemaSemanticAnalyzer:
    """AI component that understands table purposes and relationships"""
    
    def __init__(self, llm_provider: str = "ollama"):
        self.llm = create_llm(llm_provider)
    
    def analyze_table_purpose(self, table_name: str, columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine the business purpose of a table"""
        column_names = [col['name'] for col in columns]
        
        prompt = f"""
        Analyze this database table and determine its business purpose:
        
        Table Name: {table_name}
        Columns: {', '.join(column_names)}
        
        Based on the table name and column names, what is the business purpose?
        Respond in JSON format:
        {{
            "entity_type": "people|products|transactions|events|relationships",
            "business_purpose": "brief description",
            "domain_hints": ["industry or domain indicators"],
            "typical_queries": ["common questions about this data"]
        }}
        """
        
        response = self.llm.generate_text(prompt)
        try:
            return json.loads(response)
        except:
            return {
                "entity_type": "unknown",
                "business_purpose": f"Data table for {table_name}",
                "domain_hints": [],
                "typical_queries": [f"Find records in {table_name}"]
            }
    
    def suggest_relationships(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest logical relationships between tables"""
        tables_info = []
        for table_name, table_data in schema.get('tables', {}).items():
            columns = [col['name'] for col in table_data['columns']]
            tables_info.append(f"{table_name}: {', '.join(columns)}")
        
        prompt = f"""
        Given these database tables, suggest logical business relationships:
        
        {chr(10).join(tables_info)}
        
        Suggest relationships in JSON format:
        {{
            "relationships": [
                {{
                    "from_table": "table1",
                    "to_table": "table2", 
                    "relationship_type": "one_to_many|many_to_one|many_to_many",
                    "business_logic": "why these tables relate"
                }}
            ]
        }}
        """
        
        response = self.llm.generate_text(prompt)
        try:
            return json.loads(response).get('relationships', [])
        except:
            return []



class QueryStrategyGenerator:
    """AI component that generates optimal database query strategies"""
    
    def __init__(self, llm_provider: str = "ollama"):
        self.llm = create_llm(llm_provider)
    
    def generate_query_strategy(self, intent: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimal query strategy based on business intent"""
        prompt = f"""
        Business Intent: {json.dumps(intent, indent=2)}
        
        Available Schema: {json.dumps(schema, indent=2)}
        
        Generate an optimal database query strategy in JSON format:
        {{
            "main_table": "primary table to query",
            "required_joins": [
                {{
                    "table": "table_name",
                    "join_type": "LEFT|INNER|RIGHT",
                    "condition": "join condition"
                }}
            ],
            "where_conditions": [
                {{
                    "field": "table.column",
                    "operator": "=|>|<|LIKE|IN",
                    "value": "condition value",
                    "logic": "AND|OR"
                }}
            ],
            "select_fields": ["fields to include in results"],
            "expected_result_count": "estimated number of results",
            "performance_notes": ["optimization suggestions"]
        }}
        """
        
        response = self.llm.generate_text(prompt)
        try:
            return json.loads(response)
        except:
            # Fallback strategy
            relevant_tables = intent.get('relevant_tables', [])
            main_table = relevant_tables[0] if relevant_tables else 'unknown'
            
            return {
                "main_table": main_table,
                "required_joins": [],
                "where_conditions": [],
                "select_fields": ["*"],
                "expected_result_count": "unknown",
                "performance_notes": ["Add appropriate indexes"]
            }
    
    def optimize_query(self, query: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest optimizations for a given query"""
        prompt = f"""
        SQL Query: {query}
        
        Database Schema: {json.dumps(schema, indent=2)}
        
        Suggest optimizations in JSON format:
        {{
            "performance_issues": ["identified problems"],
            "optimization_suggestions": ["specific improvements"],
            "index_recommendations": ["suggested indexes"],
            "alternative_approach": "better query if needed"
        }}
        """
        
        response = self.llm.generate_text(prompt)
        try:
            return json.loads(response)
        except:
            return {
                "performance_issues": [],
                "optimization_suggestions": ["Add LIMIT clause", "Use specific columns instead of *"],
                "index_recommendations": [],
                "alternative_approach": None
            }