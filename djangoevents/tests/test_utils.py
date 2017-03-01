from ..utils import list_aggregate_events
from ..utils import list_concrete_aggregates
from .test_domain import SampleEntity


def test_list_aggregates():
    aggregates = list_concrete_aggregates()
    assert aggregates == [SampleEntity]


def test_list_events_sample_event():
    events = list_aggregate_events(SampleEntity)
    assert set(events) == {
        SampleEntity.Created,
        SampleEntity.Updated,
    }
