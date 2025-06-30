from langgraph.graph import END, StateGraph
from .schemas import ProjectState
import os
import logging
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY environment variable is not set")
    raise ValueError("OPENAI_API_KEY environment variable is required")

logger.info("Initializing OpenAI LLM...")
try:
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # Using more cost-effective model
        api_key=api_key,
        temperature=0.7,
        max_tokens=2000
    )
    logger.info("OpenAI LLM initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI LLM: {str(e)}")
    raise


# Agent functions
def planner_agent(state: ProjectState) -> ProjectState:
    try:
        logger.info("Starting Planner Agent...")
        project_info = state["input"]
        
        # Initialize state fields if not present
        if "plan" not in state:
            state["plan"] = ""
        if "schedule" not in state:
            state["schedule"] = ""
        if "review" not in state:
            state["review"] = ""
        if "html_output" not in state:
            state["html_output"] = ""
        
        prompt = f"""
As a Project Planner, your task is to break down the following project description into major phases and detailed tasks. Be very specific and ensure that the output is a clear and concise Markdown list of the phases and their corresponding tasks.

Project Description:
{project_info}

Provide the output as a Markdown list with the following structure:
# Project Plan
## Phase 1: [Phase Name]
- Task 1
- Task 2
## Phase 2: [Phase Name]
- Task 1
- Task 2

Be comprehensive and include all necessary phases for project completion.
"""
        
        response = llm.invoke(prompt).content
        logger.info(f"Planner Agent completed. Plan length: {len(response)} characters")
        logger.debug(f"Plan content preview: {response[:200]}...")
        
        state["plan"] = response
        return state
        
    except Exception as e:
        logger.error(f"Error in planner_agent: {str(e)}")
        state["plan"] = f"Error generating plan: {str(e)}"
        return state

def scheduler_agent(state: ProjectState) -> ProjectState:
    try:
        logger.info("Starting Scheduler Agent...")
        plan = state.get("plan", "")
        project_info = state.get("input", "")
        
        if not plan:
            raise ValueError("No plan available from previous step")
        
        prompt = f"""
You are a Project Scheduler. Based on the provided plan and the project description, assign realistic timelines (in weeks) for each task. Assign appropriate team members *only* from the "Team Members" list provided in the project description. Do not create or use any team member names not listed. Assign a project leader *only* from the provided team members, and indicate dependencies where appropriate.

Project Plan:
{plan}

Project Description:
{project_info}

Output as a Markdown table with columns: Task | Duration (weeks) | Team Member | Dependencies

Format example:
| Task | Duration (weeks) | Team Member | Dependencies |
|------|------------------|-------------|--------------|
| Task 1 | 2 | John Doe | None |
| Task 2 | 3 | Jane Smith | Task 1 |

Ensure all tasks from the plan are included in the schedule.
"""
        
        response = llm.invoke(prompt).content
        logger.info(f"Scheduler Agent completed. Schedule length: {len(response)} characters")
        logger.debug(f"Schedule content preview: {response[:200]}...")
        
        state["schedule"] = response
        return state
        
    except Exception as e:
        logger.error(f"Error in scheduler_agent: {str(e)}")
        state["schedule"] = f"Error generating schedule: {str(e)}"
        return state

def reviewer_agent(state: ProjectState) -> ProjectState:
    try:
        logger.info("Starting Reviewer Agent...")
        schedule = state.get("schedule", "")
        project_info = state.get("input", "")
        
        if not schedule:
            raise ValueError("No schedule available from previous step")
        
        prompt = f"""
You are a Project Reviewer. Review this schedule for completeness, any missing dependencies or tasks, potential bottlenecks, unrealistic timelines, and issues with team member assignments based on the project description.

Here is the schedule to review:
{schedule}

Project Description:
{project_info}

Output suggestions as a Markdown list. If no issues are found that would prevent successful project completion, write: "No significant issues found."

Format:
# Review Feedback
- Issue 1: Description and suggestion
- Issue 2: Description and suggestion
OR
- No significant issues found.
"""
        
        response = llm.invoke(prompt).content
        logger.info(f"Reviewer Agent completed. Review length: {len(response)} characters")
        logger.debug(f"Review content preview: {response[:200]}...")
        
        state["review"] = response
        return state
        
    except Exception as e:
        logger.error(f"Error in reviewer_agent: {str(e)}")
        state["review"] = f"Error generating review: {str(e)}"
        return state

def html_agent(state: ProjectState) -> ProjectState:
    try:
        logger.info("Starting HTML Generator Agent...")
        plan = state.get("plan", "")
        schedule = state.get("schedule", "")
        review = state.get("review", "")
        project_info = state.get("input", "")
        
        if not plan or not schedule or not review:
            raise ValueError("Missing required data from previous steps")
        
        prompt = f"""
You are an HTML Generator. Based on the project plan, schedule, and review, create a single, professional-looking HTML page that summarizes all the information.

IMPORTANT: Convert ALL markdown content to proper HTML format:
- Convert markdown headers (# ## ###) to HTML headers (h1, h2, h3)
- Convert markdown lists (- *) to HTML lists (ul/li)
- Convert markdown tables to proper HTML tables with <table>, <thead>, <tbody>, <tr>, <th>, <td> tags
- Ensure ALL rows from the schedule table are included in the HTML output

Include the following sections in order:
1. **Project Summary:** A brief overview derived from the project description
2. **Project Plan:** Convert the markdown plan to HTML format
3. **Project Schedule:** Convert the COMPLETE markdown table to a properly formatted HTML table with headers and all rows
4. **Review Feedback:** Convert the markdown review to HTML format

Use inline CSS for basic styling (borders for tables, padding, margins). Ensure the output is a complete HTML document with DOCTYPE, html, head, and body tags.

Project Description:
{project_info}

Project Plan (Markdown to convert to HTML):
{plan}

Project Schedule (Markdown table to convert to HTML table - INCLUDE ALL ROWS):
{schedule}

Review Feedback (Markdown to convert to HTML):
{review}

Make sure the HTML table includes:
- Table headers (Task, Duration, Team Member, Dependencies)
- ALL task rows from the markdown table
- Proper table styling with borders and padding
- Responsive layout

Output the complete HTML code starting with <!DOCTYPE html>.
"""
        
        response = llm.invoke(prompt).content
        logger.info(f"HTML Generator Agent completed. HTML length: {len(response)} characters")
        logger.debug(f"HTML content preview: {response[:200]}...")
        
        state["html_output"] = response
        return state
        
    except Exception as e:
        logger.error(f"Error in html_agent: {str(e)}")
        state["html_output"] = f"<html><body><h1>Error generating HTML</h1><p>{str(e)}</p></body></html>"
        return state

# Create workflow
logger.info("Creating workflow...")
try:
    workflow = StateGraph(ProjectState)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("scheduler", scheduler_agent)
    workflow.add_node("reviewer", reviewer_agent)
    workflow.add_node("html_generator", html_agent)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "scheduler")
    workflow.add_edge("scheduler", "reviewer")
    workflow.add_edge("reviewer", "html_generator")
    workflow.add_edge("html_generator", END)

    app_workflow = workflow.compile()
    logger.info("Workflow created and compiled successfully")
except Exception as e:
    logger.error(f"Failed to create workflow: {str(e)}")
    raise