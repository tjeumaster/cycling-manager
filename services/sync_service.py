from dataclasses import dataclass
from datetime import datetime
import json
from config import settings
from fastapi import Depends
from models.cyclist import Cyclist, CyclistCreate
from models.race import PcsRace, RaceCategoryPointsCreate, RaceCreate, RaceStatus
from models.result import RaceResultCreate
from models.team import TeamCreate
from repositories.base_repository import BaseRepository, get_base_repository
from loguru import logger
from zoneinfo import ZoneInfo
from rapidfuzz import process, fuzz, utils
from repositories.result_repository import ResultRepository, get_result_repository
from services.pcs_service import PcsService, RaceCircuit, RaceClass



@dataclass
class SyncService:
    base_repo: BaseRepository | None = None
    result_repo: ResultRepository | None = None
    
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
    
    async def sync_race_results(self, year: int):
        pcs = PcsService()
        races = await self.base_repo.get_pcs_races(year)
        cyclists = await self.base_repo.get_cyclists()
        
        for race in races:
            result = await pcs.fetch_race_results(race.pcs_path, race.year)
            
            if not result:
                logger.warning(f"No results found for race: {race.name}")
                await self.base_repo.update_race_status(race.id, RaceStatus.CANCELED)
                continue
            
            for r in result:
                search_query = r.cyclist_name
                cyclist = self.find_cyclist_match(search_query, cyclists)
                cyclist_id = cyclist.id if cyclist else None
                race_result = RaceResultCreate(
                    cyclist_id=cyclist_id,
                    race_id=race.id,
                    position=r.position,
                    cyclist_full_name=r.cyclist_name,
                    info=r.info
                )
                    
                await self.result_repo.insert_race_result(race_result)
                
    def find_cyclist_match(self, search_query: str, cyclists: list[Cyclist]) -> Cyclist | None:
        rider_map = {r.full_name: r for r in cyclists}
        
        match = process.extractOne(
            search_query, 
            rider_map.keys(), 
            scorer=fuzz.token_sort_ratio,
            processor=utils.default_process
        )
        
        if match:
            matched_name, score, index = match
            
            if score < 80:  # Threshold for acceptable match
                logger.warning(f"Low confidence match for search query '{search_query}': '{matched_name}' (Score: {score})")
                return None
            
            else:
                logger.info(f"Search: {search_query} | Matched: {matched_name} (Score: {score})")
                found_rider = rider_map[matched_name]
                return found_rider
            
        else:
            logger.warning(f"No match found for search query: {search_query}")
            return None
        
    async def sync_pcs_races(self, year: int):
        pcs = PcsService()
        races: list[PcsRace] = []
        # fetch lists and extend the combined list
        logger.info(f"Fetching PCS races for year {year}...")
        wt = await pcs.fetch_races_list(year, RaceCircuit.WORLD_TOUR, RaceClass.WORLD_TOUR)
        ps = await pcs.fetch_races_list(year, RaceCircuit.PRO_SERIES, RaceClass.PRO_SERIES)
        if wt:
            races.extend(wt)
        if ps:
            races.extend(ps)
        
        logger.info(races)
        
        for race in races:
            r = RaceCreate(
                name = race.name,
                year = race.year,
                start_timestamp = race.start_timestamp,
                category = race.category,
                pcs_path = race.pcs_path
            )
            
            await self.base_repo.insert_race(r)

    async def sync_startlist(self, year: int):  
        races = await self.base_repo.get_pcs_races(year)
        cyclists = await self.base_repo.get_cyclists()
        pcs = PcsService()  
        for race in races:
            await self.base_repo.delete_race_cyclists(race.id)
            startlist = await pcs.fetch_startlist(race.pcs_path, race.year)
            logger.info(startlist)
            for rider_name in startlist:
                cyclist = self.find_cyclist_match(rider_name, cyclists)
                if cyclist:
                    await self.base_repo.insert_race_cyclist(race.id, cyclist.id)
                
def get_sync_service(
    base_repo: BaseRepository = Depends(get_base_repository),
    result_repo: ResultRepository = Depends(get_result_repository)
) -> SyncService:
    return SyncService(base_repo, result_repo)