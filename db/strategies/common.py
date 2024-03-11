from typing import Literal, Any

from .base import SortStrategy, FilteringStrategy


class NameSearchFilteringStrategy(FilteringStrategy):
    def filter(self, term: str):
        assert isinstance(term, str)
        return self.query.where(self._alias.name.ilike(f"%{term}%"))


class IDFilteringStrategy(FilteringStrategy):
    def filter(self, _id: Any):
        return self.query.where(self._alias.id == _id)


class IDOrderingStrategy(SortStrategy):
    def sort(self, sort_type: Literal["asc", "desc"]):
        assert isinstance(sort_type, str) and sort_type in ("asc", "desc")
        return self.query.order_by(self._get_sort_method(self._alias.id, sort_type)())


class CreatedOrderingStrategy(SortStrategy):
    def sort(self, sort_type: Literal["asc", "desc"]):
        assert isinstance(sort_type, str) and sort_type in ("asc", "desc")
        return self.query.order_by(self._get_sort_method(self._alias.created_at, sort_type)())
