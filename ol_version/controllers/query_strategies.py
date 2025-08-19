from typing import Any
from abc import ABC, abstractmethod
from sqlalchemy.orm import Query

class JoinStrategy(ABC):
    @abstractmethod
    def apply_join(self, query: Query, model: Any) -> Query:
        pass

class InnerJoinStrategy(JoinStrategy):
    def apply_join(self, query: Query, model: Any) -> Query:
        return query.join(model)

class LeftJoinStrategy(JoinStrategy):
    def apply_join(self, query: Query, model: Any) -> Query:
        return query.outerjoin(model)

class RightJoinStrategy(JoinStrategy):
    def apply_join(self, query: Query, model: Any) -> Query:
        return query.outerjoin(model)

class FullJoinStrategy(JoinStrategy):
    def apply_join(self, query: Query, model: Any) -> Query:
        return query.outerjoin(model)