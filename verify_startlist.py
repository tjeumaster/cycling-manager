import asyncio
from services.pcs_service import PcsService


async def main():
    service = PcsService()
    url = "https://www.procyclingstats.com/race/clasica-jaen-paraiso-interior/2026/startlist"
    print(f"Testing fetch_startlist with {url}")
    results = await service.fetch_startlist(url)
    print(f"Found {len(results)} riders.")
    for name in results[:10]:
        print(f" - {name}")


if __name__ == "__main__":
    asyncio.run(main())
