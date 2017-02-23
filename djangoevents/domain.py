"""
TODO: Document abstract aggregate usage.
TODO: Disable mutate/create_for_event methods for abstract aggregates?
"""


import inspect
import warnings

from eventsourcing.domain.model.entity import DomainEvent
from eventsourcing.domain.model.entity import EventSourcedEntity


def abstract(cls):
    """
    Marks an aggregate class as abstract.

    Abstract aggregate provides (similarly do Django's abstract Models) means to share implementation
    details.
    """
    cls._abstract = True
    return cls


class BaseAggregate(EventSourcedEntity):
    """
    `EventSourcedEntity` with saner mutator routing & naming:

    >>> class Asset(BaseAggregate):
    >>>    class Created(BaseAggregate.Created):
    >>>        def mutate(event, klass):
    >>>            return klass(...)
    >>>
    >>>    class Updated(DomainEvent):
    >>>        def mutate(event, instance):
    >>>            instance.connect = True
    >>>            return instance
    """
    _abstract = False

    @classmethod
    def is_abstract_class(cls):
        return cls._abstract or cls is BaseAggregate

    @classmethod
    def mutate(cls, aggregate=None, event=None):
        if aggregate:
            aggregate._validate_originator(event)

        if not hasattr(event, 'mutate_event'):
            msg = "{} does not provide a mutate_event() method.".format(event.__class__)
            raise NotImplementedError(msg)

        aggregate = event.mutate_event(event, aggregate or cls)
        aggregate._increment_version()
        return aggregate

    @classmethod
    def create_for_event(cls, event):
        aggregate = cls(
            entity_id=event.entity_id,
            domain_event_id=event.domain_event_id,
            entity_version=event.entity_version,
        )
        return aggregate


class BaseEntity(BaseAggregate):
    """
    `EventSourcedEntity` with saner mutator routing:

    OBSOLETE! Interface kept for backward compatibility.
    """
    @classmethod
    def is_abstract_class(cls):
        return super().is_abstract_class() or cls is BaseEntity

    @classmethod
    def mutate(cls, entity=None, event=None):
        warnings.warn("`BaseEntity` is depreciated. Please switch to: `BaseAggregate`", DeprecationWarning)
        return super().mutate(aggregate=entity, event=event)


def _list_subclasses(cls):
    """
    Recursively lists all subclasses of `cls`.
    """
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in _list_subclasses(s)]


def _list_internal_classes(cls, base_class=None):
    base_class = base_class or object

    return [cls_attribute for cls_attribute in cls.__dict__.values()
            if inspect.isclass(cls_attribute)
            and issubclass(cls_attribute, base_class)]


def list_concrete_aggregates():
    """
    Lists all non abstract aggregates defined within the application.
    """
    aggregates = set(_list_subclasses(BaseAggregate) + _list_subclasses(BaseEntity))
    return [aggregate for aggregate in aggregates if not aggregate.is_abstract_class()]


def list_aggregate_events(aggregate_cls):
    """
    Lists all aggregate_cls events defined within the application.
    Note: Only events with a defined `mutate_event` flow will be returned.
    """
    events = _list_internal_classes(aggregate_cls, DomainEvent)
    return [event_cls for event_cls in events if hasattr(event_cls, 'mutate_event')]
