import inspect
import warnings

from eventsourcing.domain.model.entity import DomainEvent
from eventsourcing.domain.model.entity import EventSourcedEntity


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
    def mutate(cls, entity=None, event=None):
        warnings.warn("`BaseEntity` is depreciated. Please switch to: `BaseAggregate`", DeprecationWarning)
        return super().mutate(aggregate=entity, event=event)


def list_subclasses(cls):
    """
    Recursively lists all subclasses of `cls`.
    TODO: what about `mid level` classes -> do we want them? This can be a bit misleading..
    """
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in list_subclasses(s)]


def list_internal_classes(cls, base_class=None):
    """
    List all internal classes of `cls` which are instances of `base_class`.
    """
    base_class = base_class or object

    classes = []
    for elem in inspect.getmembers(cls):
        if inspect.isclass(elem):
            classes.append(elem)

    return classes


def list_aggregates():
    """
    Lists all aggregates defined within the application.
    """
    # `BaseEntity` needs to be removed from the list manually (also inherits
    # from BaseAggregate).
    aggregates = list_subclasses(BaseAggregate) + list_subclasses(BaseEntity)
    aggregates = set(aggregates)
    aggregates.discard(BaseEntity)
    return list(aggregates)


def list_events(aggregate_cls):
    """
    Lists all aggregate_cls events defined within the application.
    TODO: Does not work, is this approach reliable?
    """
    return list_internal_classes(aggregate_cls, DomainEvent)
