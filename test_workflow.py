#!/usr/bin/env python3
"""
Test script to verify the AI workflow execution
"""
import sys
import os
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.graph import app_workflow
from app.services import ProjectService, ProjectInput

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_workflow():
    """Test the complete workflow with sample data"""
    
    # Sample project input
    sample_project = ProjectInput(
        project_type="Web Application",
        objectives="Create a modern e-commerce website with user authentication, product catalog, shopping cart, and payment processing.",
        industry="E-commerce",
        team_members=["John Doe (Full-stack Developer)", "Jane Smith (UI/UX Designer)", "Bob Johnson (Project Manager)"],
        requirements=[
            "Responsive design for mobile and desktop",
            "User registration and authentication", 
            "Product search and filtering",
            "Shopping cart functionality",
            "Payment gateway integration",
            "Admin panel for inventory management"
        ]
    )
    
    try:
        # Create project
        logger.info("Creating sample project...")
        project = ProjectService.create_project(sample_project)
        logger.info(f"Project created with ID: {project.id}")
        
        # Format input for workflow
        formatted_input = f"""
**Project Type:** {sample_project.project_type}

**Project Objectives:** {sample_project.objectives}

**Industry:** {sample_project.industry}

**Team Members:**
{chr(10).join([f"- {member}" for member in sample_project.team_members])}

**Project Requirements:**
{chr(10).join([f"- {req}" for req in sample_project.requirements])}
"""
        
        # Initialize workflow state
        initial_state = {
            "input": formatted_input,
            "plan": "",
            "schedule": "",
            "review": "",
            "html_output": ""
        }
        
        logger.info("Starting AI workflow...")
        logger.info(f"Input length: {len(formatted_input)} characters")
        
        # Run workflow
        output = app_workflow.invoke(initial_state)
        
        logger.info("Workflow completed!")
        logger.info(f"Output keys: {list(output.keys())}")
        
        # Check results
        plan = output.get("plan", "")
        schedule = output.get("schedule", "")
        review = output.get("review", "")
        html_output = output.get("html_output", "")
        
        logger.info(f"Plan length: {len(plan)} characters")
        logger.info(f"Schedule length: {len(schedule)} characters") 
        logger.info(f"Review length: {len(review)} characters")
        logger.info(f"HTML length: {len(html_output)} characters")
        
        # Validate outputs
        if not plan:
            logger.error("❌ No plan generated!")
            return False
        if not schedule:
            logger.error("❌ No schedule generated!")
            return False
        if not review:
            logger.error("❌ No review generated!")
            return False
        if not html_output:
            logger.error("❌ No HTML output generated!")
            return False
            
        logger.info("✅ All workflow outputs generated successfully!")
        
        # Update project with results
        updated_project = ProjectService.update_project_results(
            project.id, plan, schedule, review, html_output
        )
        
        if updated_project:
            logger.info(f"✅ Project {project.id} updated successfully!")
            
            # Print sample outputs
            print("\n" + "="*50)
            print("SAMPLE OUTPUTS:")
            print("="*50)
            print(f"\nPLAN (first 300 chars):\n{plan[:300]}...")
            print(f"\nSCHEDULE (first 300 chars):\n{schedule[:300]}...")
            print(f"\nREVIEW (first 300 chars):\n{review[:300]}...")
            print(f"\nHTML (first 300 chars):\n{html_output[:300]}...")
            
            return True
        else:
            logger.error("❌ Failed to update project with results!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Testing AI Workflow...")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set!")
        sys.exit(1)
    
    success = asyncio.run(test_workflow())
    
    if success:
        print("✅ Workflow test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Workflow test failed!")
        sys.exit(1)
