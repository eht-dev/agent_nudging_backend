from sqlalchemy import inspect, text, create_engine
from typing import Dict, List, Any
import json
from datetime import datetime

class SchemaDiscovery:
    """Automatically discover database schema and relationships"""
    
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.inspector = inspect(self.engine)
    
    def get_all_tables(self) -> List[str]:
        """Get all table names"""
        return self.inspector.get_table_names()
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all columns for a table"""
        columns = self.inspector.get_columns(table_name)
        return [
            {
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col['nullable'],
                'primary_key': col.get('primary_key', False),
                'autoincrement': col.get('autoincrement', False)
            }
            for col in columns
        ]
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key relationships"""
        fks = self.inspector.get_foreign_keys(table_name)
        return [
            {
                'column': fk['constrained_columns'][0],
                'referenced_table': fk['referred_table'],
                'referenced_column': fk['referred_columns'][0]
            }
            for fk in fks
        ]
    
    def get_complete_schema(self) -> Dict[str, Any]:
        """Get complete database schema with relationships"""
        schema = {
            'discovered_at': datetime.utcnow().isoformat(),
            'tables': {}
        }
        
        for table_name in self.get_all_tables():
            schema['tables'][table_name] = {
                'columns': self.get_table_columns(table_name),
                'foreign_keys': self.get_foreign_keys(table_name),
                'relationships': self._discover_relationships(table_name)
            }
        
        return schema
    
    def _discover_relationships(self, table_name: str) -> List[Dict[str, Any]]:
        """Discover all possible relationships for a table"""
        relationships = []
        
        # Direct foreign keys (many-to-one)
        for fk in self.get_foreign_keys(table_name):
            relationships.append({
                'type': 'many_to_one',
                'table': fk['referenced_table'],
                'join_condition': f"{table_name}.{fk['column']} = {fk['referenced_table']}.{fk['referenced_column']}"
            })
        
        # Reverse relationships (one-to-many)
        for other_table in self.get_all_tables():
            if other_table != table_name:
                for fk in self.get_foreign_keys(other_table):
                    if fk['referenced_table'] == table_name:
                        relationships.append({
                            'type': 'one_to_many',
                            'table': other_table,
                            'join_condition': f"{table_name}.id = {other_table}.{fk['column']}"
                        })
        
        return relationships
    
    def suggest_joins_for_tables(self, tables: List[str]) -> List[Dict[str, Any]]:
        """Suggest optimal joins between multiple tables"""
        schema = self.get_complete_schema()
        suggested_joins = []
        
        for i, table1 in enumerate(tables):
            for table2 in tables[i+1:]:
                # Find direct relationship
                for rel in schema['tables'][table1]['relationships']:
                    if rel['table'] == table2:
                        suggested_joins.append({
                            'from_table': table1,
                            'to_table': table2,
                            'join_type': 'LEFT JOIN',
                            'condition': rel['join_condition'],
                            'relationship_type': rel['type']
                        })
        
        return suggested_joins
