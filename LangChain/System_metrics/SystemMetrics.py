import os
import psutil
from dotenv import load_dotenv

from langchain.tools import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4")

# function for System Metrics
def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    
    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_info.percent,
        "battery_status": battery.percent if battery else None
    }


# Wrap the fucntion in langchain tool
system_metrics_tool = Tool(
    name="SystemMetrics",
    func=lambda _: str(get_system_metrics()),
    description="Returns system metrics including CPU, memory, and battery usage."
)


# Define the LLM
llm = ChatOpenAI(model_name=model_name, openai_api_key=openai_api_key)


# Create a prompt template for summarizing system metrics
prompt_template = PromptTemplate(
    input_variables=["metrics"],
    template="""
Given the following system metrics:

{metrics}

Summarize the current state of the laptop in a human-readable format.
"""
)

# LLMChain
chain = LLMChain(llm=llm, prompt=prompt_template)

# Running the tool and use the chain to summarize
metrics = system_metrics_tool.run("")
summary = chain.run(metrics=metrics)

print("#################")
print(summary)