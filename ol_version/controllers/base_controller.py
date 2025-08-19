from sqlalchemy import delete, and_, desc, asc, func
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import DeclarativeBase
from datetime import timedelta
from typing import Generic, List, Dict, Any, Type, TypeVar

from database.database import session

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseController(Generic[ModelType]):
    """
    A generic controller class for managing CRUD operations with SQLAlchemy.
    Provides a flexible interface for database operations regardless of the model.

    Attributes:
        model (Type[Base]): The SQLAlchemy model class associated with this controller.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize the BaseController with a specific SQLAlchemy model.

        Args:
            model (Type[Base]): The SQLAlchemy model class to use with this controller.
        """
        self.model = model

    def paginate(self, page: int = 1, per_page: int = 10, **filters):
        """
        Récupère une page de résultats avec pagination.
        
        Args:
            page: Numéro de la page
            per_page: Nombre d'éléments par page
            filters: Filtres à appliquer
        """
        try:
            query = session.query(self.model)
            
            # Appliquer les filtres
            if filters:
                query = self._apply_filters(query, filters)
                
            # Calculer l'offset
            offset = (page - 1) * per_page
            
            # Exécuter la requête
            total = query.count()
            items = query.offset(offset).limit(per_page).all()
            
            return {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        finally:
            session.close()

    def bulk_create(self, items: List[Dict]) -> List[ModelType]:
        """Création en masse d'enregistrements"""
        try:
            instances = [self.model(**item) for item in items]
            session.bulk_save_objects(instances)
            session.commit()
            return instances
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def bulk_update(self, items: List[Dict]) -> bool:
        """Mise à jour en masse d'enregistrements"""
        try:
            for item in items:
                if 'id' not in item:
                    raise ValueError("Each item must have an 'id' field")
                instance = session.query(self.model).get(item['id'])
                if instance:
                    for key, value in item.items():
                        if key != 'id':
                            setattr(instance, key, value)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def find_by_attributes(self, **kwargs):
        """Recherche flexible par attributs avec opérateurs"""
        try:
            query = session.query(self.model)
            filters = []
            
            for key, value in kwargs.items():
                if '__' in key:
                    field, operator = key.split('__')
                    if hasattr(self.model, field):
                        column = getattr(self.model, field)
                        if operator == 'like':
                            filters.append(column.like(f'%{value}%'))
                        elif operator == 'in':
                            filters.append(column.in_(value))
                        elif operator == 'gt':
                            filters.append(column > value)
                        elif operator == 'lt':
                            filters.append(column < value)
                        elif operator == 'gte':
                            filters.append(column >= value)
                        elif operator == 'lte':
                            filters.append(column <= value)
                else:
                    if hasattr(self.model, key):
                        filters.append(getattr(self.model, key) == value)
                        
            return query.filter(and_(*filters)).all()
        finally:
            session.close()

    def get_filtered(
        self, 
        filters: Dict[str, Any] = None, 
        sort_by: List[str] = None
    ) -> List[ModelType]:
        """
        Get filtered and sorted records.
        
        Args:
            filters: Dictionary of filter criteria for each column
            sort_by: List of column names to sort by
            
        Returns:
            List[ModelType]: List of filtered and sorted records
            
        Raises:
            SQLAlchemyError: For any database-related errors
        """
        try:
            query = session.query(self.model)

            if filters:
                for field, value in filters.items():
                    if not hasattr(self.model, field):
                        continue
                        
                    column = getattr(self.model, field)
                    if isinstance(value, str):
                        query = query.filter(column.ilike(f"%{value}%"))
                    else:
                        query = query.filter(column == value)

            if not sort_by:
                sort_by = []
                for column in self.model.__table__.columns:
                    if (hasattr(column, "info") and 
                        isinstance(column.info, dict) and 
                        column.info.get("sortable", False)):
                        sort_by.append(column.key)

            if sort_by:
                query = query.order_by(
                    *[getattr(self.model, col) for col in sort_by]
                )

            return query.all()
            
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Erreur lors du filtrage : {str(e)}")
        finally:
            session.close()
            
    def get_or_create(self, defaults=None, **kwargs):
        """Récupère un enregistrement ou le crée s'il n'existe pas"""
        try:
            instance = self.search(**kwargs)
            if instance:
                return instance[0], False
            
            new_kwargs = dict(kwargs)
            if defaults:
                new_kwargs.update(defaults)
            return self.create(**new_kwargs), True
        finally:
            session.close()

    def aggregate(self, field: str, operation: str = 'count'):
        """Effectue des opérations d'agrégation"""
        try:
            if not hasattr(self.model, field):
                raise ValueError(f"Field {field} does not exist on model")
                
            column = getattr(self.model, field)
            query = session.query(self.model)
            
            if operation == 'count':
                return query.with_entities(func.count(column)).scalar()
            elif operation == 'sum':
                return query.with_entities(func.sum(column)).scalar()
            elif operation == 'avg':
                return query.with_entities(func.avg(column)).scalar()
            elif operation == 'max':
                return query.with_entities(func.max(column)).scalar()
            elif operation == 'min':
                return query.with_entities(func.min(column)).scalar()
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        finally:
            session.close()

    def join_and_query(self, join_model, join_field: str, **filters):
        """Effectue une jointure et applique des filtres"""
        try:
            query = session.query(self.model).join(join_model)
            
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
                elif hasattr(join_model, key):
                    query = query.filter(getattr(join_model, key) == value)
                    
            return query.all()
        finally:
            session.close()

    def _apply_filters(self, query, filters: Dict):
        """Applique des filtres à une requête"""
        for key, value in filters.items():
            if hasattr(self.model, key):
                if isinstance(value, (list, tuple)):
                    query = query.filter(getattr(self.model, key).in_(value))
                else:
                    query = query.filter(getattr(self.model, key) == value)
        return query
    
    def create(self, **kwargs) -> ModelType:
        """
        Create a new record in the database.

        Args:
            **kwargs: Field values for the new record.

        Returns:
            Any: The created record instance.

        Raises:
            RecordAlreadyExistsError: If a record with the same unique fields exists.
            SQLAlchemyError: For any database-related errors.
        """
        try:
            instance = self.model(**kwargs)
            session.add(instance)
            session.commit()
            return instance
        except IntegrityError:
            session.rollback()
            raise RecordAlreadyExistsError(
                "A record with the provided information already exists."
            )
        except SQLAlchemyError as e:
            session.rollback()
            raise
        finally:
            session.close()

    def get_by_id(self, id_: int) -> ModelType:
        """
        Retrieve a record by its ID.

        Args:
            id_ (int): The ID of the record to retrieve.

        Returns:
            Any: The record instance.

        Raises:
            RecordNotFoundError: If record not found.
            SQLAlchemyError: For database-related errors.
        """
        try:
            instance = session.query(self.model).get(id_)
            if not instance:
                raise RecordNotFoundError(f"Record with id {id_} not found.")
            return instance
        except SQLAlchemyError as e:
            raise
        finally:
            session.close()

    def get_all(self, order_by: str = None, direction: str = 'asc', **filters) -> List[ModelType]:
        """
        Fetch all records with optional ordering and filtering.

        Args:
            order_by (str, optional): Column name to order by.
            direction (str, optional): Sort direction ('asc' or 'desc').
            **filters: Additional filters to apply.

        Returns:
            List[Any]: List of model instances.
        """
        try:
            query = session.query(self.model)

            # Apply filters
            if filters:
                query = self._apply_filters(query, filters)

            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                query = query.order_by(desc(order_column) if direction == 'desc' else asc(order_column))
            
            return query.all()
        finally:
            session.close()

    def search(self, limit: int = None, offset: int = None, **filters) -> List[ModelType]:
        """
        Search records with advanced filtering options.

        Args:
            limit (int, optional): Maximum number of records to return.
            offset (int, optional): Number of records to skip.
            **filters: Search criteria (supports operations like __eq, __lt, __gt, __like).

        Returns:
            List[Any]: Matching records.
        """
        try:
            query = session.query(self.model)
            
            for key, value in filters.items():
                if '__' in key:
                    field, operator = key.split('__')
                    if hasattr(self.model, field):
                        column = getattr(self.model, field)
                        if operator == 'like':
                            query = query.filter(column.like(f'%{value}%'))
                        elif operator == 'lt':
                            query = query.filter(column < value)
                        elif operator == 'gt':
                            query = query.filter(column > value)
                        elif operator == 'eq':
                            query = query.filter(column == value)
                else:
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        finally:
            session.close()

    def count(self, **filters) -> int:
        """
        Count records matching the given filters.

        Args:
            **filters: Filtering criteria.

        Returns:
            int: Number of matching records.
        """
        try:
            query = session.query(func.count(self.model.id))
            if filters:
                query = self._apply_filters(query, filters)
            return query.scalar()
        finally:
            session.close()

    def exists(self, **filters) -> bool:
        """
        Check if any record matches the given filters.

        Args:
            **filters: Filtering criteria.

        Returns:
            bool: True if matching record exists, False otherwise.
        """
        return self.count(**filters) > 0

    def update(self, id_: int, **kwargs) -> ModelType:
        """
        Update an existing record with new values.

        Args:
            id_ (int): The ID of the record to update.
            **kwargs: New field values for the record.

        Returns:
            Any: The updated record instance.

        Raises:
            RecordNotFoundError: If no record with the specified ID is found.
            SQLAlchemyError: For any database-related errors.
            ValueError: If invalid fields are provided.
        """
        try:
            # Validate fields before update
            invalid_fields = [
                field for field in kwargs.keys() 
                if not hasattr(self.model, field)
            ]
            if invalid_fields:
                raise ValueError(f"Invalid fields: {', '.join(invalid_fields)}")

            # Use update() for better performance with many records
            rows_updated = (
                session.query(self.model)
                .filter(self.model.id == id_)
                .update(kwargs, synchronize_session=False)
            )
            
            if rows_updated == 0:
                raise RecordNotFoundError(f"Record with id {id_} not found.")
                
            session.commit()
            
            # Fetch and return the updated instance
            return self.get_by_id(id_)
            
        except (RecordNotFoundError, ValueError):
            session.rollback()
            raise
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Database error: {str(e)}")
        finally:
            session.close()
            
    def delete(self, id_: int) -> bool:
        """
        Delete a record by its ID.

        Args:
            id_ (int): The ID of the record to delete.

        Returns:
            bool: True if the record was deleted successfully.

        Raises:
            RecordNotFoundError: If no record with the specified ID is found.
            SQLAlchemyError: For any database-related errors.
        """
        try:
            # Use delete() for better performance
            rows_deleted = (
                session.query(self.model)
                .filter(self.model.id == id_)
                .delete(synchronize_session=False)
            )
            
            if rows_deleted == 0:
                raise RecordNotFoundError(f"Record with id {id_} not found.")
                
            session.commit()
            return True
            
        except RecordNotFoundError:
            session.rollback()
            raise
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Database error: {str(e)}")
        finally:
            session.close()

    def delete_all(self, condition: dict = None) -> int:
        """
        Delete all records matching the optional condition.

        Args:
            condition (dict, optional): Filtering condition for deletion.
                Example: {'status': 'inactive'}

        Returns:
            int: Number of records deleted.

        Raises:
            SQLAlchemyError: For any database-related errors.
        """
        try:
            query = session.query(self.model)
            
            if condition:
                query = self._apply_filters(query, condition)
                
            rows_deleted = query.delete(synchronize_session=False)
            session.commit()
            return rows_deleted
            
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Database error: {str(e)}")
        finally:
            session.close()
        
    def get_related_model(self, foreign_key_column_name):
        """
        Retrieve the related model dynamically based on a ForeignKey column.

        Args:
            foreign_key_column_name (str): The column name holding the ForeignKey.

        Returns:
            The related model class.
        """
        mapper = inspect(self.model)

        for prop in mapper.relationships:
            for col in prop.local_columns:
                if col.name == foreign_key_column_name:
                    return prop.mapper.class_

    def get_related_model_items(self, foreign_key_column_name):

        try:
            related_model = self.get_related_model(foreign_key_column_name)
            if related_model:
                return session.query(related_model).outerjoin(self.model).all()
        except SQLAlchemyError as e:
            raise
        finally:
            session.close()

    def get_related_model_item_by_id(self, foreign_key_column_name, _id):

        try:
            related_model = self.get_related_model(foreign_key_column_name)
            if related_model:
                return (
                    session.query(related_model)
                    .outerjoin(self.model)
                    .filter(related_model.id == _id)
                    .first()
                )
        except SQLAlchemyError as e:
            raise
        finally:
            session.close()

    def _get_order_columns(self):
        order_columns = []
        for column in self.model.__table__.columns:
            if column.info.get("order_column", False):
                order_columns.append(column)

        return order_columns

class RecordNotFoundError(Exception):
    """Exception raised when a record is not found."""

    pass


class RecordAlreadyExistsError(Exception):
    """Exception raised when attempting to create a record that already exists."""

    pass
