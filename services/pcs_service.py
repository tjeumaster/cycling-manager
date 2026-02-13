from fastapi import Depends
from models.result import PcsResult
from repositories.base_repository import BaseRepository, get_base_repository
from typing import List, Dict
import httpx
from bs4 import BeautifulSoup
from config import settings

class PcsService:
    def __init__(self, repository: BaseRepository = Depends(get_base_repository)):
        self.repository = repository

    async def fetch_race_results(self, pcs_path: str, year: int) -> list[PcsResult]:
        base_url = "https://www.procyclingstats.com/race"
        url = f"{base_url}/{pcs_path}/{year}/result"
        print(url)
        result: list[PcsResult] = []
        
        # PCS often blocks scripts without a User-Agent, so we mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                # Await the response
                response = await client.get(url)
                response.raise_for_status() # Raises an error for 4xx/5xx codes
                
                # Parsing is CPU-bound (sync), but fast enough here to keep in the loop
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the results table (usually the first table on the page)
                table = soup.find('table')

                if not table:
                    print("No table found.")
                    return

                # Extract rows
                rows = table.find_all('tr')
                
                # Print Header
                print(f"{'Pos':<5} {'Rider':<30} {'Team':<25}")
                print("-" * 60)

                for row in rows:
                    cols = row.find_all('td')
                    
                    # Ensure it's a data row (rank is usually the first column)
                    if len(cols) > 2:
                        position = cols[0].text.strip()
                        
                        # Rider Name (usually col 5 in the HTML structure of PCS)
                        # We look for the anchor tag <a> inside to get the clean name
                        rider_cell = cols[5] # Adjust index if PCS changes layout
                        rider_name = rider_cell.find('a').text.strip() if rider_cell.find('a') else rider_cell.text.strip()
                        
                        # Team Name (usually col 6)
                        team_cell = cols[6]
                        team_name = team_cell.find('a').text.strip() if team_cell.find('a') else team_cell.text.strip()
                        
                        pos = int(position) if position.isdigit() else None
                        info = str(position) if not position.isdigit() else None
                        result.append(PcsResult(position=pos, cyclist_name=rider_name, team_name=team_name, info=info))
                        
                return result

            except httpx.HTTPStatusError as e:
                print(f"HTTP Error: {e.response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")

def get_pcs_service(repository: BaseRepository = Depends(get_base_repository)) -> PcsService:
    return PcsService(repository)