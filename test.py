from services.pcs_service import PcsService, RaceCircuit, RaceClass

async def main():
    s = PcsService()
    races = await s.fetch_startlist("2026")
    for race in races:
        print(race)
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

