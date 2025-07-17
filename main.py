from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from config.config import settings
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from agents.sales_agent import create_sales_agent
from google.genai import types
from google import genai

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

class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.get("/health")
async def health_check():
    return {"status": "OK", "timestamp": "2025-07-09T00:00:00Z"}


sales_agent = create_sales_agent()
artifact_service = InMemoryArtifactService()
session_service = InMemorySessionService()

runner = Runner(
    agent=sales_agent,
    app_name="sales_agent_app",
    session_service=session_service,
    artifact_service=artifact_service
)



    
@app.post('/chat')
async def chat_with_agent(request: ChatRequest):
    try:
        session_id = f"session_{request.user_id}"
        
        session = await session_service.get_session(
            app_name="sales_agent_app",
            user_id=request.user_id,
            session_id=session_id
        )
        
        if not session:
            session = await session_service.create_session(
                app_name="sales_agent_app",
                user_id=request.user_id,
                session_id=session_id
            )
            print(f"✅ Created new session for user {request.user_id}")
        else:
            print(f"🔄 Found existing session for user {request.user_id}")
                    
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
                    print(event.content)
                    print(event)
                break
        
        return {"response": final_response}
        
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print(f"🚀 Starting ADK Agent Server with Artifacts on port {settings.PORT}")
    print(f"💾 Artifact caching: ENABLED (In-Memory)")
    print(f"🔧 Debug artifacts at: GET /debug/artifacts/{{user_id}}")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=settings.PORT,
        reload=settings.DEBUG
    )