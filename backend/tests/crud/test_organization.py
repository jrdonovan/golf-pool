from sqlmodel import Session

from app import crud
from app.models.organizations import (
    Organization,
    OrganizationCreate,
    OrganizationDelete,
    OrganizationUpdate,
)
from tests.utils.utils import random_lower_string


def test_create_organization(db: Session) -> None:
    name = random_lower_string()
    external_id = 10
    organization_in = OrganizationCreate(name=name, external_id=external_id)
    organization = crud.create_organization(session=db, organization_in=organization_in)
    assert organization.name == name
    assert organization.external_id == external_id


def test_create_organization_duplicate_name(db: Session) -> None:
    name = random_lower_string()
    organization_in = OrganizationCreate(name=name)
    crud.create_organization(session=db, organization_in=organization_in)
    try:
        crud.create_organization(session=db, organization_in=organization_in)
        raise AssertionError("Expected ValueError for duplicate organization name")
    except ValueError as e:
        assert str(e) == "Organization with this name already exists"


def test_create_organization_duplicate_external_id(db: Session) -> None:
    name = random_lower_string()
    external_id = 10
    organization_in = OrganizationCreate(name=name, external_id=external_id)
    crud.create_organization(session=db, organization_in=organization_in)
    try:
        crud.create_organization(session=db, organization_in=organization_in)
        raise AssertionError(
            "Expected ValueError for duplicate organization external_id"
        )
    except ValueError as e:
        assert str(e) == "Organization with this external_id already exists"


def test_get_organization(db: Session) -> None:
    name = random_lower_string()
    organization_in = OrganizationCreate(name=name)
    created_organization = crud.create_organization(
        session=db, organization_in=organization_in
    )
    retrieved_organization = db.get(Organization, created_organization.id)

    assert retrieved_organization
    assert retrieved_organization.id == created_organization.id
    assert retrieved_organization.name == created_organization.name


def test_get_organization_by_name(db: Session) -> None:
    name = random_lower_string()
    organization_in = OrganizationCreate(name=name)
    created_organization = crud.create_organization(
        session=db, organization_in=organization_in
    )
    retrieved_organization = crud.get_organization_by_name(session=db, name=name)

    assert retrieved_organization
    assert retrieved_organization.id == created_organization.id
    assert retrieved_organization.name == created_organization.name


def test_get_organization_by_external_id(db: Session) -> None:
    name = random_lower_string()
    external_id = 10
    organization_in = OrganizationCreate(name=name, external_id=external_id)
    created_organization = crud.create_organization(
        session=db, organization_in=organization_in
    )
    retrieved_organization = crud.get_organization_by_external_id(
        session=db, external_id=external_id
    )

    assert retrieved_organization
    assert retrieved_organization.id == created_organization.id
    assert retrieved_organization.external_id == created_organization.external_id


def test_list_organizations(db: Session) -> None:
    name_1 = random_lower_string()
    name_2 = random_lower_string()
    organization_in_1 = OrganizationCreate(name=name_1)
    organization_in_2 = OrganizationCreate(name=name_2)
    crud.create_organization(session=db, organization_in=organization_in_1)
    crud.create_organization(session=db, organization_in=organization_in_2)

    organizations = crud.list_organizations(session=db)

    assert len(organizations) >= 2
    assert any(org.name == name_1 for org in organizations)
    assert any(org.name == name_2 for org in organizations)


def test_update_organization(db: Session) -> None:
    name = random_lower_string()
    organization_in = OrganizationCreate(name=name)
    created_organization = crud.create_organization(
        session=db, organization_in=organization_in
    )

    new_name = random_lower_string()
    updated_organization = crud.update_organization(
        session=db,
        organization_id=created_organization.id,
        update_vals=OrganizationUpdate(name=new_name),
    )

    assert updated_organization
    assert updated_organization.id == created_organization.id
    assert updated_organization.name == new_name


def test_delete_organization(db: Session) -> None:
    name = random_lower_string()
    organization_in = OrganizationCreate(name=name)
    created_organization = crud.create_organization(
        session=db, organization_in=organization_in
    )

    crud.delete_organization(
        session=db, organization_in=OrganizationDelete(id=created_organization.id)
    )

    deleted_organization = db.get(Organization, created_organization.id)
    assert deleted_organization is None
