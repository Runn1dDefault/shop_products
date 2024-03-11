from abc import ABC, abstractmethod
from typing import Literal, Any

from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.selectable import Select


class AliasedStrategy:
    _alias: AliasedClass = None

    def __init__(self, alias: AliasedClass):
        self._alias = alias


class SelectStrategy(AliasedStrategy, ABC):
    _alias: AliasedClass = None

    @property
    def aliased_class(self):
        return self._alias

    @abstractmethod
    def select(self) -> Select[_alias]:
        pass


class BaseQueryStrategy(AliasedStrategy):
    default_data: Any = None
    bool_check: bool = False

    def __init__(self, query, alias: AliasedClass = None):
        super().__init__(alias)
        self.query = query


class FilteringStrategy(BaseQueryStrategy, ABC):
    _alias: AliasedClass = None

    @abstractmethod
    def filter(self, data) -> Select[_alias] | None:
        pass


class SortStrategy(BaseQueryStrategy, ABC):
    _alias: AliasedClass = None

    @staticmethod
    def _get_sort_method(field, sort_type: Literal["asc", "desc"]):
        return getattr(field, sort_type)

    @abstractmethod
    def sort(self, sort_type: Literal["asc", "desc"]) -> Select[_alias] | None:
        pass
