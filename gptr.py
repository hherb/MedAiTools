from gpt_researcher import GPTResearcher
import asyncio


async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    return report

if __name__ == "__main__":
    query = "what impact does diastolic hypertension on overall mortality and cognitive decline?"
    report_type = "research_report"

    report = asyncio.run(get_report(query, report_type))
    print(report)