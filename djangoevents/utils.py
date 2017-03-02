import inspect
from .domain import BaseEntity
from .domain import BaseAggregate
from .domain import DomainEvent


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


def event_to_json(event):
    """
    Converts an event class to its dictionary representation.
    Underlying eventsourcing library does not provide a proper event->dict conversion function.

    Note: Similarly to event journal persistence flow, this method supports native JSON types only.
    """
    return vars(event)


def _list_subclasses(cls):
    """
    Recursively lists all subclasses of `cls`.
    """
    subclasses = cls.__subclasses__()

    for subclass in cls.__subclasses__():
        subclasses += _list_subclasses(subclass)

    return subclasses


def _list_internal_classes(cls, base_class=None):
    base_class = base_class or object

    return [cls_attribute for cls_attribute in cls.__dict__.values()
            if inspect.isclass(cls_attribute)
            and issubclass(cls_attribute, base_class)]

