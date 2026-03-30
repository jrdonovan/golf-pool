from pydantic import BaseModel, ConfigDict, PositiveInt

from app.core.config import settings
from app.services.api_base import APIBase


class _QueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def to_params(self) -> dict[str, str | int | float | bool | None]:
        return self.model_dump(by_alias=True, exclude_none=True)


class OrganizationData(BaseModel):
    orgName: str
    orgId: str


class LeaderboardParams(_QueryParams):
    orgId: str
    tournId: str
    year: str
    roundId: PositiveInt | None = None


class LeaderboardData(BaseModel):
    orgId: str
    year: str
    tournId: str
    status: str
    roundId: PositiveInt | None = None


class PlayersParams(_QueryParams):
    lastName: str | None = None
    firstName: str | None = None
    playerId: str | None = None


class PlayerData(BaseModel):
    playerId: str
    firstName: str
    lastName: str


class TournamentsParams(_QueryParams):
    org_id: PositiveInt
    tourn_id: str
    year: str


class TournamentData(BaseModel):
    model_config = ConfigDict(extra="allow")


class ScorecardsParams(_QueryParams):
    player_id: str
    org_id: PositiveInt
    tourn_id: str
    year: str
    round_id: str | None = None


class ScorecardData(BaseModel):
    model_config = ConfigDict(extra="allow")


class LiveGolfData(APIBase):
    def __init__(self):
        base_url = settings.LIVE_GOLF_DATA_BASE_URL
        headers = {
            "X-RapidAPI-Key": settings.LIVE_GOLF_DATA_API_KEY,
            "X-RapidAPI-Host": settings.LIVE_GOLF_DATA_API_HOST,
        }
        super().__init__(base_url, headers, timeout=30)

    def get_organizations(self) -> list[OrganizationData]:
        """
        Fetches the organizations data
        """
        payload = self.send_request("organizations")
        if not isinstance(payload, list):
            raise RuntimeError("Expected list payload for organizations")
        return [OrganizationData.model_validate(item) for item in payload]

    def get_leaderboard(
        self, org_id: str, tourn_id: str, year: str, round_id: int | None = None
    ) -> tuple[list[LeaderboardData], bool]:
        """
        Fetches the leaderboard data
        """
        params = LeaderboardParams(
            orgId=org_id,
            tournId=tourn_id,
            year=year,
            roundId=round_id,
        ).to_params()
        payload = self.send_request("leaderboard", params=params)
        if not isinstance(payload, list):
            raise RuntimeError("Expected list payload for leaderboard")
        data = [LeaderboardData.model_validate(item) for item in payload]
        return data, False

    def get_players(
        self,
        last_name: str | None = None,
        first_name: str | None = None,
        player_id: str | None = None,
    ) -> list[PlayerData]:
        """
        Fetches player data
        """
        params = PlayersParams(
            lastName=last_name, firstName=first_name, playerId=player_id
        ).to_params()
        payload = self.send_request("players", params=params)
        if not isinstance(payload, list):
            raise RuntimeError("Expected list payload for players")
        return [PlayerData.model_validate(item) for item in payload]

    def get_tournaments(
        self,
        org_id: int,
        tourn_id: str,
        year: str,
    ) -> list[TournamentData]:
        """
        Fetches tournament data
        """
        params = TournamentsParams(
            org_id=org_id, tourn_id=tourn_id, year=year
        ).to_params()
        payload = self.send_request("tournaments", params=params)
        if not isinstance(payload, list):
            raise RuntimeError("Expected list payload for tournaments")
        return [TournamentData.model_validate(item) for item in payload]

    def get_scorecards(
        self,
        player_id: str,
        org_id: int,
        tourn_id: str,
        year: str,
        round_id: str | None = None,
    ) -> ScorecardData:
        """
        Fetches scorecard data
        """
        params = ScorecardsParams(
            player_id=player_id,
            org_id=org_id,
            tourn_id=tourn_id,
            year=year,
            round_id=round_id,
        ).to_params()
        payload = self.send_request("scorecard", params=params)
        if not isinstance(payload, dict):
            raise RuntimeError("Expected object payload for scorecard")
        return ScorecardData.model_validate(payload)
