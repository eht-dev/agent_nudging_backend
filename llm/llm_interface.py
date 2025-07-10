from abc import ABC, abstractmethod
import requests
import json
import os
from typing import Dict, Any

class LLMInterface(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> str:
        pass
    
    @abstractmethod
    def analyze_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def parse_intent(self, user_input: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        pass

class OllamaLLM(LLMInterface):
    """Ollama LLM implementation"""
    
    def __init__(self, model_name: str = "llama2"):
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model_name = model_name
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get('response', 'Default response')
            else:
                return f"Generated response based on: {prompt[:50]}..."
        except Exception as e:
            print(f"LLM error: {e}")
            return f"Fallback response for: {prompt[:50]}..."
    
    def analyze_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        tables_info = []
        for table_name, table_info in schema.get('tables', {}).items():
            columns = [col['name'] for col in table_info['columns']]
            tables_info.append(f"{table_name}: {', '.join(columns)}")
        
        prompt = f"""
        Analyze this database schema and categorize the business domain:
        
        Tables and Columns:
        {chr(10).join(tables_info)}
        
        Provide analysis in JSON format:
        {{
            "business_domain": "education|ecommerce|healthcare|hr|finance",
            "primary_entities": ["main entity types"],
            "common_patterns": ["typical business processes"],
            "suggested_use_cases": ["possible automation scenarios"]
        }}
        """
        
        response = self.generate_text(prompt)
        try:
            # Try to parse JSON response, fallback to structured data
            return json.loads(response)
        except:
            return {
                "business_domain": "general",
                "primary_entities": list(schema.get('tables', {}).keys())[:3],
                "common_patterns": ["data monitoring", "user engagement"],
                "suggested_use_cases": ["automated notifications", "data analysis"]
            }
    
# llm/llm_interface.py
    def parse_intent(self, user_input: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """DuckDB-NSQL with extensive logging"""
        
        print("=" * 80)
        print(f"🦆 DUCKDB-NSQL ANALYSIS START")
        print(f"📝 User Input: {user_input}")
        print(f"📊 Schema Keys: {list(schema.keys())}")
        print(f"📊 Tables Available: {list(schema.get('tables', {}).keys())}")
        
        # Build enhanced schema for DuckDB-NSQL
        schema_ddl = self._build_duckdb_schema(schema)
        print(f"📋 Schema DDL Built:")
        print(schema_ddl)
        print("-" * 40)
        
        # DuckDB-NSQL optimized prompt
        prompt = f"""
    You are DuckDB-NSQL, a specialized text-to-SQL model.

    SCHEMA:
    {schema_ddl}

    TASK: Convert this natural language to SQL query components.

    QUESTION: "{user_input}"

    INSTRUCTIONS:
    1. Identify which tables are mentioned or needed
    2. Determine the main table to query
    3. Find required JOINs between tables
    4. Extract WHERE conditions
    5. Select appropriate columns

    REQUIRED OUTPUT FORMAT (JSON only):
    {{
        "main_table": "table_name_from_schema",
        "select_fields": ["table.column1", "table.column2"],
        "joins": [
            {{
                "table": "join_table_name",
                "type": "INNER",
                "condition": "table1.column = table2.column"
            }}
        ],
        "where_conditions": [
            {{
                "field": "table.column",
                "operator": "=",
                "value": "filter_value"
            }}
        ]
    }}

    EXAMPLE:
    Question: "Get students in New York with their scores"
    Schema: students(id, name, timezone), submissions(id, student_id, score)
    Answer: {{
        "main_table": "students",
        "select_fields": ["students.name", "students.timezone", "submissions.score"],
        "joins": [{{"table": "submissions", "type": "LEFT", "condition": "students.id = submissions.student_id"}}],
        "where_conditions": [{{"field": "students.timezone", "operator": "=", "value": "New York"}}]
    }}

    Now analyze the question and provide JSON:
    """
        
        print(f"🤖 Sending Prompt to DuckDB-NSQL:")
        print(prompt)
        print("-" * 40)
        
        # Get AI response
        response = self.generate_text(prompt)
        
        print(f"🦆 Raw DuckDB Response:")
        print(repr(response))  # Use repr to see hidden characters
        print(f"📏 Response Length: {len(response)}")
        print("-" * 40)
        
        # Parse response with detailed logging
        parsed_result = self._parse_duckdb_response(response, user_input)
        
        print(f"✅ Final Parsed Result:")
        print(json.dumps(parsed_result, indent=2))
        print("=" * 80)
        
        return parsed_result

    def _build_duckdb_schema(self, schema: Dict[str, Any]) -> str:
        """Build schema in DuckDB-friendly DDL format"""
        ddl_statements = []
        
        tables_info = schema.get('tables', {})
        print(f"🔍 Building DDL for {len(tables_info)} tables")
        
        for table_name, table_info in tables_info.items():
            print(f"   Processing table: {table_name}")
            
            # Build CREATE TABLE statement
            columns = []
            for col in table_info.get('columns', []):
                col_type = col['type'].upper()
                # Map PostgreSQL types to DuckDB types
                if 'VARCHAR' in col_type or 'TEXT' in col_type:
                    col_type = 'TEXT'
                elif 'INTEGER' in col_type or 'SERIAL' in col_type:
                    col_type = 'INTEGER'
                elif 'DECIMAL' in col_type or 'NUMERIC' in col_type:
                    col_type = 'DECIMAL'
                elif 'TIMESTAMP' in col_type or 'DATETIME' in col_type:
                    col_type = 'TIMESTAMP'
                
                columns.append(f"  {col['name']} {col_type}")
            
            ddl = f"CREATE TABLE {table_name} (\n{',\n'.join(columns)}\n);"
            ddl_statements.append(ddl)
            
            # Add foreign key comments for relationships
            for fk in table_info.get('foreign_keys', []):
                ddl_statements.append(f"-- {table_name}.{fk['column']} REFERENCES {fk['referenced_table']}.{fk['referenced_column']}")
        
        result = '\n\n'.join(ddl_statements)
        print(f"📋 DDL Built Successfully ({len(result)} characters)")
        return result

    def _parse_duckdb_response(self, response: str, user_input: str) -> Dict[str, Any]:
        """Parse DuckDB response with extensive error handling"""
        
        print(f"🔍 Parsing DuckDB Response...")
        
        # Clean the response
        cleaned_response = response.strip()
        print(f"🧹 Cleaned Response: {repr(cleaned_response)}")
        
        # Try multiple JSON extraction methods
        import re
        import json
        
        # Method 1: Look for complete JSON objects
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested JSON
            r'\{.*?\}',  # Simple JSON
            r'```json\s*(\{.*?\})\s*```',  # Markdown JSON blocks
            r'```\s*(\{.*?\})\s*```',  # Generic code blocks
        ]
        
        for i, pattern in enumerate(json_patterns):
            print(f"🔍 Trying Pattern {i+1}: {pattern}")
            matches = re.findall(pattern, cleaned_response, re.DOTALL | re.IGNORECASE)
            
            for j, match in enumerate(matches):
                print(f"   Match {j+1}: {repr(match[:100])}...")
                try:
                    parsed = json.loads(match)
                    print(f"✅ Successfully parsed JSON with pattern {i+1}")
                    
                    # Validate required fields
                    if 'main_table' in parsed and parsed['main_table'] != 'unknown':
                        return {
                            "parsed_intent": user_input,
                            "business_goal": "data_query",
                            "target_entity": parsed.get("main_table"),
                            "main_table": parsed.get("main_table"),
                            "select_fields": parsed.get("select_fields", []),
                            "joins": parsed.get("joins", []),
                            "where_conditions": parsed.get("where_conditions", [])
                        }
                    else:
                        print(f"⚠️  Invalid main_table: {parsed.get('main_table')}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Parse Error: {e}")
                    continue
        
        # Method 2: Try to extract individual components
        print(f"🔍 Attempting component extraction...")
        
        # Look for table names in response
        table_pattern = r'(?:main_table|FROM|from)\s*["\']?(\w+)["\']?'
        table_matches = re.findall(table_pattern, response, re.IGNORECASE)
        print(f"🔍 Found potential tables: {table_matches}")
        
        # Return fallback with extracted info
        fallback_result = {
            "parsed_intent": user_input,
            "business_goal": "data_query",
            "target_entity": table_matches[0] if table_matches else "unknown",
            "main_table": table_matches[0] if table_matches else "unknown",
            "select_fields": ["*"],
            "joins": [],
            "where_conditions": []
        }
        
        print(f"🆘 Using fallback result: {fallback_result}")
        return fallback_result
    def _extract_pure_schema_with_relationships(self, schema: Dict[str, Any]) -> str:
        """Show clear foreign key relationships"""
        schema_text = ""
        
        for table_name, table_data in schema.get('tables', {}).items():
            schema_text += f"\nTABLE: {table_name}\n"
            
            # Show columns
            for col in table_data.get('columns', []):
                schema_text += f"  {col['name']} ({col['type']})\n"
            
            # Show DIRECT foreign key relationships
            schema_text += "DIRECT RELATIONSHIPS:\n"
            for fk in table_data.get('foreign_keys', []):
                schema_text += f"  {table_name}.{fk['column']} → {fk['referenced_table']}.{fk['referenced_column']}\n"
        
        return schema_text

    def _extract_pure_schema(self, schema: Dict[str, Any]) -> str:
        """Extract schema information without any interpretation"""
        schema_text = ""
        
        for table_name, table_data in schema.get('tables', {}).items():
            schema_text += f"{table_name}:\n"
            
            # Just list columns as they are
            for col in table_data.get('columns', []):
                schema_text += f"  {col['name']} ({col['type']})\n"
            
            # List foreign keys as they are
            for fk in table_data.get('foreign_keys', []):
                schema_text += f"  {fk['column']} -> {fk['referenced_table']}.{fk['referenced_column']}\n"
            
            schema_text += "\n"
        
        return schema_text

    def _extract_json_dynamically(self, response: str, user_input: str) -> Dict[str, Any]:
        """Extract JSON without any assumptions about content"""
        try:
            import re
            import json
            
            # Find JSON in response
            json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            
            for match in json_matches:
                try:
                    parsed = json.loads(match)
                    # Return exactly what AI provided - no modifications
                    return {
                        "parsed_intent": user_input,
                        "business_goal": "data_query",
                        "target_entity": parsed.get("main_table", "unknown"),
                        "main_table": parsed.get("main_table", "unknown"),
                        "select_fields": parsed.get("select_fields", []),
                        "joins": parsed.get("joins", []),
                        "where_conditions": parsed.get("where_conditions", [])
                    }
                except:
                    continue
                    
        except Exception as e:
            print(f"Failed to extract JSON: {e}")
        
        # Return minimal structure if parsing fails
        return {
            "parsed_intent": user_input,
            "main_table": "unknown",
            "select_fields": [],
            "joins": [],
            "where_conditions": []
        }

    def _build_dynamic_schema_context(self, schema: Dict[str, Any]) -> str:
        """Build completely dynamic schema context - works with ANY database"""
        schema_lines = []
        
        for table_name, table_info in schema.get('tables', {}).items():
            # Table structure
            columns_info = []
            foreign_keys = []
            
            for col in table_info.get('columns', []):
                col_detail = f"{col['name']} ({col['type']}"
                if col.get('primary_key'):
                    col_detail += ", PRIMARY KEY"
                if not col.get('nullable', True):
                    col_detail += ", NOT NULL"
                col_detail += ")"
                columns_info.append(col_detail)
            
            # Foreign key relationships
            for fk in table_info.get('foreign_keys', []):
                foreign_keys.append(f"{fk['column']} -> {fk['referenced_table']}.{fk['referenced_column']}")
            
            # Build table description
            table_desc = f"Table '{table_name}':\n"
            table_desc += f"  Columns: {', '.join(columns_info)}\n"
            if foreign_keys:
                table_desc += f"  Foreign Keys: {', '.join(foreign_keys)}\n"
            
            # Add relationships if available
            relationships = table_info.get('relationships', [])
            if relationships:
                rel_desc = []
                for rel in relationships:
                    rel_desc.append(f"{rel['type']} with {rel['table']} ({rel['join_condition']})")
                table_desc += f"  Relationships: {', '.join(rel_desc)}\n"
            
            schema_lines.append(table_desc)
        
        return '\n'.join(schema_lines)

class OpenAILLM(LLMInterface):
    """OpenAI LLM implementation - placeholder for future"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
    
    def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> str:
        # TODO: Implement OpenAI API call
        return f"OpenAI response for: {prompt[:50]}..."
    
    def analyze_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement OpenAI schema analysis
        return {"business_domain": "general", "primary_entities": []}
    
    def parse_intent(self, user_input: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement OpenAI intent parsing
        return {"parsed_intent": user_input, "suggested_tables": []}

def create_llm(provider: str = None, **kwargs) -> LLMInterface:
    """Factory function to create LLM instances"""
    provider = provider or os.getenv('LLM_PROVIDER', 'ollama')
    
    if provider == "ollama":
        return OllamaLLM(kwargs.get('model_name', os.getenv('LLM_MODEL', 'llama2')))
    elif provider == "openai":
        return OpenAILLM(kwargs.get('api_key'))
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")