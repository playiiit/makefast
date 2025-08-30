from typing import List, Dict, Any, Optional, Union, Set
from fastapi import HTTPException
from mysql.connector import Error
import datetime
import re
from contextlib import contextmanager


class SecurityValidator:
    """Security validation utilities"""

    # Valid SQL identifier pattern (letters, numbers, underscores)
    VALID_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    # Valid operators whitelist
    VALID_OPERATORS = {
        '=', '!=', '<>', '<', '>', '<=', '>=',
        'LIKE', 'NOT LIKE', 'IN', 'NOT IN',
        'IS', 'IS NOT', 'BETWEEN', 'NOT BETWEEN'
    }

    # Valid sort directions
    VALID_DIRECTIONS = {'ASC', 'DESC'}

    @classmethod
    def validate_identifier(cls, identifier: str) -> bool:
        """Validate SQL identifier (table/column names)"""
        if not identifier or len(identifier) > 64:  # MySQL max identifier length
            return False
        return bool(cls.VALID_IDENTIFIER_PATTERN.match(identifier))

    @classmethod
    def validate_operator(cls, operator: str) -> bool:
        """Validate SQL operator"""
        return operator.upper() in cls.VALID_OPERATORS

    @classmethod
    def validate_direction(cls, direction: str) -> bool:
        """Validate sort direction"""
        return direction.upper() in cls.VALID_DIRECTIONS

    @classmethod
    def sanitize_identifier(cls, identifier: str) -> str:
        """Sanitize and validate identifier, raise exception if invalid"""
        if not cls.validate_identifier(identifier):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid identifier: {identifier}"
            )
        return identifier

    @classmethod
    def sanitize_operator(cls, operator: str) -> str:
        """Sanitize and validate operator"""
        operator = operator.upper()
        if not cls.validate_operator(operator):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operator: {operator}"
            )
        return operator

    @classmethod
    def sanitize_direction(cls, direction: str) -> str:
        """Sanitize and validate sort direction"""
        direction = direction.upper()
        if not cls.validate_direction(direction):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort direction: {direction}"
            )
        return direction


class QueryBuilder:
    def __init__(self, model_class):
        self.model_class = model_class
        self.where_conditions = []
        self.where_params = []
        self.order_conditions = []
        self.limit_count = None
        self.offset_count = 0
        self._validate_model()

    def _validate_model(self):
        """Validate model configuration"""
        if not hasattr(self.model_class, 'table_name') or not self.model_class.table_name:
            raise HTTPException(status_code=500, detail="Model must have table_name")

        if not SecurityValidator.validate_identifier(self.model_class.table_name):
            raise HTTPException(
                status_code=500,
                detail=f"Invalid table name: {self.model_class.table_name}"
            )

    def _validate_column(self, column: str):
        """Validate column name against model's allowed columns"""
        # Sanitize the column name
        column = SecurityValidator.sanitize_identifier(column)

        # Check if column is in model's allowed columns (if defined)
        if hasattr(self.model_class, 'columns') and self.model_class.columns:
            if column not in self.model_class.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column '{column}' not allowed for model {self.model_class.__name__}"
                )

        return column

    def where(self, column: str, operator: str = "=", value: Any = None):
        """Add a WHERE condition with proper validation"""
        if value is None:
            value = operator
            operator = "="

        # Validate inputs
        column = self._validate_column(column)
        operator = SecurityValidator.sanitize_operator(operator)

        # Use backticks for column names to prevent SQL injection
        self.where_conditions.append(f"`{column}` {operator} %s")
        self.where_params.append(value)
        return self

    def where_in(self, column: str, values: List[Any]):
        """Add WHERE IN condition"""
        if not values:
            raise HTTPException(status_code=400, detail="Values list cannot be empty for IN clause")

        column = self._validate_column(column)
        placeholders = ', '.join(['%s'] * len(values))
        self.where_conditions.append(f"`{column}` IN ({placeholders})")
        self.where_params.extend(values)
        return self

    def where_not_in(self, column: str, values: List[Any]):
        """Add WHERE NOT IN condition"""
        if not values:
            raise HTTPException(status_code=400, detail="Values list cannot be empty for NOT IN clause")

        column = self._validate_column(column)
        placeholders = ', '.join(['%s'] * len(values))
        self.where_conditions.append(f"`{column}` NOT IN ({placeholders})")
        self.where_params.extend(values)
        return self

    def where_null(self, column: str):
        """Add WHERE IS NULL condition"""
        column = self._validate_column(column)
        self.where_conditions.append(f"`{column}` IS NULL")
        return self

    def where_not_null(self, column: str):
        """Add WHERE IS NOT NULL condition"""
        column = self._validate_column(column)
        self.where_conditions.append(f"`{column}` IS NOT NULL")
        return self

    def where_between(self, column: str, start: Any, end: Any):
        """Add WHERE BETWEEN condition"""
        column = self._validate_column(column)
        self.where_conditions.append(f"`{column}` BETWEEN %s AND %s")
        self.where_params.extend([start, end])
        return self

    def where_not_between(self, column: str, start: Any, end: Any):
        """Add WHERE NOT BETWEEN condition"""
        column = self._validate_column(column)
        self.where_conditions.append(f"`{column}` NOT BETWEEN %s AND %s")
        self.where_params.extend([start, end])
        return self

    def where_like(self, column: str, pattern: str):
        """Add WHERE LIKE condition"""
        column = self._validate_column(column)
        self.where_conditions.append(f"`{column}` LIKE %s")
        self.where_params.append(pattern)
        return self

    def where_not_like(self, column: str, pattern: str):
        """Add WHERE NOT LIKE condition"""
        column = self._validate_column(column)
        self.where_conditions.append(f"`{column}` NOT LIKE %s")
        self.where_params.append(pattern)
        return self

    def or_where(self, column: str, operator: str = "=", value: Any = None):
        """Add OR WHERE condition"""
        if value is None:
            value = operator
            operator = "="

        column = self._validate_column(column)
        operator = SecurityValidator.sanitize_operator(operator)

        if self.where_conditions:
            # Replace the last condition with OR grouped condition
            last_condition = self.where_conditions[-1]
            self.where_conditions[-1] = f"({last_condition} OR `{column}` {operator} %s)"
        else:
            self.where_conditions.append(f"`{column}` {operator} %s")

        self.where_params.append(value)
        return self

    def order_by(self, column: str, direction: str = "ASC"):
        """Add ORDER BY clause with validation"""
        column = self._validate_column(column)
        direction = SecurityValidator.sanitize_direction(direction)

        # Use backticks for column names
        self.order_conditions.append(f"`{column}` {direction}")
        return self

    def limit(self, count: int):
        """Add LIMIT clause"""
        if not isinstance(count, int) or count < 0:
            raise HTTPException(status_code=400, detail="Limit must be a non-negative integer")
        if count > 10000:  # Reasonable upper limit
            raise HTTPException(status_code=400, detail="Limit cannot exceed 10000")

        self.limit_count = count
        return self

    def offset(self, count: int):
        """Add OFFSET clause"""
        if not isinstance(count, int) or count < 0:
            raise HTTPException(status_code=400, detail="Offset must be a non-negative integer")

        self.offset_count = count
        return self

    def _build_query(self, base_query: str) -> tuple[str, List[Any]]:
        """Build the complete query with conditions"""
        query = base_query

        if self.where_conditions:
            where_clause = " AND ".join(self.where_conditions)
            query += f" WHERE {where_clause}"

        if self.order_conditions:
            order_clause = ", ".join(self.order_conditions)
            query += f" ORDER BY {order_clause}"

        if self.limit_count is not None:
            query += f" LIMIT {self.limit_count}"
            if self.offset_count > 0:
                query += f" OFFSET {self.offset_count}"

        return query, self.where_params

    async def get(self) -> List[Dict[str, Any]]:
        """Execute the query and return results"""
        table_name = SecurityValidator.sanitize_identifier(self.model_class.table_name)
        base_query = f"SELECT * FROM `{table_name}`"
        query, params = self._build_query(base_query)

        with self.model_class.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params)
                return cursor.fetchall()
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    async def first(self) -> Optional[Dict[str, Any]]:
        """Get the first result"""
        self.limit_count = 1
        results = await self.get()
        return results[0] if results else None

    async def first_or_fail(self) -> Dict[str, Any]:
        """Get the first result or raise exception"""
        result = await self.first()
        if result is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return result

    async def count(self) -> int:
        """Count the results"""
        table_name = SecurityValidator.sanitize_identifier(self.model_class.table_name)
        base_query = f"SELECT COUNT(*) as count FROM `{table_name}`"
        query, params = self._build_query(base_query)

        with self.model_class.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result['count'] if result else 0
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    async def update(self, **kwargs) -> int:
        """Update records matching the query"""
        if not kwargs:
            raise HTTPException(status_code=400, detail="No data provided for update")

        data = self.model_class._prepare_data(kwargs, 'update')
        table_name = SecurityValidator.sanitize_identifier(self.model_class.table_name)

        # Validate all column names in the update data
        validated_data = {}
        for key, value in data.items():
            validated_key = self._validate_column(key)
            validated_data[validated_key] = value

        set_clause = ', '.join([f"`{key}` = %s" for key in validated_data.keys()])
        base_query = f"UPDATE `{table_name}` SET {set_clause}"

        update_params = list(validated_data.values())
        if self.where_conditions:
            where_clause = " AND ".join(self.where_conditions)
            base_query += f" WHERE {where_clause}"
            update_params.extend(self.where_params)

        with self.model_class.get_connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(base_query, update_params)
                connection.commit()
                return cursor.rowcount
            except Error as e:
                connection.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    async def delete(self) -> int:
        """Delete records matching the query"""
        if not self.where_conditions:
            raise HTTPException(
                status_code=400,
                detail="DELETE queries must have WHERE conditions for safety"
            )

        table_name = SecurityValidator.sanitize_identifier(self.model_class.table_name)
        base_query = f"DELETE FROM `{table_name}`"

        where_clause = " AND ".join(self.where_conditions)
        base_query += f" WHERE {where_clause}"

        with self.model_class.get_connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(base_query, self.where_params)
                connection.commit()
                return cursor.rowcount
            except Error as e:
                connection.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()


class MySQLBase:
    table_name: str = ""
    columns: List[str] = []  # REQUIRED: Define allowed columns for security
    fillable: List[str] = []
    guarded: List[str] = ['id']
    timestamps: bool = True
    primary_key: str = "id"
    _database = None

    @classmethod
    def set_database(cls, database):
        cls._database = database

    @classmethod
    def get_database(cls):
        return cls._database

    @classmethod
    @contextmanager
    def get_connection(cls):
        """Context manager for database connections"""
        connection = None
        try:
            connection = cls.get_database()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @classmethod
    def _prepare_data(cls, data: Dict[str, Any], operation: str = 'create') -> Dict[str, Any]:
        """Prepare data for database operations"""
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Data must be a dictionary")

        # Validate column names
        for key in data.keys():
            if not SecurityValidator.validate_identifier(key):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {key}")

        # Filter by fillable if defined
        if cls.fillable:
            data = {k: v for k, v in data.items() if k in cls.fillable}

        # Remove guarded fields
        for field in cls.guarded:
            data.pop(field, None)

        # Add timestamps
        if cls.timestamps:
            now = datetime.datetime.now()
            if operation == 'create' and 'created_at' not in data:
                data['created_at'] = now
            if 'updated_at' not in data and operation in ['create', 'update']:
                data['updated_at'] = now

        return data

    @classmethod
    def _validate_columns(cls, columns: List[str]) -> List[str]:
        """Validate and sanitize column names"""
        validated = []
        for col in columns:
            validated.append(SecurityValidator.sanitize_identifier(col))
        return validated

    # Basic CRUD Operations
    @classmethod
    async def create(cls, **kwargs) -> Dict[str, Any]:
        """Create a new record"""
        data = cls._prepare_data(kwargs, 'create')
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                columns = ', '.join([f"`{col}`" for col in data.keys()])
                placeholders = ', '.join(['%s'] * len(data))
                query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
                cursor.execute(query, list(data.values()))
                connection.commit()
                return await cls.find(cursor.lastrowid)
            except Error as e:
                connection.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def find(cls, id: int) -> Dict[str, Any]:
        """Find a record by ID"""
        if not isinstance(id, int) or id <= 0:
            raise HTTPException(status_code=400, detail="ID must be a positive integer")

        table_name = SecurityValidator.sanitize_identifier(cls.table_name)
        primary_key = SecurityValidator.sanitize_identifier(cls.primary_key)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT * FROM `{table_name}` WHERE `{primary_key}` = %s"
                cursor.execute(query, (id,))
                result = cursor.fetchone()
                if result is None:
                    raise HTTPException(status_code=404, detail="Record not found")
                return result
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def find_or_fail(cls, id: int) -> Dict[str, Any]:
        """Find a record by ID or raise exception"""
        return await cls.find(id)

    @classmethod
    async def first(cls) -> Optional[Dict[str, Any]]:
        """Get the first record"""
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT * FROM `{table_name}` LIMIT 1"
                cursor.execute(query)
                return cursor.fetchone()
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def first_or_fail(cls) -> Dict[str, Any]:
        """Get the first record or raise exception"""
        result = await cls.first()
        if result is None:
            raise HTTPException(status_code=404, detail="No records found")
        return result

    @classmethod
    async def all(cls) -> List[Dict[str, Any]]:
        """Get all records"""
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT * FROM `{table_name}`"
                cursor.execute(query)
                return cursor.fetchall()
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def update(cls, id: int, **kwargs) -> Dict[str, Any]:
        """Update a record"""
        if not isinstance(id, int) or id <= 0:
            raise HTTPException(status_code=400, detail="ID must be a positive integer")

        data = cls._prepare_data(kwargs, 'update')
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)
        primary_key = SecurityValidator.sanitize_identifier(cls.primary_key)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                set_clause = ', '.join([f"`{key}` = %s" for key in data.keys()])
                query = f"UPDATE `{table_name}` SET {set_clause} WHERE `{primary_key}` = %s"
                cursor.execute(query, list(data.values()) + [id])
                connection.commit()
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Record not found")
                return await cls.find(id)
            except Error as e:
                connection.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def delete(cls, id: int) -> Dict[str, bool]:
        """Delete a record"""
        if not isinstance(id, int) or id <= 0:
            raise HTTPException(status_code=400, detail="ID must be a positive integer")

        table_name = SecurityValidator.sanitize_identifier(cls.table_name)
        primary_key = SecurityValidator.sanitize_identifier(cls.primary_key)

        with cls.get_connection() as connection:
            cursor = connection.cursor()
            try:
                query = f"DELETE FROM `{table_name}` WHERE `{primary_key}` = %s"
                cursor.execute(query, (id,))
                connection.commit()
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Record not found")
                return {"success": True}
            except Error as e:
                connection.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    # Query Builder Methods
    @classmethod
    def query(cls):
        """Start a new query builder"""
        return QueryBuilder(cls)

    @classmethod
    async def where(cls, column: str, operator: str = "=", value: Any = None) -> List[Dict[str, Any]]:
        """Filter records by a condition"""
        return await cls.query().where(column, operator, value).get()

    @classmethod
    async def where_in(cls, column: str, values: List[Any]) -> List[Dict[str, Any]]:
        """Filter records by values in a list"""
        return await cls.query().where_in(column, values).get()

    @classmethod
    async def where_not_in(cls, column: str, values: List[Any]) -> List[Dict[str, Any]]:
        """Filter records by values not in a list"""
        return await cls.query().where_not_in(column, values).get()

    @classmethod
    async def where_null(cls, column: str) -> List[Dict[str, Any]]:
        """Filter records where column is null"""
        return await cls.query().where_null(column).get()

    @classmethod
    async def where_not_null(cls, column: str) -> List[Dict[str, Any]]:
        """Filter records where column is not null"""
        return await cls.query().where_not_null(column).get()

    @classmethod
    async def order_by(cls, column: str, direction: str = "ASC") -> List[Dict[str, Any]]:
        """Order records by a column"""
        return await cls.query().order_by(column, direction).get()

    @classmethod
    async def limit(cls, count: int, offset: int = 0) -> List[Dict[str, Any]]:
        """Limit the number of records"""
        return await cls.query().limit(count).offset(offset).get()

    @classmethod
    async def paginate(cls, page: int = 1, per_page: int = 15) -> Dict[str, Any]:
        """Paginate records"""
        if not isinstance(page, int) or page < 1:
            raise HTTPException(status_code=400, detail="Page must be a positive integer")
        if not isinstance(per_page, int) or per_page < 1 or per_page > 1000:
            raise HTTPException(status_code=400, detail="Per page must be between 1 and 1000")

        offset = (page - 1) * per_page
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                # Get total count
                count_query = f"SELECT COUNT(*) as total FROM `{table_name}`"
                cursor.execute(count_query)
                total = cursor.fetchone()['total']

                # Get paginated data
                data_query = f"SELECT * FROM `{table_name}` LIMIT %s OFFSET %s"
                cursor.execute(data_query, (per_page, offset))
                data = cursor.fetchall()

                return {
                    'data': data,
                    'total': total,
                    'per_page': per_page,
                    'current_page': page,
                    'last_page': (total + per_page - 1) // per_page,
                    'from': offset + 1 if data else 0,
                    'to': offset + len(data) if data else 0
                }
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    # Aggregate Methods
    @classmethod
    async def count(cls) -> int:
        """Count all records"""
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT COUNT(*) as count FROM `{table_name}`"
                cursor.execute(query)
                return cursor.fetchone()['count']
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def max(cls, column: str) -> Any:
        """Get maximum value of a column"""
        column = SecurityValidator.sanitize_identifier(column)
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT MAX(`{column}`) as max_value FROM `{table_name}`"
                cursor.execute(query)
                result = cursor.fetchone()
                return result['max_value'] if result else None
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def min(cls, column: str) -> Any:
        """Get minimum value of a column"""
        column = SecurityValidator.sanitize_identifier(column)
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT MIN(`{column}`) as min_value FROM `{table_name}`"
                cursor.execute(query)
                result = cursor.fetchone()
                return result['min_value'] if result else None
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def sum(cls, column: str) -> Any:
        """Get sum of a column"""
        column = SecurityValidator.sanitize_identifier(column)
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT SUM(`{column}`) as sum_value FROM `{table_name}`"
                cursor.execute(query)
                result = cursor.fetchone()
                return result['sum_value'] if result else None
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def avg(cls, column: str) -> Any:
        """Get average of a column"""
        column = SecurityValidator.sanitize_identifier(column)
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT AVG(`{column}`) as avg_value FROM `{table_name}`"
                cursor.execute(query)
                result = cursor.fetchone()
                return result['avg_value'] if result else None
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    # Utility Methods
    @classmethod
    async def exists(cls, id: int) -> bool:
        """Check if a record exists"""
        if not isinstance(id, int) or id <= 0:
            return False

        table_name = SecurityValidator.sanitize_identifier(cls.table_name)
        primary_key = SecurityValidator.sanitize_identifier(cls.primary_key)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT COUNT(*) as count FROM `{table_name}` WHERE `{primary_key}` = %s"
                cursor.execute(query, (id,))
                result = cursor.fetchone()
                return result['count'] > 0
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def where_multiple(cls, **kwargs) -> List[Dict[str, Any]]:
        """Filter by multiple conditions"""
        if not kwargs:
            raise HTTPException(status_code=400, detail="At least one condition must be provided")

        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                conditions = []
                values = []

                for key, value in kwargs.items():
                    # Validate column name
                    validated_key = SecurityValidator.sanitize_identifier(key)
                    if hasattr(cls, 'columns') and cls.columns and validated_key not in cls.columns:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Column '{validated_key}' not allowed for model {cls.__name__}"
                        )

                    conditions.append(f"`{validated_key}` = %s")
                    values.append(value)

                where_clause = " AND ".join(conditions)
                query = f"SELECT * FROM `{table_name}` WHERE {where_clause}"
                cursor.execute(query, values)
                return cursor.fetchall()
            except Error as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def get_or_create(cls, defaults: Dict[str, Any] = None, **kwargs) -> tuple[Dict[str, Any], bool]:
        """Get existing record or create new one"""
        try:
            # Try to find existing record
            records = await cls.where_multiple(**kwargs)
            if records:
                return records[0], False

            # Create new record
            create_data = {**kwargs}
            if defaults:
                create_data.update(defaults)

            new_record = await cls.create(**create_data)
            return new_record, True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @classmethod
    async def update_or_create(cls, defaults: Dict[str, Any] = None, **kwargs) -> tuple[Dict[str, Any], bool]:
        """Update existing record or create new one"""
        try:
            records = await cls.where_multiple(**kwargs)
            if records:
                # Update existing record
                record_id = records[0][cls.primary_key]
                update_data = defaults or {}
                updated_record = await cls.update(record_id, **update_data)
                return updated_record, False
            else:
                # Create new record
                create_data = {**kwargs}
                if defaults:
                    create_data.update(defaults)

                new_record = await cls.create(**create_data)
                return new_record, True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @classmethod
    async def bulk_create(cls, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple records in bulk"""
        if not data_list:
            raise HTTPException(status_code=400, detail="Data list cannot be empty")

        if len(data_list) > 1000:  # Reasonable limit
            raise HTTPException(status_code=400, detail="Bulk create limited to 1000 records")

        created_records = []
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                for data in data_list:
                    prepared_data = cls._prepare_data(data, 'create')
                    columns = ', '.join([f"`{col}`" for col in prepared_data.keys()])
                    placeholders = ', '.join(['%s'] * len(prepared_data))
                    query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
                    cursor.execute(query, list(prepared_data.values()))
                    created_records.append({**prepared_data, cls.primary_key: cursor.lastrowid})

                connection.commit()
                return created_records
            except Error as e:
                connection.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()

    @classmethod
    async def safe_raw_query(cls, query: str, params: tuple = None, allowed_operations: Set[str] = None) -> List[
        Dict[str, Any]]:
        """Execute raw SQL query with safety checks"""
        if not query or not isinstance(query, str):
            raise HTTPException(status_code=400, detail="Query must be a non-empty string")

        # Default allowed operations
        if allowed_operations is None:
            allowed_operations = {'SELECT'}

        # Normalize and check query type
        query_upper = query.strip().upper()
        operation = query_upper.split()[0] if query_upper else ""

        if operation not in allowed_operations:
            raise HTTPException(
                status_code=400,
                detail=f"Operation '{operation}' not allowed. Allowed: {', '.join(allowed_operations)}"
            )

        # Additional safety checks
        dangerous_keywords = {
            'DROP', 'TRUNCATE', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER',
            'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'UNION', 'LOAD_FILE', 'OUTFILE',
            'DUMPFILE', 'BENCHMARK', 'SLEEP'
        }

        if operation == 'SELECT':
            # Allow SELECT but check for dangerous keywords
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Dangerous keyword '{keyword}' not allowed in SELECT query"
                    )

        # Validate table name appears in query (basic check)
        table_name = SecurityValidator.sanitize_identifier(cls.table_name)
        if f"`{table_name}`" not in query and table_name not in query:
            raise HTTPException(
                status_code=400,
                detail=f"Query must reference the model's table: {table_name}"
            )

        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                if operation == 'SELECT':
                    return cursor.fetchall()
                else:
                    connection.commit()
                    return [{"affected_rows": cursor.rowcount}]
            except Error as e:
                if operation != 'SELECT':
                    connection.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            finally:
                cursor.close()
