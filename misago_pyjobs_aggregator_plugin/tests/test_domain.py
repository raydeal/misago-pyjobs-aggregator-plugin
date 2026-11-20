from misago_pyjobs_aggregator_plugin.domain import JobAdvertisement


def test_keywords_match_title_description_and_skills(job):
    assert job.matches(["python"])
    assert job.matches(["django"])
    assert not job.matches(["rust"])


def test_hash_is_stable_for_unordered_lists(job):
    equivalent = JobAdvertisement(**{**job.__dict__, "skills": ("Django", "Python")})
    assert job.content_hash() == equivalent.content_hash()


def test_content_change_changes_hash(job):
    changed = JobAdvertisement(**{**job.__dict__, "description": "A different role"})
    assert job.content_hash() != changed.content_hash()
