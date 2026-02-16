import pytest
from app.models import User, OrganizationProfile
from sqlalchemy.exc import IntegrityError

def test_create_organization_profile(db_session):
    # Create organization user
    user = User(
        email="org@test.com",
        hashed_password="fakehashed",
        role="organization"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create organization profile
    profile = OrganizationProfile(
        user_id=user.id,
        organization_name="Tech Corp",
        industry="Software",
        website="https://techcorp.com",
        description="We build innovative software."
    )

    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)

    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.user.email == "org@test.com"

def test_organization_user_cannot_have_multiple_profiles(db_session):
    user = User(
        email="dup_org@test.com",
        hashed_password="fakehashed",
        role="organization"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile1 = OrganizationProfile(
        user_id=user.id,
        organization_name="First Org"
    )

    db_session.add(profile1)
    db_session.commit()

    profile2 = OrganizationProfile(
        user_id=user.id,
        organization_name="Second Org"
    )

    db_session.add(profile2)

    with pytest.raises(IntegrityError):
        db_session.commit()
