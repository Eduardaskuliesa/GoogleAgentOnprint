from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from config.config import settings
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from agents.sales_agent import create_sales_agent
from tools.drive_tools import get_folder_files_content, get_folders
from google.genai import types

app = FastAPI(
    title="ADK Agent Server",
    description="AI Agent server using Google ADK",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContentRequest(BaseModel):
    fileId: str = None
    folderId: str = None


@app.get("/health")
async def health_check():
    return {"status": "OK", "timestamp": "2025-07-09T00:00:00Z"}


@app.get("/test-folders")
async def test_folders():
    result = await get_folders()
    return result


@app.post("/test-content")
async def test_content(request: ContentRequest):
    result = await get_folder_files_content(file_id=request.fileId, folder_id=request.folderId)
    return result

sales_agent = create_sales_agent()

session_service = InMemorySessionService()

runner = Runner(
    agent=sales_agent,
    app_name="sales_agent_app",
    session_service=session_service
)


class ChatRequest(BaseModel):
    message: str
    user_id: str


@app.post('/chat')
async def chat_with_agent(request: ChatRequest):
    try:
        session_id = f"session_{request.user_id}"
        
        # Try to get existing session, create if it doesn't exist
        session = await session_service.get_session(
            app_name="sales_agent_app",
            user_id=request.user_id,
            session_id=session_id
        )
        
        if not session:
            # Session doesn't exist, create new one
            session = await session_service.create_session(
                app_name="sales_agent_app",
                user_id=request.user_id,
                session_id=session_id
            )
            print(f"Created new session for user {request.user_id}")
        else:
            print(f"Found existing session for user {request.user_id}")
        
        # Rest stays the same
        content = types.Content(role='user', parts=[types.Part(text=request.message)])
        
        final_response = "No response generated"
        
        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                break
        
        return {"response": final_response}
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(f"🚀 Starting ADK Agent Server on port {settings.PORT}")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=settings.PORT,
        reload=settings.DEBUG
    )
