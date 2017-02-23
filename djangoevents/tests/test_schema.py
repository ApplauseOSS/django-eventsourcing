import avro.schema
import json
import pytest
from io import StringIO
from ..schema import decode_cls_name, parse_event_schema, validate_event, event_to_schema_path
from django.test import override_settings


SAMPLE_EVENT_SCHEMA = json.dumps({
    "name": "project_created",
    "type": "record",
    "doc": "Event posted when a project has been created",
    "namespace": "services.project_svc",
    "fields": [
        {
            "name": "schema_version",
            "type": "int",
            "doc": "Event schema version"
        },
        {
            "name": "project_id",
            "type": "string",
            "doc": "ID of a project"
        },
        {
            "name": "name",
            "type": "string",
            "doc": "Name of a project"
        },
    ]
})


def test_decode_cls_name():
    class LongName:
        pass

    class Shortname:
        pass

    assert decode_cls_name(LongName) == 'long_name'
    assert decode_cls_name(Shortname) == 'shortname'


def test_parse_invalid_event_schema():
    fp = StringIO("Invalid schema")

    with pytest.raises(avro.schema.SchemaParseException):
        parse_event_schema(fp)


def test_parse_valid_event_schema():
    fp = StringIO(SAMPLE_EVENT_SCHEMA)
    schema = parse_event_schema(fp)
    assert schema is not None


def test_validate_invalid_event():
    schema = avro.schema.Parse(SAMPLE_EVENT_SCHEMA)
    event = {'test': 'test'}

    ret = validate_event(event, schema)
    assert ret is False


def test_validate_valid_event():
    schema = avro.schema.Parse(SAMPLE_EVENT_SCHEMA)
    event = {
        'schema_version': 1,
        'project_id': "XYZ",
        'name': 'Awesome Project'
    }

    ret = validate_event(event, schema)
    assert ret is True


@override_settings(ROOT_DIR='/path/to/proj/')
def test_valid_event_to_schema_path():
    from .test_domain import SampleEntity

    avro_path = event_to_schema_path(aggregate_cls=SampleEntity, event_cls=SampleEntity.Created)
    assert avro_path == "/path/to/proj/avro/sample_entity/sample_entity_created_1.json"
