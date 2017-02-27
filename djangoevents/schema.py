"""
Aggregate event avro schema validation
"""

import avro.schema
import os
import stringcase

from avro.io import Validate as avro_validate
from django.conf import settings
from .settings import CONFIG
from .utils import list_concrete_aggregates, list_aggregate_events
from .exceptions import EventSchemaError


schemas = {}


def load_all_event_schemas():
    """
    Initializes aggregate event schemas lookup cache.
    """
    errors = []
    for aggregate in list_concrete_aggregates():
        for event in list_aggregate_events(aggregate_cls=aggregate):
            try:
                schemas[event] = load_event_schema(aggregate, event)
            except EventSchemaError as e:
                errors.append(str(e))

    # Serve all schema errors at once not iteratively.
    if errors:
        raise EventSchemaError("\n".join(errors))

    return schemas


def load_event_schema(aggregate, event):
    spec_path = event_to_schema_path(aggregate, event)

    try:
        with open(spec_path) as fp:
            return parse_event_schema(fp)
    except FileNotFoundError:
        msg = "No event schema found for: {event} (expecting file at:{path})."
        raise EventSchemaError(msg.format(event=event, path=spec_path))
    except avro.schema.SchemaParseException as e:
        msg = "Can't parse schema for event: {event} from {path}."
        raise EventSchemaError(msg.format(event=event, path=spec_path)) from e


def event_to_schema_path(aggregate_cls, event_cls):
    aggregate_name = decode_cls_name(aggregate_cls)
    event_name = decode_cls_name(event_cls)

    try:
        version = int(getattr(event_cls, 'schema_version', 1))
    except ValueError:
        msg = "`{}.schema_version` must be an integer. Currently it is {}."
        raise EventSchemaError(msg.format(event_cls, event_cls.schema_version))

    filename = "{aggregate_name}_{event_name}_v{version}.json".format(
        aggregate_name=aggregate_name, event_name=event_name, version=version)

    avro_dir = CONFIG['EVENT_SCHEMA_VALIDATION']['SCHEMA_DIR']
    return os.path.join(settings.ROOT_DIR, avro_dir, aggregate_name, filename)


def decode_cls_name(cls):
    """
    Convert camel case class name to snake case names used in event documentation.
    """
    return stringcase.snakecase(cls.__name__)


def parse_event_schema(spec):
    schema = avro.schema.Parse(spec.read())
    return schema


def get_schema_for_event(event_cls):
    if event_cls not in schemas:
        raise EventSchemaError("Cached Schema not found for: {}".format(event_cls))
    return schemas[event_cls]


def validate_event(event, schema=None):
    schema = schema or get_schema_for_event(event.__class__)
    # TODO: Vars shouldn't be used like that. We need a proper to_dict method
    return avro_validate(schema, vars(event))
