from typing import Optional
import httpx
from config.config import settings

async def get_headers():
   return {
       "x-api-key": settings.EXPRESS_API_KEY,
       "Content-Type": "application/json"
   }

async def get_folders():
   """Fetches folders from the Express server"""
   try:
       async with httpx.AsyncClient(timeout=30) as client:
           response = await client.get(f"{settings.EXPRESS_BASE_URL}/api/folders", headers=await get_headers())
           
           print(f"API Key: {settings.EXPRESS_API_KEY}")
           if response.status_code == 200:
               drive_structure = response.json()
               return {"success": True, "driveStructure": drive_structure}
           else:
               return {"success": False, "error": f"HTTP {response.status_code}"}
               
   except Exception as e:
       return {"success": False, "error": str(e)}

async def get_folder_files_content(file_id: Optional[str] = None, folder_id: Optional[str] = None):
    """Gets file or folder content from Express server"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            body = {}
            if file_id:
                body["fileId"] = file_id
            if folder_id:
                body["folderId"] = folder_id
            
            if not body:
                return {"success": False, "error": "Missing fileId or folderId"}
                
            response = await client.post(
                f"{settings.EXPRESS_BASE_URL}/api/content", 
                headers=await get_headers(),
                json=body
            )
                        
            if response.status_code == 200:
                content_data = response.json()
                return {"success": True, "data": content_data}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                    
    except Exception as e:
        return {"success": False, "error": str(e)}