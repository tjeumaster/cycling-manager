from services.pcs_service import PcsService, RaceCircuit, RaceClass

async def main():
    s = PcsService()
    races = await s.fetch_races_list(2025, RaceCircuit.PRO_SERIES, RaceClass.PRO_SERIES)
    for race in races:
        print(race)
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

