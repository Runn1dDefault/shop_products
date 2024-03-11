from typing import Type, Iterable, TypeVar

from sqlalchemy import Select
from sqlalchemy.orm.util import AliasedClass

from .base import SelectStrategy, FilteringStrategy, SortStrategy, BaseQueryStrategy


BQS = TypeVar('BQS', bound=BaseQueryStrategy)
FS = TypeVar('FS', bound=FilteringStrategy)
OS = TypeVar("OS", bound=SortStrategy)


class SelectContext:
    def __init__(self, strategy: SelectStrategy):
        self._strategy = strategy

    @property
    def aliased_class(self):
        return self._strategy.aliased_class

    def set_strategy(self, strategy: SelectStrategy):
        self._strategy = strategy

    def select(self):
        return self._strategy.select()


class MultiplyStrategiesContext:
    def __init__(self, strategies: dict[str, Type[BQS]], query, aliased_class: AliasedClass):
        self._strategies = strategies
        self.query = query
        self.aliased_class = aliased_class

    def create_strategy(self, name: str) -> BQS:
        if name not in self._strategies:
            raise ValueError('Invalid strategy name')
        return self._strategies[name](self.query, self.aliased_class)


class FilterContext(MultiplyStrategiesContext):
    def __init__(self, strategies: dict[str, Type[FS]], query, aliased_class: AliasedClass):
        super().__init__(strategies, query, aliased_class)

    def filter(self, data, strategy_name: str) -> Select | None:
        strategy = self.create_strategy(strategy_name)
        if data is None and strategy.default_data is not None:
            data = strategy.default_data

        if data is None:
            return

        try:
            return strategy.filter(data)
        except Exception as e:
            print(strategy_name, ' ', data)
            raise e


class OrderingContext(MultiplyStrategiesContext):
    def __init__(self, strategies: dict[str, Type[OS]], query, aliased_class: AliasedClass):
        super().__init__(strategies, query, aliased_class)

    def order_by(self, strategy_name: str, by_asc: bool = True):
        strategy = self.create_strategy(strategy_name)
        return strategy.sort("desc" if by_asc is False else "asc")


class QueryContext:
    def __init__(
        self,
        select_strategy: SelectStrategy,
        filtering_strategies: dict[str, Type[FS]] = None,
        ordering_strategies: dict[str, Type[OS]] = None
    ):
        select_context = SelectContext(strategy=select_strategy)
        self.query = select_context.select()
        self.aliased_class = select_context.aliased_class
        self.filtering_strategies = filtering_strategies
        self.ordering_strategies = ordering_strategies

    def filtering(self, **filters) -> bool:
        assert self.filtering_strategies, "filtering_strategies required on using this method!"

        filtering_context = FilterContext(
            strategies=self.filtering_strategies,
            query=self.query,
            aliased_class=self.aliased_class
        )

        for filter_name, value in (filters or {}).items():
            filtered_query = filtering_context.filter(value, filter_name)
            if filtered_query is not None:
                filtering_context.query = self.query = filtered_query

    def ordering(self, ordering_fields: Iterable[str] = None) -> None:
        assert self.ordering_strategies, "ordering_strategies required on using this method!"

        ordering_context = OrderingContext(
            strategies=self.ordering_strategies,
            query=self.query,
            aliased_class=self.aliased_class
        )

        for field in ordering_fields or []:
            ordered_query = ordering_context.order_by(field.split("-")[-1], not field.startswith("-"))
            if ordered_query is not None:
                ordering_context.query = self.query = ordered_query
