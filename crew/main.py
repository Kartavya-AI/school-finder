from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
from src.crew.school_crew import schoolcrew

# Initialize FastAPI app
app = FastAPI(
    title="School Crew API",
    description="API for finding schools based on location, grade, and curriculum",
    version="1.0.0"
)

# Pydantic models for request/response
class SchoolSearchRequest(BaseModel):
    location: str = Field(
        default="Bangalore | use my current location",
        description="Location to search for schools",
        example="Mumbai"
    )
    grade: str = Field(
        default="1st Grade",
        description="Grade level you're interested in",
        example="5th Grade"
    )
    curriculum: str = Field(
        default="CBSE",
        description="Preferred curriculum",
        example="ICSE"
    )

class SchoolSearchResponse(BaseModel):
    success: bool
    message: str
    data: Optional[str] = None

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "School Crew API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "school-crew-api"}

# Main endpoint for school search
@app.post("/search-schools", response_model=SchoolSearchResponse)
async def search_schools(request: SchoolSearchRequest):
    """
    Search for schools based on location, grade, and curriculum preferences.
    
    - **location**: The city or area where you want to find schools
    - **grade**: The grade level (e.g., "1st Grade", "10th Grade") 
    - **curriculum**: The curriculum type (e.g., "CBSE", "ICSE", "IB")
    """
    try:
        # Initialize school crew
        crew_instance = schoolcrew()
        
        # Prepare inputs
        inputs = {
            "location": request.location,
            "grade": request.grade, 
            "curriculum": request.curriculum
        }
        
        # Execute the crew
        result = crew_instance.crew().kickoff(inputs=inputs)
        
        return SchoolSearchResponse(
            success=True,
            message="School search completed successfully",
            data=str(result)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing school search: {str(e)}"
        )

# Alternative GET endpoint for simple queries
@app.get("/search-schools/{location}")
async def search_schools_simple(
    location: str,
    grade: str = "1st Grade",
    curriculum: str = "CBSE"
):
    """
    Simple GET endpoint for school search with path parameter.
    """
    try:
        crew_instance = schoolcrew()
        
        inputs = {
            "location": location,
            "grade": grade,
            "curriculum": curriculum
        }
        
        result = crew_instance.crew().kickoff(inputs=inputs)
        
        return {
            "success": True,
            "location": location,
            "grade": grade,
            "curriculum": curriculum,
            "results": str(result)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing school search: {str(e)}"
        )

# Endpoint to get supported curricula
@app.get("/curricula")
async def get_supported_curricula():
    """Get list of supported curricula"""
    return {
        "supported_curricula": [
            "CBSE",
            "ICSE", 
            "IB",
            "State Board",
            "IGCSE",
            "Cambridge",
            "Montessori"
        ]
    }

# Endpoint to get supported grades
@app.get("/grades")
async def get_supported_grades():
    """Get list of supported grade levels"""
    return {
        "supported_grades": [
            "Nursery",
            "Pre-KG", 
            "LKG",
            "UKG",
            "1st Grade",
            "2nd Grade",
            "3rd Grade",
            "4th Grade", 
            "5th Grade",
            "6th Grade",
            "7th Grade",
            "8th Grade",
            "9th Grade",
            "10th Grade",
            "11th Grade",
            "12th Grade"
        ]

    }
