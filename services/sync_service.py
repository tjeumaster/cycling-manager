from dataclasses import dataclass
from datetime import datetime
import json
from config import settings
from fastapi import Depends
from models.cyclist import CyclistCreate
from models.race import RaceCategoryPointsCreate, RaceCreate
from models.team import TeamCreate
from repositories.base_repository import BaseRepository, get_base_repository
from loguru import logger
from zoneinfo import ZoneInfo

@dataclass
class SyncService:
    base_repo: BaseRepository | None = None
    
    async def sync(self):
        await self.sync_teams()
        await self.sync_cyclists()
        await self.sync_races()
        await self.sync_race_category_points()
    
    async def sync_cyclists(self):
        try:
            path = "data/cyclists.json"
            with open(path, "r") as f:
                data = json.load(f)
                
        except Exception as e:
            message = f"Error loading cyclists data from {path}: {e}"
            logger.error(message)
            raise Exception(message)
            
        cyclists = data.get("cyclists", [])
        
        if not cyclists:
            logger.warning("No cyclists data found in the JSON file.")
            return
        
        try:
            teams = await self.base_repo.get_teams()
            team_dict = {team.code: team.id for team in teams}
            
            for cyclist in cyclists:
                first_name = cyclist.get("firstName")
                last_name = cyclist.get("lastName")
                birth_date = cyclist.get("dateOfBirth")
                nationality = cyclist.get("nationality")
                price = cyclist.get("price")  # Placeholder for price
                team = cyclist.get("team")
                team_code = team.get("shortName")
                team_id = team_dict.get(team_code)
                image_url = team.get("jerseyUrl")
                
                c = CyclistCreate(
                    first_name=first_name,
                    last_name=last_name,
                    price=price,
                    birth_date=datetime.strptime(birth_date, "%Y-%m-%d").date(),
                    nationality=nationality,
                    team_id=team_id,
                    image_url=image_url
                )
                
                await self.base_repo.insert_cyclist(c)
                
        except Exception as e:
            message = f"Error syncing cyclists data: {e}"
            logger.error(message)
            raise Exception(message)
            
    async def sync_teams(self):
        try:
            with open("data/cyclists.json", "r") as f:
                data = json.load(f)
        except Exception as e:
            message = f"Error loading teams data from JSON file: {e}"
            logger.error(message)
            raise Exception(message)
            
        teams = data.get("teams", [])
        
        if not teams:
            logger.warning("No teams data found in the JSON file.")
            return
        
        try:
            for team in teams:
                name = team.get("name")
                code = team.get("shortName")
                image_url = team.get("jerseyUrl")
                
                t = TeamCreate(
                    code=code,
                    name=name,
                    image_url=image_url
                )
                
                await self.base_repo.insert_team(t)
        
        except Exception as e:
            message = f"Error syncing teams data: {e}"
            logger.error(message)
            raise Exception(message)
        
    async def sync_races(self):
        try:
            path = "data/races.json"
            with open(path, "r") as f:
                data = json.load(f)
                
        except Exception as e:
            message = f"Error loading races data from {path}: {e}"
            logger.error(message)
            raise Exception(message)

        try:
            for race in data:
                name = race.get("name")
                start = race.get("start_timestamp")
                category = race.get("category")
                year = settings.YEAR
                start_timestamp = datetime.fromisoformat(start).replace(tzinfo=ZoneInfo("Europe/Brussels"))
                r = RaceCreate(
                    name=name,
                    start_timestamp=start_timestamp,
                    category=category,
                    year=year
                )
                await self.base_repo.insert_race(r)
        except Exception as e:
            message = f"Error syncing races data: {e}"
            logger.error(message)
            raise Exception(message)
        
    async def sync_race_category_points(self):
        try:
            path = "data/points.json"
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            message = f"Error loading race category points data from {path}: {e}"
            logger.error(message)
            raise Exception(message)
        
        try:
            for item in data:
                category = item.get("category")
                position = item.get("position")
                points = item.get("points")
                
                rcp = RaceCategoryPointsCreate(
                    category=category,
                    position=position,
                    points=points
                )
                
                await self.base_repo.insert_race_category_points(rcp)
        except Exception as e:
            message = f"Error syncing race category points data: {e}"
            logger.error(message)
            raise Exception(message)
        
def get_sync_service(base_repo: BaseRepository = Depends(get_base_repository)) -> SyncService:
    return SyncService(base_repo)