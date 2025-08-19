from typing import Generic, List, Dict, Any, Type, TypeVar, Optional, Union
from sqlalchemy import func, desc, asc, and_
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import DeclarativeBase

from database.database import session
from .utils import (
    QueryOperator,
    SortDirection,
    AggregateFunction,
    JoinMode,
    SearchOptions,
    PaginationOptions,
)
from .query_strategies import (
    Query,
    InnerJoinStrategy,
    LeftJoinStrategy,
    RightJoinStrategy,
    FullJoinStrategy
)

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseController(Generic[ModelType]):
    """
    Generic controller class for managing database operations.
    
    Attributes:
        model: SQLAlchemy model class
    """

    def __init__(self, model: Type[ModelType]):
        """Initialize controller with model class."""
        self.model = model

    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        try:
            instance = self.model(**kwargs)
            session.add(instance)
            session.commit()
            return instance
        except IntegrityError:
            session.rollback()
            raise RecordAlreadyExistsError(
                "A record with these values already exists"
            )
        except SQLAlchemyError as e:
            session.rollback()
            raise
        finally:
            session.close()

    def bulk_create(self, items: List[Dict]) -> List[ModelType]:
        """Bulk create multiple records."""
        try:
            instances = [self.model(**item) for item in items]
            session.bulk_save_objects(instances)
            session.commit()
            return instances
        except SQLAlchemyError as e:
            session.rollback()
            raise
        finally:
            session.close()

    def get_by_id(self, id_: int) -> ModelType:
        """Get record by ID."""
        try:
            instance = session.query(self.model).get(id_)
            if not instance:
                raise RecordNotFoundError(f"Record with id {id_} not found")
            return instance
        except SQLAlchemyError as e:
            raise
        finally:
            session.close()

    def get_all(
        self, 
        options: Optional[SearchOptions] = None
    ) -> List[ModelType]:
        """
        Get all records with optional search options.
        
        Args:
            options: Search configuration
        """
        try:
            query = session.query(self.model)

            if options:
                if options.filters:
                    query = self._apply_filters(query, options.filters)

                if options.order_by:
                    order_column = getattr(self.model, options.order_by)
                    query = query.order_by(
                        desc(order_column) 
                        if options.direction == SortDirection.DESCENDING 
                        else asc(order_column)
                    )

                if options.offset:
                    query = query.offset(options.offset)
                    
                if options.limit:
                    query = query.limit(options.limit)

            return query.all()
        finally:
            session.close()

    def update(self, id_: int, **kwargs) -> ModelType:
        """Update record by ID."""
        try:
            invalid_fields = [
                field for field in kwargs.keys() 
                if not hasattr(self.model, field)
            ]
            if invalid_fields:
                raise ValueError(f"Invalid fields: {', '.join(invalid_fields)}")

            rows_updated = (
                session.query(self.model)
                .filter(self.model.id == id_)
                .update(kwargs, synchronize_session=False)
            )
            
            if rows_updated == 0:
                raise RecordNotFoundError(f"Record with id {id_} not found")
                
            session.commit()
            return self.get_by_id(id_)
            
        except (RecordNotFoundError, ValueError):
            session.rollback()
            raise
        except SQLAlchemyError as e:
            session.rollback()
            raise
        finally:
            session.close()
            
    def bulk_update(self, items: List[Dict[str, Any]]) -> bool:
        """
        Bulk update multiple records.
        
        Args:
            items: List of dictionaries containing id and update data
        """
        try:
            for item in items:
                if 'id' not in item:
                    raise ValueError("Each item must have an 'id' field")
                
                id_ = item.pop('id')
                self.update(id_, **item)
                
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, id_: int) -> bool:
        """Delete a record by ID."""
        try:
            instance = self.get_by_id(id_)
            session.delete(instance)
            session.commit()
            return True
        except RecordNotFoundError:
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_all(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Delete multiple records based on filters.
        
        Args:
            filters: Optional filters to apply before deletion
            
        Returns:
            Number of records deleted
        """
        try:
            query = session.query(self.model)
            
            if filters:
                query = self._apply_filters(query, filters)
                
            rows_deleted = query.delete(synchronize_session=False)
            session.commit()
            return rows_deleted
        except SQLAlchemyError as e:
            session.rollback()
            raise
        finally:
            session.close()

    def find_by_attributes(self, **kwargs) -> List[ModelType]:
        """
        Flexible search by attributes with operators.
        
        Example:
            >>> controller.find_by_attributes(
            ...     name__like='John',
            ...     age__gt=18
            ... )
        """
        try:
            query = session.query(self.model)
            filters = []
            
            for key, value in kwargs.items():
                if '__' in key:
                    field, operator = key.split('__')
                    if hasattr(self.model, field):
                        column = getattr(self.model, field)
                        operator_map = self._get_operator_mapping(column)
                        
                        if operator in operator_map:
                            filters.append(operator_map[operator](value))
                else:
                    if hasattr(self.model, key):
                        filters.append(getattr(self.model, key) == value)
                        
            return query.filter(and_(*filters)).all()
        finally:
            session.close()

    def paginate(self, options: PaginationOptions) -> Dict[str, Any]:
        """
        Get paginated results.
        
        Args:
            options: Pagination configuration
            
        Returns:
            Dictionary containing items and pagination metadata
        """
        try:
            query = session.query(self.model)
            
            if options.filters:
                query = self._apply_filters(query, options.filters)
                
            total = query.count()
            
            if options.order_by:
                column = getattr(self.model, options.order_by)
                query = query.order_by(
                    desc(column) 
                    if options.direction == SortDirection.DESCENDING 
                    else asc(column)
                )
                
            offset = (options.page - 1) * options.per_page
            items = query.offset(offset).limit(options.per_page).all()
            
            return {
                "items": items,
                "total": total,
                "page": options.page,
                "per_page": options.per_page,
                "pages": (total + options.per_page - 1) // options.per_page
            }
        finally:
            session.close()
            
    def aggregate(self, field: str, operation: AggregateFunction = AggregateFunction.COUNT) -> Any:
        """
        Perform aggregate operations on a field.
        
        Args:
            field: Field name to aggregate
            operation: Type of aggregate function to apply
            
        Returns:
            Result of the aggregate operation
            
        Raises:
            ValueError: If field doesn't exist
        """
        try:
            if not hasattr(self.model, field):
                raise ValueError(f"Field {field} does not exist")
                
            column = getattr(self.model, field)
            query = session.query(self.model)
            
            aggregate_functions = {
                AggregateFunction.COUNT: func.count,
                AggregateFunction.SUM: func.sum,
                AggregateFunction.AVERAGE: func.avg,
                AggregateFunction.MAXIMUM: func.max,
                AggregateFunction.MINIMUM: func.min
            }
            
            return query.with_entities(aggregate_functions[operation](column)).scalar()
        finally:
            session.close()

    def get_related_model(self, foreign_key_column_name: str) -> Optional[Type[DeclarativeBase]]:
        """
        Get the related model class for a foreign key.
        
        Args:
            foreign_key_column_name: Name of the foreign key column
            
        Returns:
            Related model class or None if not found
        """
        try:
            relationships = inspect(self.model).relationships
            for rel in relationships:
                if rel.key == foreign_key_column_name:
                    return rel.mapper.class_
            return None
        except SQLAlchemyError:
            return None

    def get_related_items(
        self, 
        foreign_key_column_name: str,
        join_mode: JoinMode = JoinMode.LEFT,
        options: Optional[SearchOptions] = None
    ) -> List[Any]:
        """Get related items for a relationship."""
        try:
            related_model = self.get_related_model(foreign_key_column_name)
            if not related_model:
                raise ValueError(f"No relationship found for {foreign_key_column_name}")

            query = session.query(related_model)
            
            # Mapping des stratégies de jointure
            join_strategies = {
                JoinMode.INNER: InnerJoinStrategy(),
                JoinMode.LEFT: LeftJoinStrategy(),
                JoinMode.RIGHT: RightJoinStrategy(),
                JoinMode.FULL: FullJoinStrategy(),
            }
            
            # Application de la stratégie de jointure
            strategy = join_strategies.get(join_mode, LeftJoinStrategy())
            query = strategy.apply_join(query, self.model)
            
            if options:
                query = self._apply_search_options(query, options, related_model)
                    
            return query.all()
        finally:
            session.close()

    def _apply_search_options(self, query: Query, options: SearchOptions, model: Any) -> Query:
        """Apply search options to query."""
        if options.filters:
            query = self._apply_filters(query, options.filters)
            
        if options.order_by:
            order_column = getattr(model, options.order_by)
            query = query.order_by(
                desc(order_column) 
                if options.direction == SortDirection.DESCENDING 
                else asc(order_column)
            )
            
        if options.offset:
            query = query.offset(options.offset)
            
        if options.limit:
            query = query.limit(options.limit)
            
        return query

    def _apply_filters(self, query: Any, filters: Dict[str, Any]) -> Any:
        """
        Apply filters to a query.
        
        Args:
            query: SQLAlchemy query object
            filters: Dictionary of filters to apply
            
        Returns:
            Modified query with filters applied
        """
        for key, value in filters.items():
            if isinstance(value, (list, tuple)):
                query = query.filter(getattr(self.model, key).in_(value))
            else:
                query = query.filter(getattr(self.model, key) == value)
        return query

    def _validate_fields(self, fields: List[str]) -> List[str]:
        """
        Validate field names against model attributes.
        
        Args:
            fields: List of field names to validate
            
        Returns:
            List of invalid field names
        """
        return [
            field for field in fields 
            if not hasattr(self.model, field)
        ]

    def _get_order_columns(self) -> List[str]:
        """
        Get columns that can be used for ordering.
        
        Returns:
            List of column names that support ordering
        """
        return [
            column.name 
            for column in self.model.__table__.columns 
            if column.info.get("order_column", False)
        ]

    def _validate_order_by(self, field: str) -> bool:
        """
        Validate if a field can be used for ordering.
        
        Args:
            field: Field name to validate
            
        Returns:
            True if field is valid for ordering
        """
        return (
            hasattr(self.model, field) and 
            field in self._get_order_columns()
        )

    @staticmethod
    def _validate_pagination(page: int, per_page: int) -> None:
        """
        Validate pagination parameters.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Raises:
            ValueError: If parameters are invalid
        """
        if page < 1:
            raise ValueError("Page number must be greater than 0")
        if per_page < 1:
            raise ValueError("Items per page must be greater than 0")

    @staticmethod
    def _calculate_offset(page: int, per_page: int) -> int:
        """
        Calculate offset for pagination.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Offset value
        """
        return (page - 1) * per_page

    def _get_operator_mapping(self, column):
        """Get mapping of operators to their corresponding filter functions."""
        return {
            QueryOperator.LIKE: lambda v: column.like(f'%{v}%'),
            QueryOperator.ILIKE: lambda v: column.ilike(f'%{v}%'),
            QueryOperator.IN: lambda v: column.in_(v),
            QueryOperator.NOT_IN: lambda v: ~column.in_(v),
            QueryOperator.GREATER_THAN: lambda v: column > v,
            QueryOperator.LESS_THAN: lambda v: column < v,
            QueryOperator.GREATER_EQUAL: lambda v: column >= v,
            QueryOperator.LESS_EQUAL: lambda v: column <= v,
            QueryOperator.NOT_EQUAL: lambda v: column != v,
            QueryOperator.EQUAL: lambda v: column == v,
        }
    
    
"""Custom exceptions for the controllers module."""

class RecordNotFoundError(Exception):
    """Exception raised when a record is not found."""
    pass

class RecordAlreadyExistsError(Exception):
    """Exception raised when attempting to create a record that already exists."""
    pass

class InvalidFieldError(Exception):
    """Exception raised when invalid fields are provided."""
    pass

class DatabaseOperationError(Exception):
    """Exception raised for general database operation errors."""
    pass