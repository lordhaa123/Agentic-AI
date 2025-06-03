import os
from crewai import Agent, Task, Crew
from crewai.tools import tool
import psutil
from dotenv import load_dotenv

# Set up the environment variables for OpenAI API
load_dotenv()
os.environ["OPENAI_MODEL_NAME"] = os.getenv("OPENAI_MODEL_NAME")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Define the Tool that retrives cpu usage, memory usage and battry status
@tool("SystemMetrics")
def SystemMetrics():
    """Retrieves system metrics such as CPU usage, memory usage, and battery status."""

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    
    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_info.percent,
        "battery_status": battery.percent if battery else None
    }
    

# Define the Agent
metrics_agent = Agent(
    role="laptop metrics agent",
    goal="given the system metrics, provide a summary of the current state of the laptop",
    backstory="You are a laptop metrics agent that provides system metrics and summaries.",
    verbose=True,
    tools=[SystemMetrics],
)

# Define the Task
task1 = Task(
    description = "Retrieve system metrics and summarize the current state of the laptop.",
    expected_output = "The system metrics are as follows: CPU usage, memory usage, and battery status.",
    agent = metrics_agent,
)

# Define the Crew
crew = Crew(
    agents = [metrics_agent],
    tasks = [task1],
    verbose=True
)

# Run the crew
result = crew.kickoff()

print("#################")
print(result)
