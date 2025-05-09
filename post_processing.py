import re
import json
from typing import Dict, Any

def extract_draft_reply(llm_output: str) -> str:
    # This regex captures everything after 'Draft Reply:' up to 'Action Item:' or end of string
    match = re.search(r"Draft Reply:\s*(.*?)\s*Action Item:", llm_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: if 'Action Item:' is not present, get everything after 'Draft Reply:'
    match = re.search(r"Draft Reply:\s*(.*)", llm_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return llm_output.strip()  # fallback: return the whole thing

def extract_action_item(llm_output: str):
    # This regex captures the JSON block after 'Action Item:'
    match = re.search(r"Action Item:\s*```json\s*(\{.*?\})\s*```", llm_output, re.DOTALL)
    if not match:
        # Fallback: try to capture after 'Action Item:' up to the end
        match = re.search(r"Action Item:\s*(\{.*\})", llm_output, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)  # Return as a Python dict
        except Exception as e:
            print(f"Failed to parse action item JSON: {e}")
            return json_str  # Return as string if JSON parsing fails
    return None  # No action item found

def process_action_item(action_item: Dict[str, Any]):
    # TODO: This is where we would process the action item
    # like sending a api call to task management system for a super, etc.
    print(f"Processing action item: {action_item}")