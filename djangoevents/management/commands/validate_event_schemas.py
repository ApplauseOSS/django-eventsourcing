"""
Parses event schemas and reports on their validity.
"""
from assets.build_metadata import get_build_metadata
from django.core.management.base import BaseCommand
from pprint import pprint
from djangoevents.exceptions import EventSchemaError
from djangoevents.schema import load_all_event_schemas, schemas
from djangoevents.settings import schema_validation_enabled


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("=> Searching for schema files...")
        try:
            if schema_validation_enabled():
                print("--> Schema validation enabled. Checking state..")
            load_all_event_schemas()
        except EventSchemaError as e:
            print("Missing or invalid event schemas:")
            print(e)
        else:
            print("--> Detected events:")
            for item in schemas.keys():
                print("--> {}".format(item))
            print("--> All schemas valid!")
        print("=> Done.")
