from google.adk.agents import Agent
from tools.drive_tools import get_folders, get_folder_files_content


def create_sales_agent():
    return Agent(
        name="sales_agent",
        model="gemini-2.5-flash",
        description="A sales agent that helps customers by accessing their folders and files",
        instruction=(
            "You are a helpful sales agent. You can have normal conversations with customers "
            "and also access their Google Drive folders and files when needed. "
            "Remember information from previous messages in the conversation. "
            "Use get_folders to see available folders, and get_folder_files_content "
            "to read specific files or folder contents when asked about files."
        ),
        tools=[get_folders, get_folder_files_content]
    )
