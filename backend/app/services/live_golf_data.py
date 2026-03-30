from datetime import date, datetime, time, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator
from pydantic_extra_types.timezone_name import TimeZoneName

from app.core.config import settings
from app.services.api_base import APIBase


# Query Parameter Models
class _QueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def to_params(self) -> dict[str, str | int | float | bool | None]:
        return self.model_dump(by_alias=True, exclude_none=True)


class ScheduleParams(_QueryParams):
    year: int
    orgId: str | None


class PlayersParams(_QueryParams):
    lastName: str | None = None
    firstName: str | None = None
    playerId: str | None = None


class TournamentParams(_QueryParams):
    orgId: str
    tournId: str
    year: int


class LeaderboardParams(_QueryParams):
    orgId: str
    tournId: str
    year: int
    roundId: PositiveInt | None = Field(default=None, ge=1, le=4)


class ScorecardsParams(_QueryParams):
    orgId: str
    tournId: str
    year: int
    playerId: str
    roundId: PositiveInt | None = Field(default=None, ge=1, le=4)


################################### Response Models ###################################
class _LiveGolfDataBaseResponseModel(BaseModel):
    timestamp: datetime | None

    @field_validator("timestamp", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return None
        # If the API sends a naive datetime, explicitly set it to UTC
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class OrganizationData(_LiveGolfDataBaseResponseModel):
    orgName: str
    orgId: str


class TournamentDate(BaseModel):
    weekNumber: int
    start: date
    end: date


class TournamentFormat(StrEnum):
    stroke = "stroke"
    team = "team"
    team_match = "team match"


class ScheduleTournamentData(BaseModel):
    tournId: str
    name: str
    date: TournamentDate
    format: TournamentFormat
    purse: PositiveInt | None
    winnersShare: PositiveInt | None
    fedexCupPoints: PositiveInt | None


class ScheduleData(_LiveGolfDataBaseResponseModel):
    orgId: str
    year: int
    schedule: list[ScheduleTournamentData]


class PlayerData(BaseModel):
    playerId: str
    firstName: str
    lastName: str


class LocationData(BaseModel):
    city: str
    state: str | None
    country: str


class HoleData(BaseModel):
    holeId: PositiveInt = Field(ge=1, le=18)
    par: PositiveInt


class CourseData(_LiveGolfDataBaseResponseModel):
    courseId: str
    courseName: str
    host: bool | None
    location: LocationData
    parFrontNine: PositiveInt
    parBackNine: PositiveInt
    parTotal: PositiveInt
    holes: list[HoleData]


class TeeTimeData(BaseModel):
    roundId: PositiveInt = Field(ge=1, le=4)
    teeTime: time | None
    teeTimeTimestamp: datetime | None
    startingHole: PositiveInt | None = Field(ge=1, le=18)

    @field_validator("teeTime", mode="before")
    @classmethod
    def parse_12hr_time(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            # %I is 12-hour clock, %M is minutes, %p is AM/PM
            # We parse to a datetime first, then extract just the .time()
            return datetime.strptime(v.lower(), "%I:%M%p").time()
        return v


class TournamentPlayerData(PlayerData):
    courseId: str | None
    status: (
        str | None
    )  # TODO: validate expected values (complete, wd, cut, dq). Don't know what others exist
    isAmateur: bool | None
    teeTimes: list[TeeTimeData] | None


class TournamentStatus(StrEnum):
    not_started = "Not Started"
    in_progress = "In Progress"
    complete = "Complete"
    official = "Official"


class TournamentData(_LiveGolfDataBaseResponseModel):
    orgId: str
    year: int
    tournId: str
    name: str
    purse: PositiveInt | None
    fedexCupPoints: PositiveInt | None
    date: TournamentDate
    format: TournamentFormat | None
    status: TournamentStatus | None
    currentRound: int  # TODO: validate that value = -1 if status is not started
    timeZone: TimeZoneName | None
    courses: list[CourseData] | None
    players: list[TournamentPlayerData] | None


class LeaderboardData(BaseModel):
    orgId: str
    year: int
    tournId: str
    status: str
    roundId: PositiveInt | None = Field(default=None, ge=1, le=4)


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

    def get_schedule(self, year: int, org_id: int | None = None) -> ScheduleData:
        """
        Fetches the schedule data
        """
        params = ScheduleParams(year=year, orgId=str(org_id)).to_params()
        payload = self.send_request("schedule", params=params)
        if not isinstance(payload, list):
            raise RuntimeError("Expected list payload for schedule")
        return ScheduleData.model_validate(payload)

    def get_leaderboard(
        self, org_id: str, tourn_id: str, year: int, round_id: int | None = None
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

    def get_player_by_id(self, player_id: str) -> PlayerData | None:
        """
        Fetches player data by ID
        """
        players = self.get_players(player_id=player_id)
        if not players:  # TODO: handle not found exception
            return None
        return players[0]

    def get_tournament(
        self,
        org_id: str,
        tourn_id: str,
        year: int,
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
            year=year,
            playerId=player_id,
            roundId=round_id,
        ).to_params()
        payload = self.send_request("scorecard", params=params)
        if not isinstance(payload, dict):
            raise RuntimeError("Expected object payload for scorecard")
        return ScorecardData.model_validate(payload)
