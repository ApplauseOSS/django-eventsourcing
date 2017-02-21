from ..domain import BaseEntity, DomainEvent, list_events, list_aggregates

import pytest


class SampleEntity(BaseEntity):
    class Created(BaseEntity.Created):
        def mutate_event(self, event, klass):
            return klass(entity_id=event.entity_id,
                         entity_version=event.entity_version,
                         domain_event_id=event.domain_event_id)

    class Updated(DomainEvent):
        def mutate_event(self, event, entity):
            entity.is_dirty = True
            return entity

    class Closed(DomainEvent):
        # no mutate_event
        pass

    def __init__(self, is_dirty=False, **kwargs):
        super().__init__(**kwargs)
        self.is_dirty = is_dirty


def test_base_entity_calls_mutator():
    create_event = SampleEntity.Created(entity_id=1)
    entity = SampleEntity.mutate(event=create_event)

    close_event = SampleEntity.Updated(entity_id=entity.id, entity_version=entity.version)
    entity = SampleEntity.mutate(event=close_event, entity=entity)
    assert entity.is_dirty is True

def test_base_entity_requires_mutator():
    create_event = SampleEntity.Created(entity_id=1)
    entity = SampleEntity.mutate(event=create_event)

    close_event = SampleEntity.Closed(entity_id=entity.id, entity_version=entity.version)

    with pytest.raises(NotImplementedError):
        SampleEntity.mutate(event=close_event, entity=entity)


def test_create_for_event():
    event = SampleEntity.Created(
        entity_id='ENTITY_ID',
        domain_event_id='DOMAIN_EVENT_ID',
        entity_version=0,
    )
    obj = SampleEntity.create_for_event(event)

    assert obj.id == 'ENTITY_ID'
    assert obj.version == 0


def test_list_aggregates():
    aggregates = list_aggregates()
    assert len(aggregates) == 1
    assert aggregates[0] is SampleEntity


def test_list_events_sample_event():
    events = list_events(SampleEntity)
    assert len(events) == 2
    assert set(events) == {
        SampleEntity.Created,
        SampleEntity.Updated,
    }
