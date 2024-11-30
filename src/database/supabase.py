from typing import Any, Dict, List, Optional, Union

from supabase import create_client, Client
from src.core.config import get_settings
from src.utils.logging import SingletonLogger


class SupabaseDatabase:
    """
    A simple abstraction layer for Supabase database operations.
    Provides basic CRUD (Create, Read, Update, Delete) functionality.
    """

    def __init__(self):
        """
        Initialize Supabase client using configuration settings.
        """
        settings = get_settings()
        self.url = str(settings.supabase_url)
        self.key = settings.supabase_key.get_secret_value()

        self.client: Client = create_client(self.url, self.key)
        self.logger = SingletonLogger().get_logger()

    def insert(
        self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Insert one or multiple records into a specified table.

        :param table: Name of the Supabase table
        :param data: Single record or list of records to insert
        :return: Inserted records
        """
        try:
            response = self.client.table(table).insert(data).execute()
            self.logger.info(f"Inserted {len(response.data)} record(s) into {table}")
            return response.data
        except Exception as e:
            self.logger.error(f"Error inserting into {table}: {e}")
            raise

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        single: bool = False,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Select records from a specified table with optional filtering.

        :param table: Name of the Supabase table
        :param columns: Columns to select (default is all)
        :param filters: Dictionary of column-value filters
        :param single: Whether to return a single record
        :return: Selected record(s)
        """
        try:
            query = self.client.table(table).select(columns)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            response = query.execute()

            if single:
                result = response.data[0] if response.data else None
            else:
                result = response.data

            self.logger.info(f"Selected {len(response.data)} record(s) from {table}")
            return result
        except Exception as e:
            self.logger.error(f"Error selecting from {table}: {e}")
            raise

    def update(
        self, table: str, data: Dict[str, Any], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Update records in a specified table matching given filters.

        :param table: Name of the Supabase table
        :param data: Dictionary of columns to update
        :param filters: Dictionary of column-value filters to identify records
        :return: Updated records
        """
        try:
            query = self.client.table(table)
            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.update(data).execute()

            self.logger.info(f"Updated {len(response.data)} record(s) in {table}")
            return response.data
        except Exception as e:
            self.logger.error(f"Error updating {table}: {e}")
            raise

    def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Delete records from a specified table matching given filters.

        :param table: Name of the Supabase table
        :param filters: Dictionary of column-value filters to identify records
        :return: Deleted records
        """
        try:
            query = self.client.table(table)
            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.delete().execute()

            self.logger.info(f"Deleted {len(response.data)} record(s) from {table}")
            return response.data
        except Exception as e:
            self.logger.error(f"Error deleting from {table}: {e}")
            raise

    def upsert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        on_conflict: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Insert or update records based on conflict resolution.

        :param table: Name of the Supabase table
        :param data: Single record or list of records to upsert
        :param on_conflict: Column to use for conflict resolution
        :return: Upserted records
        """
        try:
            query = self.client.table(table).upsert(data)

            if on_conflict:
                query = query.on_conflict(on_conflict)

            response = query.execute()

            self.logger.info(f"Upserted {len(response.data)} record(s) into {table}")
            return response.data
        except Exception as e:
            self.logger.error(f"Error upserting into {table}: {e}")
            raise
