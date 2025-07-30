import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import psycopg2
from pathlib import Path

# Load environment variables
load_dotenv()

LIST_SCHEMA="./sql_files/list_schema.sql"
LIST_DATABASE_INFOS="./sql_files/list_database_infos.sql"
TABLE_IN_SCHEMA="./sql_files/list_tables_in_schema.sql"
COLUMN_IN_TABLE="./sql_files/list_columns_in_table.sql"
EXTENSIONS_IN_TABLE = "./sql_files/list_extentions.sql"

class DatabaseInterface:
	def __init__(self, db_config: Optional[Dict[str, Any]] = None):
		
		if db_config:
			self.db_config = db_config
		else:
			# Fallback to environment variables
			self.db_config = {
				'host': os.getenv('DB_HOST'),
				'port': int(os.getenv('DB_PORT', 5432)),
				'database': os.getenv('DB_NAME'),
				'user': os.getenv('DB_USER'),
				'password': os.getenv('DB_PASSWORD')
			}
			
		# Validate configuration
		required_fields = ['host', 'database', 'user', 'password']
		missing_fields = [field for field in required_fields if not self.db_config.get(field)]
		if missing_fields:
			raise ValueError(f"Missing required database configuration: {missing_fields}")
		
	def get_db_connection(self):
		"""Create database connection with error handling"""
		try:
			return psycopg2.connect(**self.db_config)
		except psycopg2.Error as e:
			raise ConnectionError(f"Failed to connect to database: {str(e)}")
	
	def list_database_info(self):
		sql_path = Path(LIST_DATABASE_INFOS)
		with sql_path.open("r", encoding="utf-8") as f:
			query = f.read()

		conn = self.get_db_connection()
		try:
			with conn.cursor() as cur:
				cur.execute(query)
				result = cur.fetchone()[0]  # JSON object
				return result
		finally:
			conn.close()

	def list_schemas(self):
		sql_path = Path(LIST_SCHEMA)
		with sql_path.open("r", encoding="utf-8") as f:
			query = f.read()

		conn = self.get_db_connection()
		try:
			with conn.cursor() as cur:
				cur.execute(query)
				result = cur.fetchone()[0]  # JSON object
				return result
		finally:
			conn.close()
	
	def list_tables_in_schema(self, schema_name: str):
		sql_path = Path(TABLE_IN_SCHEMA)
		with sql_path.open("r", encoding="utf-8") as f:
			query = f.read()

		conn = self.get_db_connection()
		try:
			with conn.cursor() as cur:
				cur.execute(query, {'schema_name': schema_name})
				result = cur.fetchone()[0]  # JSON object
				return result
		finally:
			conn.close()

	
	def list_columns_in_table(self, schema_name: str, table_name: str):
		sql_path = Path(COLUMN_IN_TABLE)
		with sql_path.open("r", encoding="utf-8") as f:
			query = f.read()

		conn = self.get_db_connection()
		try:
			with conn.cursor() as cur:
				cur.execute(query, {
					'schema_name': schema_name,
					'table_name': table_name
				})
				result = cur.fetchone()[0]  # JSON object
				return result
		finally:
			conn.close()
	
	def list_extensions(self):
		sql_path = Path(EXTENSIONS_IN_TABLE)
		with sql_path.open("r", encoding="utf-8") as f:
			query = f.read()
		conn = self.get_db_connection()
		try:
			with conn.cursor() as cur:
				cur.execute(query)
				result = cur.fetchone()[0]  # JSON object
				return result
		finally:
			conn.close()

	def execute_sql_file(self, file_path: str):
		"""Execute SQL statements from a file"""
		sql_path = Path(file_path)
		if not sql_path.exists():
			return f"❌ SQL file not found: {file_path}"
		
		try:
			with sql_path.open("r", encoding="utf-8") as f:
				sql_content = f.read()
			conn = self.get_db_connection()
			try:
				with conn.cursor() as cur:
					# Split SQL content by semicolon and execute each statement
					sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
					executed_commands = []
					for command in sql_commands:
						if command:  # Skip empty commands
							cur.execute(command)
							executed_commands.append(command.split()[0:3])  # First few words for logging
					
					conn.commit()
					return f"✅ Successfully executed {len(executed_commands)} SQL commands"
					
			except Exception as e:
				conn.rollback()
				return f"❌ Error executing SQL file: {str(e)}"
			finally:
				conn.close()
				
		except Exception as e:
			return f"❌ Error reading SQL file: {str(e)}"

	def read_only_query(self, query):
		try:
			conn = self.get_db_connection()
			try:
				with conn.cursor() as cur:
					cur.execute("SET TRANSACTION READ ONLY")
					cur.execute(query)
					result = cur.fetchall()  # JSON object
					return result
			except Exception as e:
					conn.rollback()
					return f"❌ Error creating table: {str(e)}"
			finally:
				conn.close()
		except Exception as e:
			return f"❌ Connection error: {str(e)}"

	def create_table_from_query(self, table_name: str, source_query: str, drop_if_exists: bool = True) -> str:
		"""Create permanent table from any SELECT query"""
		try:
			conn = self.get_db_connection()
			try:
				with conn.cursor() as cur:
					# Optional: Drop existing table first
					if drop_if_exists and (table_name != "transactions" and table_name != "customers" and table_name != "articles"):
						drop_query = f"DROP TABLE IF EXISTS {table_name}"
						cur.execute(drop_query)
					
					# Create permanent table (removed TEMP keyword)
					create_query = f"CREATE TABLE {table_name} AS {source_query}"
					cur.execute(create_query)
					conn.commit()
					
					# Verify creation and get row count
					cur.execute(f"SELECT COUNT(*) FROM {table_name}")
					count = cur.fetchone()[0]
					
					print(f"✅ Table '{table_name}' created successfully with {count} rows")
					return f"✅ Table '{table_name}' created successfully with {count} rows"
					
			except Exception as e:
				conn.rollback()
				return f"❌ Error creating table: {str(e)}"
			finally:
				conn.close()
		except Exception as e:
			return f"❌ Connection error: {str(e)}"
	
	def drop_table(self, table_name: str, cascade: bool = False) -> str:
		"""Drop a table"""
		try:
			conn = self.get_db_connection()
			try:
				with conn.cursor() as cur:
					cascade_clause = " CASCADE" if cascade else ""
					if table_name != "transactions" and table_name != "customers" and table_name != "articles":
						drop_query = f"DROP TABLE IF EXISTS {table_name}{cascade_clause}"
						cur.execute(drop_query)
						conn.commit()
						return f"✅ Table '{table_name}' dropped successfully"
					else:
						return f"❌ Table '{table_name}' is a system table and cannot be dropped"
			except Exception as e:
				conn.rollback()
				return f"❌ Error dropping table: {str(e)}"
			finally:
				conn.close()
		except Exception as e:
			return f"❌ Connection error: {str(e)}"