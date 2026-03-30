from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from app.core.config import settings
from app.services.api_base import APIBase


# Query Parameter Models
class _QueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def to_params(self) -> dict[str, str | int | float | bool | None]:
        return self.model_dump(by_alias=True, exclude_none=True)


class ScheduleParams(_QueryParams):
    year: str
    orgId: str | None


class PlayersParams(_QueryParams):
    lastName: str | None = None
    firstName: str | None = None
    playerId: str | None = None


class TournamentParams(_QueryParams):
    orgId: str
    tournId: str
    year: str


class LeaderboardParams(_QueryParams):
    orgId: str
    tournId: str
    year: str
    roundId: PositiveInt | None = Field(default=None, ge=1, le=4)


class ScorecardsParams(_QueryParams):
    orgId: str
    tournId: str
    year: str
    playerId: str
    roundId: PositiveInt | None = Field(default=None, ge=1, le=4)


# Response Models
class OrganizationData(BaseModel):
    orgName: str
    orgId: str


class LeaderboardData(BaseModel):
    orgId: str
    year: str
    tournId: str
    status: str
    roundId: PositiveInt | None = Field(default=None, ge=1, le=4)


class BasicPlayerData(BaseModel):
    playerId: str
    firstName: str
    lastName: str


class TournamentDate(BaseModel):
    weekNumber: str  # TODO: validate this is a number in string format
    start: str  # TODO: validate this is a UTC date in string format
    end: str  # TODO: validate this is a UTC date in string format


class ScheduleTournamentData(BaseModel):
    tournId: str
    name: str
    date: TournamentDate
    format: str
    purse: int
    winnersShare: int
    fedexCupPoints: int


class TeeTimeData(BaseModel):
    roundId: PositiveInt = Field(ge=1, le=4)
    teeTime: str  # TODO: validate format like "1:40pm"
    teeTimeTimestamp: str  # TODO: validate this is a UTC date in string format
    startingHole: PositiveInt = Field(ge=1, le=18)


class TournamentPlayerData(BasicPlayerData):
    courseId: str
    status: str
    isAmateur: bool
    teeTimes: list[TeeTimeData]


class LocationData(BaseModel):
    city: str
    state: str | None
    country: str


class HoleData(BaseModel):
    holeId: PositiveInt = Field(ge=1, le=18)
    par: str  # TODO: validate this is a number in string format


class CourseData(BaseModel):
    courseId: str
    courseName: str
    host: str  # TODO: validate yes/no
    location: LocationData
    parFrontNine: int  # TODO: validate this is a number in string format
    parBackNine: int  # TODO: validate this is a number in string format
    parTotal: (
        int  # TODO: validate this is a number in string format & sum of front/back nine
    )
    holes: list[HoleData]


class TournamentData(BaseModel):
    orgId: str
    year: str
    tournId: str
    name: str
    purse: int
    fedexCupPoints: int
    date: TournamentDate
    format: str
    status: str
    currentRound: PositiveInt
    timeZone: str
    courses: list[CourseData]
    players: list[TournamentPlayerData]
    timestamp: str  # TODO: validate this is a UTC date in string format


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

    def get_schedule(
        self, year: int, org_id: int | None = None
    ) -> list[ScheduleTournamentData]:
        """
        Fetches the schedule data
        """
        params = ScheduleParams(year=str(year), orgId=str(org_id)).to_params()
        payload = self.send_request("schedule", params=params)
        if not isinstance(payload, list):
            raise RuntimeError("Expected list payload for schedule")
        return [ScheduleTournamentData.model_validate(item) for item in payload]

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
    ) -> list[BasicPlayerData]:
        """
        Fetches player data
        """
        params = PlayersParams(
            lastName=last_name, firstName=first_name, playerId=player_id
        ).to_params()
        payload = self.send_request("players", params=params)
        if not isinstance(payload, list):
            raise RuntimeError("Expected list payload for players")
        return [BasicPlayerData.model_validate(item) for item in payload]

    def get_tournament(
        self,
        org_id: str,
        tourn_id: str,
        year: str,
    ) -> list[TournamentData]:
        """
        Fetches tournament data
        """
        params = TournamentParams(orgId=org_id, tournId=tourn_id, year=year).to_params()
        payload = self.send_request("tournaments", params=params)
        if not isinstance(payload, list):
            raise RuntimeError("Expected list payload for tournaments")
        return [TournamentData.model_validate(item) for item in payload]

    def get_scorecards(
        self,
        org_id: str,
        tournament_id: str,
        year: int,
        player_id: str,
        round_id: int | None = None,
    ) -> ScorecardData:
        """
        Fetches scorecard data
        """
        params = ScorecardsParams(
            orgId=org_id,
            tournId=tournament_id,
            year=str(year),
            playerId=player_id,
            roundId=round_id,
        ).to_params()
        payload = self.send_request("scorecard", params=params)
        if not isinstance(payload, dict):
            raise RuntimeError("Expected object payload for scorecard")
        return ScorecardData.model_validate(payload)
