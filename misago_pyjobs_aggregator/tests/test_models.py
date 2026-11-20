import pytest

from misago_pyjobs_aggregator.models import AggregatorConfig, CollectionState


@pytest.mark.django_db
def test_aggregator_config_is_a_singleton():
    first = AggregatorConfig.get_solo()
    second = AggregatorConfig.get_solo()

    assert first.pk == second.pk == 1
    assert first.keywords == ["Python"]
    assert first.enabled_sources == ["solid_jobs"]


@pytest.mark.django_db
def test_aggregator_config_save_forces_singleton_primary_key():
    config = AggregatorConfig(target_category_id=10, bot_user_id=20)
    config.save()

    assert config.pk == 1
    assert AggregatorConfig.objects.count() == 1


@pytest.mark.django_db
def test_collection_state_get_solo_is_stable():
    assert CollectionState.get_solo().pk == CollectionState.get_solo().pk
