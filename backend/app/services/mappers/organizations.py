from typing import TYPE_CHECKING

from app.models.organizations import OrganizationCreate, OrganizationUpdate

if TYPE_CHECKING:
    from app.services.live_golf_data import OrganizationData


class OrganizationMapperFactory:
    @staticmethod
    def create_model(incoming_data: "OrganizationData") -> OrganizationCreate:
        return OrganizationCreate(
            live_golf_data_id=incoming_data.orgId, name=incoming_data.orgName
        )

    @staticmethod
    def update_model(incoming_data: "OrganizationData") -> OrganizationUpdate:
        return OrganizationUpdate(name=incoming_data.orgName)
