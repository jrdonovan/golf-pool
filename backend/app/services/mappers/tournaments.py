import uuid

from app.models.tournaments import TournamentCreate, TournamentUpdate
from app.models.tournaments import TournamentFormat as BackendTournamentFormat
from app.models.tournaments import TournamentStatus as BackendTournamentStatus
from app.services.live_golf_data import ScheduleTournamentData, TournamentData


class TournamentMapperFactory:
    @staticmethod
    def create_from_schedule(
        incoming_data: ScheduleTournamentData, *, organization_id: uuid.UUID, year: int
    ) -> TournamentCreate:
        return TournamentCreate(
            name=incoming_data.name,
            organization_id=organization_id,
            year=year,
            purse=incoming_data.purse,
            format=BackendTournamentFormat(incoming_data.format.value),
            start_date=incoming_data.date.start,
            end_date=incoming_data.date.end,
            live_golf_data_id=incoming_data.tournId,
        )

    @staticmethod
    def update_from_schedule(incoming_data: ScheduleTournamentData) -> TournamentUpdate:
        return TournamentUpdate(
            name=incoming_data.name,
            purse=incoming_data.purse,
            format=incoming_data.format.value,
            start_date=incoming_data.date.start,
            end_date=incoming_data.date.end,
        )

    @staticmethod
    def create_from_tournament_data(
        incoming_data: TournamentData, *, organization_id: uuid.UUID
    ) -> TournamentCreate:
        status = (
            BackendTournamentStatus(incoming_data.status.value)
            if incoming_data.status
            else None
        )
        tournament_format = (
            BackendTournamentFormat(incoming_data.format.value)
            if incoming_data.format
            else None
        )

        return TournamentCreate(
            name=incoming_data.name,
            organization_id=organization_id,
            year=incoming_data.year,
            purse=incoming_data.purse,
            format=tournament_format,
            status=status,
            start_date=incoming_data.date.start,
            end_date=incoming_data.date.end,
            timezone=incoming_data.timeZone,
            live_golf_data_id=incoming_data.tournId,
        )

    @staticmethod
    def update_from_tournament_data(incoming_data: TournamentData) -> TournamentUpdate:
        status = (
            BackendTournamentStatus(incoming_data.status.value)
            if incoming_data.status
            else None
        )
        return TournamentUpdate(
            name=incoming_data.name,
            purse=incoming_data.purse,
            format=incoming_data.format.value if incoming_data.format else None,
            status=status,
            start_date=incoming_data.date.start,
            end_date=incoming_data.date.end,
            timezone=incoming_data.timeZone,
        )
