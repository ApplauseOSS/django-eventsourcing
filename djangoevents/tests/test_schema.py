from ..schema import decode_cls_name


def test_decode_cls_name():
    class LongName:
        pass

    class Shortname:
        pass

    assert decode_cls_name(LongName) == 'long_name'
    assert decode_cls_name(Shortname) == 'shortname'


def test_event_to_schema_path():
    from ..domain import SampleEvent
