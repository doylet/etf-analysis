"""
BigQuery client for production data storage
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from google.cloud import bigquery
from google.api_core import exceptions


class BigQueryClient:
    """Client for BigQuery operations"""
    
    def __init__(self, project_id: str = None, dataset_id: str = 'etf_analysis'):
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.dataset_id = dataset_id
        self.client = None
        
        if self.project_id:
            try:
                self.client = bigquery.Client(project=self.project_id)
                self._ensure_dataset()
                self._ensure_tables()
            except Exception as e:
                print(f"Warning: Could not initialize BigQuery: {e}")
    
    def _ensure_dataset(self):
        """Create dataset if it doesn't exist"""
        if not self.client:
            return
        
        dataset_id = f"{self.project_id}.{self.dataset_id}"
        try:
            self.client.get_dataset(dataset_id)
        except exceptions.NotFound:
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "US"
            self.client.create_dataset(dataset)
            print(f"Created dataset {dataset_id}")
    
    def _ensure_tables(self):
        """Create tables if they don't exist"""
        if not self.client:
            return
        
        # Instruments table schema
        instruments_schema = [
            bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING"),
            bigquery.SchemaField("instrument_type", "STRING"),
            bigquery.SchemaField("sector", "STRING"),
            bigquery.SchemaField("is_active", "BOOLEAN"),
            bigquery.SchemaField("added_date", "TIMESTAMP"),
            bigquery.SchemaField("last_updated", "TIMESTAMP"),
            bigquery.SchemaField("notes", "STRING"),
        ]
        
        # Price data table schema
        price_data_schema = [
            bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("date", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("open_price", "FLOAT64"),
            bigquery.SchemaField("high_price", "FLOAT64"),
            bigquery.SchemaField("low_price", "FLOAT64"),
            bigquery.SchemaField("close_price", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("adj_close", "FLOAT64"),
            bigquery.SchemaField("volume", "FLOAT64"),
            bigquery.SchemaField("created_at", "TIMESTAMP"),
        ]
        
        self._create_table_if_not_exists("instruments", instruments_schema)
        self._create_table_if_not_exists("price_data", price_data_schema)
    
    def _create_table_if_not_exists(self, table_name: str, schema: List[bigquery.SchemaField]):
        """Create a table if it doesn't exist"""
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        try:
            self.client.get_table(table_id)
        except exceptions.NotFound:
            table = bigquery.Table(table_id, schema=schema)
            self.client.create_table(table)
            print(f"Created table {table_id}")
    
    def add_instrument(self, symbol: str, name: str, instrument_type: str, 
                       sector: str = None, notes: str = None, quantity: float = 0.0) -> bool:
        """Add or update an instrument"""
        if not self.client:
            return False
        
        table_id = f"{self.project_id}.{self.dataset_id}.instruments"
        
        # Check if exists
        query = f"""
            SELECT symbol, is_active FROM `{table_id}`
            WHERE symbol = @symbol
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("symbol", "STRING", symbol)
            ]
        )
        
        results = list(self.client.query(query, job_config=job_config))
        
        if results:
            # Update existing
            update_query = f"""
                UPDATE `{table_id}`
                SET is_active = TRUE,
                    name = @name,
                    instrument_type = @instrument_type,
                    sector = @sector,
                    quantity = @quantity,
                    notes = @notes,
                    last_updated = CURRENT_TIMESTAMP()
                WHERE symbol = @symbol
            """
        else:
            # Insert new
            update_query = f"""
                INSERT INTO `{table_id}` (
                    symbol, name, instrument_type, sector, quantity, is_active, 
                    added_date, last_updated, notes
                )
                VALUES (
                    @symbol, @name, @instrument_type, @sector, @quantity, TRUE,
                    CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), @notes
                )
            """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
                bigquery.ScalarQueryParameter("name", "STRING", name),
                bigquery.ScalarQueryParameter("instrument_type", "STRING", instrument_type),
                bigquery.ScalarQueryParameter("sector", "STRING", sector),
                bigquery.ScalarQueryParameter("quantity", "FLOAT64", quantity),
                bigquery.ScalarQueryParameter("notes", "STRING", notes),
            ]
        )
        
        self.client.query(update_query, job_config=job_config).result()
        return True
    
    def get_instruments(self, active_only: bool = True) -> List[Dict]:
        """Get all instruments"""
        if not self.client:
            return []
        
        table_id = f"{self.project_id}.{self.dataset_id}.instruments"
        query = f"""
            SELECT symbol, name, instrument_type as type, sector, added_date, notes
            FROM `{table_id}`
            WHERE is_active = TRUE
        """ if active_only else f"""
            SELECT symbol, name, instrument_type as type, sector, added_date, notes
            FROM `{table_id}`
        """
        
        results = self.client.query(query).result()
        return [dict(row) for row in results]
    
    def remove_instrument(self, symbol: str) -> bool:
        """Soft delete an instrument"""
        if not self.client:
            return False
        
        table_id = f"{self.project_id}.{self.dataset_id}.instruments"
        query = f"""
            UPDATE `{table_id}`
            SET is_active = FALSE
            WHERE symbol = @symbol
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("symbol", "STRING", symbol)
            ]
        )
        
        self.client.query(query, job_config=job_config).result()
        return True
    
    def update_instrument_quantity(self, symbol: str, quantity: float) -> bool:
        """Update an instrument's quantity"""
        if not self.client:
            return False
        
        table_id = f"{self.project_id}.{self.dataset_id}.instruments"
        query = f"""
            UPDATE `{table_id}`
            SET quantity = @quantity
            WHERE symbol = @symbol
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
                bigquery.ScalarQueryParameter("quantity", "FLOAT64", quantity)
            ]
        )
        
        self.client.query(query, job_config=job_config).result()
        return True
    
    def insert_price_data(self, df: pd.DataFrame) -> bool:
        """Insert price data from DataFrame"""
        if not self.client or df.empty:
            return False
        
        table_id = f"{self.project_id}.{self.dataset_id}.price_data"
        
        # Add created_at timestamp
        df['created_at'] = datetime.utcnow()
        
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("symbol", "STRING"),
                bigquery.SchemaField("date", "TIMESTAMP"),
                bigquery.SchemaField("open_price", "FLOAT64"),
                bigquery.SchemaField("high_price", "FLOAT64"),
                bigquery.SchemaField("low_price", "FLOAT64"),
                bigquery.SchemaField("close_price", "FLOAT64"),
                bigquery.SchemaField("volume", "FLOAT64"),
                bigquery.SchemaField("created_at", "TIMESTAMP"),
            ],
            write_disposition="WRITE_APPEND",
        )
        
        job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        return True
    
    def get_price_data(self, symbol: str, start_date: datetime = None, 
                       end_date: datetime = None) -> pd.DataFrame:
        """Get price data for a symbol"""
        if not self.client:
            return pd.DataFrame()
        
        table_id = f"{self.project_id}.{self.dataset_id}.price_data"
        
        where_clauses = ["symbol = @symbol"]
        params = [bigquery.ScalarQueryParameter("symbol", "STRING", symbol)]
        
        if start_date:
            where_clauses.append("date >= @start_date")
            params.append(bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date))
        
        if end_date:
            where_clauses.append("date <= @end_date")
            params.append(bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date))
        
        query = f"""
            SELECT date, open_price as open, high_price as high, 
                   low_price as low, close_price as close, volume
            FROM `{table_id}`
            WHERE {" AND ".join(where_clauses)}
            ORDER BY date
        """
        
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        df = self.client.query(query, job_config=job_config).to_dataframe()
        
        if not df.empty:
            df.set_index('date', inplace=True)
        
        return df
    
    def get_latest_prices(self, symbols: List[str]) -> Dict:
        """Get latest prices for multiple symbols"""
        if not self.client:
            return {}
        
        table_id = f"{self.project_id}.{self.dataset_id}.price_data"
        
        query = f"""
            WITH RankedPrices AS (
                SELECT symbol, date, close_price,
                       ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC) as rn
                FROM `{table_id}`
                WHERE symbol IN UNNEST(@symbols)
            )
            SELECT symbol, date, close_price as close
            FROM RankedPrices
            WHERE rn = 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("symbols", "STRING", symbols)
            ]
        )
        
        results = self.client.query(query, job_config=job_config).result()
        return {row['symbol']: {'close': row['close'], 'date': row['date']} for row in results}
    
    def is_available(self) -> bool:
        """Check if BigQuery is available"""
        return self.client is not None
