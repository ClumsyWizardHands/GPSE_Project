"""
Example of using the FileWriterTool from crewai_tools
This tool allows dynamic filename specification when used by agents
"""

from crewai_tools import FileWriterTool

# Example 1: Basic usage with default settings
file_writer = FileWriterTool()

# The tool can be used with dynamic filenames like this:
result = file_writer._run(
    filename="analysis_report_2025_06_02.txt",
    content="This is the strategic analysis content...",
    directory="./outputs",  # Optional: specify a directory
    overwrite=True  # Optional: whether to overwrite if file exists
)

# Example 2: Initialize with specific directory
file_writer_reports = FileWriterTool(directory="./reports")

# Example 3: When used in a CrewAI agent/task:
# The agent can dynamically specify the filename based on the task
"""
from crewai import Agent, Task, Crew

# Create an agent with the file writer tool
analyst_agent = Agent(
    role='Strategic Analyst',
    goal='Analyze and document strategic insights',
    tools=[file_writer],
    verbose=True
)

# Create a task that uses dynamic filename
analysis_task = Task(
    description='''
    Analyze the current geopolitical situation and save your analysis.
    Use the filename format: analysis_YYYY_MM_DD.txt
    ''',
    agent=analyst_agent,
    expected_output='A saved analysis file with today\'s date'
)

# The agent will use the FileWriterTool with a dynamically generated filename
"""

print("FileWriterTool is available from crewai_tools package")
print(f"Tool description: {file_writer.description}")
print("\nThe tool accepts these parameters:")
print("- filename: The name of the file to write")
print("- content: The content to write to the file")
print("- directory: (optional) The directory to save the file in")
print("- overwrite: (optional) Whether to overwrite existing files")
