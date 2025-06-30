from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from src.crew.tools.websearch import tool as web_search_tool
from src.crew.tools.location import tool as location_tool
import os
load_dotenv()

print(os.getenv("GEMINI_API_KEY"))
# Initialize Gemini model
llm = LLM(model="gemini/gemini-2.0-flash")
@CrewBase
class schoolcrew():
    """schoolcrew crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def school_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['school_finder'],
            llm=llm,
            tools=[web_search_tool, location_tool]
        )
    @agent
    def school_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['school_analyzer'],
            llm=llm,
            tools=[web_search_tool, location_tool]
        )
    @task
    def find_schools_task(self) -> Task:
        return Task(
            config=self.tasks_config["find_schools_task"]
        )
    @task
    def analyze_schools_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_schools_task"]
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the excelcrew crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose= True,
        )