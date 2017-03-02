import avro.schema
from djangoevents.exceptions import EventSchemaError

import djangoevents.schema as schema
import json
import pytest
from djangoevents.domain import BaseAggregate
from djangoevents.domain import DomainEvent
from io import StringIO
from django.test import override_settings
from unittest import mock
from .test_domain import SampleEntity


class Project(BaseAggregate):
    class Created(BaseAggregate.Created):
        def mutate_event(self, event, klass):
            return klass(
                entity_id=event.entity_id,
                entity_version=event.entity_version,
                domain_event_id=event.domain_event_id,
                name=event.name,
            )

    class Closed(DomainEvent):
        # no mutate_event
        pass

    def __init__(self, schema_version, project_id, name, **kwargs):
        super().__init__(**kwargs)
        self.schema_version = schema_version
        self.project_id = project_id
        self.name = name


PROJECT_CREATED_SCHEMA = json.dumps({
    "name": "project_created",
    "type": "record",
    "doc": "Event posted when a project has been created",
    "namespace": "services.project_svc",
    "fields": [
        {
            "name": "entity_id",
            "type": "string",
            "doc": "ID of a the asset."
        },
        {
            "name": "entity_version",
            "type": "string",
            "doc": "Aggregate revision"
        },
        {
            "name": "domain_event_id",
            "type": "string",
            "doc": "ID of the last modifying event"
        },
        {
            "name": "name",
            "type": "string",
            "doc": "name of the project"
        }
    ]
})


@override_settings(BASE_DIR='/path/to/proj/src/')
def test_load_all_event_schemas():
    with mock.patch('djangoevents.schema.list_concrete_aggregates') as list_aggs, \
            mock.patch('djangoevents.schema.load_event_schema') as load_schema:
        list_aggs.return_value = [Project]
        schema.load_all_event_schemas()

    load_schema.assert_called_once_with(Project, Project.Created)


@override_settings(BASE_DIR='/path/to/proj/src/')
def test_load_all_event_schemas_missing_specs():
    with mock.patch('djangoevents.schema.list_concrete_aggregates') as list_aggs:
        list_aggs.return_value = [Project]

        with pytest.raises(EventSchemaError) as e:
            schema.load_all_event_schemas()

    path = "/path/to/proj/avro/project/v1_project_created.json"
    msg = "No event schema found for: {cls} (expecting file at:{path}).".format(cls=Project.Created, path=path)
    assert msg in str(e.value)


@override_settings(BASE_DIR='/path/to/proj/src/')
def test_valid_event_to_schema_path():
    avro_path = schema.event_to_schema_path(aggregate_cls=SampleEntity, event_cls=SampleEntity.Created)
    assert avro_path == "/path/to/proj/avro/sample_entity/v1_sample_entity_created.json"


def test_parse_invalid_event_schema():
    fp = StringIO("Invalid schema")

    with pytest.raises(avro.schema.SchemaParseException):
        schema.parse_event_schema(fp)


def test_parse_valid_event_schema():
    evt_schema = schema.parse_event_schema(PROJECT_CREATED_SCHEMA)
    assert evt_schema is not None


def test_validate_valid_event():
    class TestEvent:
        def __init__(self):
            self.entity_id = "1"
            self.entity_version = "XYZ"
            self.domain_event_id = "2"
            self.name = "Awesome Project"

    event = TestEvent()
    evt_schema = avro.schema.Parse(PROJECT_CREATED_SCHEMA)
    ret = schema.validate_event(event, evt_schema)
    assert ret is True


def test_validate_invalid_event():
    class TestEvent:
        def __init__(self):
            self.test = 'test'

    event = TestEvent()
    evt_schema = avro.schema.Parse(PROJECT_CREATED_SCHEMA)
    ret = schema.validate_event(event, evt_schema)
    assert ret is False


def test_decode_cls_name():
    class LongName:
        pass

    class Shortname:
        pass

    assert schema.decode_cls_name(LongName) == 'long_name'
    assert schema.decode_cls_name(Shortname) == 'shortname'
