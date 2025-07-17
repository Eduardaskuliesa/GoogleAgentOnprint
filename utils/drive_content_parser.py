import json

def parse_spreadsheet_content(content_json):
    """
    Cleans Google Sheets-like JSON into a list of row dicts.
    Returns: [ {Header1: value1, Header2: value2, ...}, ... ]
    """
    if isinstance(content_json, str):
        content_json = json.loads(content_json)
    sheets = content_json.get("sheets", [])
    if not sheets:
        return []
    result = []
    for sheet in sheets:
        cells = sheet.get("cells", [])
        if not cells:
            continue
        headers = [cell.get("value", "") for cell in cells[0]["data"]]
        for row in cells[1:]:
            row_values = [cell.get("value", "") for cell in row.get("data", [])]
            row_dict = dict(zip(headers, row_values))
            result.append(row_dict)
    return result
