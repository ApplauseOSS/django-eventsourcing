import fastavro as avro
import os
import stringcase

from collections import defaultdict
from django.conf import settings
from .settings import CONFIG
from .domain import list_aggregates, list_events


schemas = defaultdict(dict)


def decode_cls_name(cls):
    """
    Convert camel case class name to snake case names used in event documentation.
    """
    return stringcase.snakecase(cls.__name__)


def load_all_event_schemas():
    for aggregate in list_aggregates():
        for event in list_events(aggregate_cls=aggregate):

            aggregate_name = decode_cls_name(aggregate)
            event_name = decode_cls_name(event)

            schemas[aggregate][event] = load_event_schema(aggregate_name, event_name)


def load_event_schema(aggregate, event):
    """
    * TODO: Is setting up `BASE_DIR` a standard practice for our services? Can we assume this exists?
    * TODO: Event version is not taken into an account.
    """
    avro_dir = CONFIG['EVENT_SCHEMA_VALIDATION']['VALIDATOR_SCHEMA_DIR']
    schema_dir = os.path.join(settings.BASE_DIR, avro_dir)

    # We store event schemas in json files for now.
    event_path = os.path.join(schema_dir, aggregate, event + '.json')

    with open(event_path) as fp:
        event_spec = avro.reader(fp)

    return event_spec.schema


def validate_event(event):
    """
    Interesting libraries to check out:
    * https://github.com/datamountaineer/python-serializers
    * https://github.com/linkedin/python-avro-json-serializer
    """
    aggregate = '?'
    schema = schemas[aggregate][event]
    avro.writer.validate(event, schema)
