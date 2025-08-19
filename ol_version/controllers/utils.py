from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class QueryOperator(str, Enum):
    """
    Enumeration of query operators for filtering and searching.
    """
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    LIKE = "like"
    ILIKE = "ilike"  # Case-insensitive LIKE
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    IS_NULL = "is_null"
    NOT_NULL = "not_null"
    
    def __str__(self) -> str:
        return self.value

class SortDirection(str, Enum):
    """
    Enumeration for sort directions.
    """
    ASCENDING = "asc"
    DESCENDING = "desc"
    
    def __str__(self) -> str:
        return self.value
    
from enum import Enum

class AggregateFunction(str, Enum):
    """
    Enumeration of SQL aggregate functions.
    """
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "avg"
    MAXIMUM = "max"
    MINIMUM = "min"
    
    def __str__(self) -> str:
        return self.value
    
class JoinMode(str, Enum):
    """
    Enumeration for SQL join types.
    """
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    FULL = "full"
    
@dataclass
class SearchOptions:
    """
    Configuration options for search operations.
    """
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: Optional[int] = None
    offset: Optional[int] = None
    order_by: Optional[str] = None
    direction: SortDirection = SortDirection.ASCENDING
    include_related: List[str] = field(default_factory=list)
    
@dataclass
class PaginationOptions:
    """
    Configuration options for pagination.
    """
    page: int = 1
    per_page: int = 10
    order_by: Optional[str] = None
    direction: SortDirection = SortDirection.ASCENDING
    filters: Dict[str, Any] = field(default_factory=dict)