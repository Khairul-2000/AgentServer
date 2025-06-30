from pydantic import BaseModel
from datetime import datetime
from typing import TypedDict

# Response models
class ProjectResponse(BaseModel):
    id: str
    plan: str
    schedule: str
    review: str
    html_output: str
    created_at: datetime

class ProjectListResponse(BaseModel):
    id: str
    project_type: str
    objectives: str
    industry: str
    created_at: datetime

# LangGraph State
class ProjectState(TypedDict):
    input: str
    plan: str
    schedule: str
    review: str
    html_output: str
