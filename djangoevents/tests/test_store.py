from djangoevents import store_event
from unittest import mock


def test_store_event_validation_enabled():
    evt = {}

    with mock.patch('djangoevents.is_validation_enabled') as validation_enabled, \
         mock.patch('djangoevents.validate_event') as validate_event, \
         mock.patch('djangoevents.es_publish') as publish:

        validation_enabled.return_value = True
        validate_event.return_value = True
        store_event(evt)

    assert validation_enabled.call_count == 1
    validate_event.assert_called_once_with(evt)
    publish.assert_called_once_with(evt)


def test_store_event_validation_disabled():
    evt = {}

    with mock.patch('djangoevents.is_validation_enabled') as validation_enabled, \
         mock.patch('djangoevents.validate_event') as validate_event, \
         mock.patch('djangoevents.es_publish') as publish:

        validation_enabled.return_value = False
        store_event(evt)

    assert validation_enabled.call_count == 1
    assert validate_event.call_count == 0
    publish.assert_called_once_with(evt)


def test_store_event_validation_disabled_force():
    evt = {}

    with mock.patch('djangoevents.is_validation_enabled') as validation_enabled, \
         mock.patch('djangoevents.validate_event') as validate_event, \
         mock.patch('djangoevents.es_publish') as publish:

        validation_enabled.return_value = False
        store_event(evt, force_validate=True)

    assert validation_enabled.call_count == 1
    validate_event.assert_called_once_with(evt)
    publish.assert_called_once_with(evt)
