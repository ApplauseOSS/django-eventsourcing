import avro.schema
import json
import pytest
from io import StringIO
from ..schema import decode_cls_name, load_event_schema, validate_event


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


def test_load_invalid_event_schema():
    fp = StringIO("Invalid schema")

    with pytest.raises(avro.schema.SchemaParseException):
        load_event_schema(fp)


def test_load_valid_event_schema():
    fp = StringIO(SAMPLE_EVENT_SCHEMA)
    schema = load_event_schema(fp)
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
