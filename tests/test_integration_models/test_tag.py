from sqlalchemy import delete

from db.models import Tag


def test_tag_creation(session):
    tag1 = Tag(name="Test tag 1")
    tag2 = Tag(name="Test tag 2", group=tag1)
    session.add_all([tag1, tag2])
    session.commit()

    assert tag1.id is not None
    assert tag1.name == "Test tag 1"
    assert tag1.group is None

    assert tag2.id is not None
    assert tag2.name == "Test tag 2"
    assert tag2.group is not None
    assert tag2.group.id == tag1.id


def test_tag_update(session):
    tag1 = Tag(name="Test tag to update 1")
    tag2 = Tag(name="Test tag to update 2")
    session.add_all([tag1, tag2])
    session.commit()

    assert tag2.id is not None
    assert tag1.id is not None
    assert tag2.name == "Test tag to update 2"

    tag2.name = "Test updated tag"
    tag2.group = tag1
    session.commit()

    assert tag2.name == "Test updated tag"
    assert tag2.group.id == tag1.id


def test_tag_delete(session):
    tag = Tag(name="Tag to delete")
    session.add(tag)
    session.commit()

    session.execute(delete(Tag).where(Tag.id == tag.id))
    session.commit()

    query = session.query(Tag).where(Tag.id == tag.id).first()
    assert query is None
