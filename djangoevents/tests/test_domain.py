from ..domain import BaseEntity, DomainEvent
from ..schema import get_event_version
from ..schema import set_event_version
from django.test import override_settings

import os
import pytest
import shutil
import tempfile


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


@override_settings(BASE_DIR='/path/to/proj/src/')
def test_version_1():
    assert get_event_version(SampleEntity.Created) == 1


def test_version_4():
    try:
        # make temporary directory structure
        temp_dir = tempfile.mkdtemp()
        entity_dir = os.path.join(temp_dir, 'sample_entity')
        os.mkdir(entity_dir)

        for version in range(1, 4):
            # make empty schema file
            expected_schema_path = os.path.join(entity_dir, 'v{}_sample_entity_created.json'.format(version))
            with open(expected_schema_path, 'w'):
                pass

            # refresh version
            set_event_version(SampleEntity, SampleEntity.Created, avro_dir=temp_dir)

            assert get_event_version(SampleEntity.Created) == version
    finally:
        # remove temporary directory
        shutil.rmtree(temp_dir)
