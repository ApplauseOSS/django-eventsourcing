def validate_event(event, schema):
    """
    * https://github.com/datamountaineer/python-serializers
    * https://github.com/linkedin/python-avro-json-serializer
    """
    # TODO: Implement
    from datamountaineer.schemaregistry.client import SchemaRegistryClient
    from datamountaineer.schemaregistry.serializers import MessageSerializer, Util

    client = SchemaRegistryClient(url='http://registry.host')