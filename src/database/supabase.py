from typing import Any, Dict, List, Optional, Union, Callable
from contextlib import contextmanager
from datetime import datetime, timedelta

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from pydantic import BaseModel, ValidationError

from src.core.config import get_settings
from src.utils.logging import SingletonLogger


class DatabaseError(Exception):
    """Custom exception for database-related errors."""

    pass


class SupabaseDatabase:
    """
    Advanced abstraction layer for Supabase database operations.
    Provides enhanced CRUD functionality with additional features.
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize Supabase client with configurable timeout and advanced options.

        :param timeout: Request timeout in seconds
        """
        settings = get_settings()
        self.url = str(settings.supabase_url)
        self.key = settings.supabase_key.get_secret_value()

        # Configure client with custom options
        options = ClientOptions(postgrest_client_timeout=timeout, supabase_key=self.key)
        self.client: Client = create_client(self.url, self.key, options)
        self.logger = SingletonLogger().get_logger()

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        Provides a way to group multiple operations.
        """
        try:
            yield self
            # In Supabase, transactions are typically handled at the database level
            self.logger.info("Transaction completed successfully")
        except Exception as e:
            self.logger.error(f"Transaction failed: {e}")
            raise DatabaseError(f"Transaction failed: {e}")

    def validate_data(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        model: Optional[type[BaseModel]] = None,
    ):
        """
        Validate input data against a Pydantic model.

        :param data: Data to validate
        :param model: Pydantic model for validation
        :return: Validated data
        """
        if model is None:
            return data

        try:
            if isinstance(data, list):
                return [model(**item).model_dump() for item in data]
            return model(**data).model_dump()
        except ValidationError as e:
            self.logger.error(f"Data validation failed: {e}")
            raise DatabaseError(f"Invalid data: {e}")

    def insert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        model: Optional[type[BaseModel]] = None,
        returning: str = "*",
    ) -> List[Dict[str, Any]]:
        """
        Enhanced insert method with optional data validation and custom returning.

        :param table: Name of the Supabase table
        :param data: Single record or list of records to insert
        :param model: Optional Pydantic model for data validation
        :param returning: Columns to return after insertion
        :return: Inserted records
        """
        validated_data = self.validate_data(data, model)

        try:
            response = (
                self.client.table(table)
                .insert(validated_data)
                .select(returning)
                .execute()
            )

            self.logger.info(f"Inserted {len(response.data)} record(s) into {table}")
            return response.data
        except Exception as e:
            self.logger.error(f"Error inserting into {table}: {e}")
            raise DatabaseError(f"Insert failed: {e}")

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        single: bool = False,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        range_filter: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Advanced select method with additional filtering and sorting options.

        :param table: Name of the Supabase table
        :param columns: Columns to select
        :param filters: Exact match filters
        :param single: Whether to return a single record
        :param order_by: Column to order results by
        :param limit: Maximum number of records to return
        :param range_filter: Range-based filtering
        :return: Selected record(s)
        """
        try:
            query = self.client.table(table).select(columns)

            # Apply exact match filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            # Apply range filters
            if range_filter:
                for key, (start, end) in range_filter.items():
                    query = query.gte(key, start).lte(key, end)

            # Apply ordering
            if order_by:
                query = query.order(order_by)

            # Apply limit
            if limit:
                query = query.limit(limit)

            response = query.execute()

            if single:
                result = response.data[0] if response.data else None
            else:
                result = response.data

            self.logger.info(f"Selected {len(response.data)} record(s) from {table}")
            return result
        except Exception as e:
            self.logger.error(f"Error selecting from {table}: {e}")
            raise DatabaseError(f"Select failed: {e}")

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any],
        model: Optional[type[BaseModel]] = None,
        returning: str = "*",
    ) -> List[Dict[str, Any]]:
        """
        Enhanced update method with validation and custom returning.

        :param table: Name of the Supabase table
        :param data: Dictionary of columns to update
        :param filters: Dictionary of column-value filters
        :param model: Optional Pydantic model for data validation
        :param returning: Columns to return after update
        :return: Updated records
        """
        validated_data = self.validate_data(data, model)

        try:
            query = self.client.table(table)
            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.update(validated_data).select(returning).execute()

            self.logger.info(f"Updated {len(response.data)} record(s) in {table}")
            return response.data
        except Exception as e:
            self.logger.error(f"Error updating {table}: {e}")
            raise DatabaseError(f"Update failed: {e}")

    def delete(
        self, table: str, filters: Dict[str, Any], returning: str = "*"
    ) -> List[Dict[str, Any]]:
        """
        Enhanced delete method with custom returning.

        :param table: Name of the Supabase table
        :param filters: Dictionary of column-value filters
        :param returning: Columns to return after deletion
        :return: Deleted records
        """
        try:
            query = self.client.table(table)
            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.delete().select(returning).execute()

            self.logger.info(f"Deleted {len(response.data)} record(s) from {table}")
            return response.data
        except Exception as e:
            self.logger.error(f"Error deleting from {table}: {e}")
            raise DatabaseError(f"Delete failed: {e}")

    def upsert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        on_conflict: Optional[str] = None,
        model: Optional[type[BaseModel]] = None,
        returning: str = "*",
    ) -> List[Dict[str, Any]]:
        """
        Enhanced upsert method with validation and custom returning.

        :param table: Name of the Supabase table
        :param data: Single record or list of records to upsert
        :param on_conflict: Column to use for conflict resolution
        :param model: Optional Pydantic model for data validation
        :param returning: Columns to return after upsert
        :return: Upserted records
        """
        validated_data = self.validate_data(data, model)

        try:
            query = self.client.table(table).upsert(validated_data)

            if on_conflict:
                query = query.on_conflict(on_conflict)

            response = query.select(returning).execute()

            self.logger.info(f"Upserted {len(response.data)} record(s) into {table}")
            return response.data
        except Exception as e:
            self.logger.error(f"Error upserting into {table}: {e}")
            raise DatabaseError(f"Upsert failed: {e}")

    def bulk_operation(
        self, operations: List[Callable[[], Any]], stop_on_error: bool = False
    ) -> List[Any]:
        """
        Perform multiple database operations in sequence.

        :param operations: List of database operation functions
        :param stop_on_error: Whether to stop on first error or continue
        :return: List of operation results
        """
        results = []
        for op in operations:
            try:
                result = op()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Bulk operation failed: {e}")
                if stop_on_error:
                    raise DatabaseError(f"Bulk operation failed: {e}")
        return results
