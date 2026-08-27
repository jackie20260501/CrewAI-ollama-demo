from crewai import Crew, Process

from src.agents import create_researcher, create_reviewer, create_writer
from src.tasks import create_research_task, create_review_task, create_writing_task


def build_content_crew(llm) -> Crew:
    researcher = create_researcher(llm)
    writer = create_writer(llm)
    reviewer = create_reviewer(llm)

    research_task = create_research_task(researcher)
    writing_task = create_writing_task(writer, context=[research_task])
    review_task = create_review_task(reviewer, context=[writing_task])

    return Crew(
        agents=[researcher, writer, reviewer],
        tasks=[research_task, writing_task, review_task],
        process=Process.sequential,
        verbose=True,
        memory=False,
    )

