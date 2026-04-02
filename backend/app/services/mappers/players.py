from app.models.players import PlayerCreate, PlayerUpdate
from app.services.live_golf_data import TournamentPlayerData


class PlayerMapperFactory:
    @staticmethod
    def create_from_tournament_player(
        incoming_data: TournamentPlayerData,
    ) -> PlayerCreate:
        return PlayerCreate(
            live_golf_data_id=incoming_data.playerId,
            first_name=incoming_data.firstName,
            last_name=incoming_data.lastName,
            is_amateur=incoming_data.isAmateur,
        )

    @staticmethod
    def update_from_tournament_player(
        incoming_data: TournamentPlayerData,
    ) -> PlayerUpdate:
        return PlayerUpdate(
            first_name=incoming_data.firstName,
            last_name=incoming_data.lastName,
            is_amateur=incoming_data.isAmateur,
        )
