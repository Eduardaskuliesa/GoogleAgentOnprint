import time
from typing import Optional
import httpx
import json
from google.adk.tools import tool
from typing import List, Dict, Any
from config.config import settings
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

# ========== Utility functions (move these to tools/common.py if you want) ==========

def parse_spreadsheet_content(content_json) -> str:
    """
    Converts Google Sheets JSON to clean, token-efficient text format.
    Removes all the JSON bloat and cell metadata.
    """
    if isinstance(content_json, str):
        content_json = json.loads(content_json)
    
    sheets = content_json.get("sheets", [])
    if not sheets:
        return "No data found"
    
    result = []
    title = content_json.get("title", "Spreadsheet")
    result.append(f"# {title}\n")
    
    for sheet in sheets:
        cells = sheet.get("cells", [])
        if not cells:
            continue
        
        # Convert to simple table format
        for row_data in cells:
            row_values = []
            for cell in row_data.get("data", []):
                value = cell.get("value", "")
                # Convert to string and clean up
                if value is not None and str(value).strip():
                    row_values.append(str(value).strip())
                else:
                    row_values.append("")
            
            # Skip completely empty rows
            if any(val for val in row_values):
                # Join with | for clean table format
                result.append(" | ".join(row_values))
    
    return "\n".join(result)

def flatten_drive_folder_content(response_data: dict) -> List[Dict[str, Any]]:
    """
    Clean, token-efficient version that removes JSON bloat.
    """
    files_out = []
    files = response_data.get('files', [])
    
    for file in files:
        file_id = file.get('fileId') or file.get('id')
        name = file.get('name')
        content = file.get('content', "")
        
        # Try to parse as spreadsheet, else treat as text
        parsed = None
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "sheets" in data:
                parsed = parse_spreadsheet_content(data)
            else:
                parsed = content
        except Exception:
            parsed = content
        
        files_out.append({
            "fileId": file_id,
            "name": name,
            "content": parsed
        })
    
    return files_out

def format_drive_structure_for_llm(drive_structure: dict) -> str:
    lines = []
    def process_folder(folder, indent=0):
        prefix = "#" * (indent + 1)
        lines.append(f"{prefix} 📂 {folder['name']} [ID: {folder['id']}]")
        for file in folder.get('files', []):
            if file.get('type') == 'file':
                lines.append('  ' * (indent + 1) + f"- {file['name']} [ID: {file['id']}]")
            elif file.get('type') == 'folder':
                process_folder(file, indent=indent + 1)
    for folder in drive_structure.get('folders', []):
        process_folder(folder)
    for rule in drive_structure.get('salesAgentRules', []):
        lines.append(f"\n# 📝 Sales Agent Rule: {rule['name']} [ID: {rule['fileId']}]\n")
        content = rule.get('content', '').strip()
        if content:
            lines.append(content)
    return "\n".join(lines)

# ========== Main async API functions ==========

async def get_headers():
    return {
        "x-api-key": settings.EXPRESS_API_KEY,
        "Content-Type": "application/json"
    }


async def get_folders_and_sales_rules():
    """Fetches folders and Sales agent rules from Express server"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{settings.EXPRESS_BASE_URL}/api/sales-agent/rules-and-folders",
                headers=await get_headers()
            )
            if response.status_code == 200:
                drive_structure = response.json()
                llm_ready_summary = format_drive_structure_for_llm(drive_structure)
                return {"success": True, "driveStructure": llm_ready_summary}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_folder_files_content(file_id: Optional[str] = None, folder_id: Optional[str] = None):
    """Gets file or folder content from Express server. Always first use folderId to get all info in one go.
    Returns LLM-cleaned content (spreadsheets as list of dicts, docx/text as plain string).
    """
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
                files_llm_ready = flatten_drive_folder_content(content_data)
                return {"success": True, "files": files_llm_ready}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_design_recommendations():
    """Fetches self design recommendations from Express server"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{settings.EXPRESS_BASE_URL}/api/sales-agent/design-recommendations", headers=await get_headers())
            if response.status_code == 200:
                design_recommendations = response.json()
                return {"success": True, "design_recommendations": design_recommendations}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
