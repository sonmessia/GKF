"""
FastAPI REST API Gateway
Exposes knowledge graph and intelligent services via REST API.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

# Initialize FastAPI app
app = FastAPI(
    title="Genesis Knowledge Framework API",
    description="RESTful API for IT EduGraph - Intelligent Learning & Career Recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ===== Pydantic Models =====

class Skill(BaseModel):
    uri: str
    name: str
    level: Optional[str] = None
    description: Optional[str] = None


class Course(BaseModel):
    uri: str
    name: str
    url: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[str] = None
    rating: Optional[float] = None


class Job(BaseModel):
    uri: str
    title: str
    salary: Optional[float] = None
    description: Optional[str] = None


class LearningPathRequest(BaseModel):
    target_job_uri: str
    current_skills: List[str]


class SkillRecommendationRequest(BaseModel):
    user_skills: List[str]
    top_k: int = 5


class InteractionData(BaseModel):
    user_id: str
    interaction_type: str
    entity_uri: str
    metadata: Dict[str, Any] = {}


# ===== Dependency Injection (Placeholder) =====
# In production, initialize these from config

def get_triplestore_manager():
    """Placeholder for triplestore manager dependency"""
    from backend.layer2_knowledge.triplestore.triplestore_manager import TripleStoreManager
    config = {
        'endpoint': 'http://localhost:7200/repositories/gkf'
    }
    return TripleStoreManager(config)


def get_reasoning_engine():
    """Placeholder for reasoning engine dependency"""
    from backend.layer3_intelligence.reasoning.reasoning_engine import ReasoningEngine
    from backend.layer2_knowledge.ontology.ontology_manager import OntologyManager

    triplestore = get_triplestore_manager()
    ontology_manager = OntologyManager()

    return ReasoningEngine(triplestore, ontology_manager)


def get_knowledge_integrator():
    """Placeholder for knowledge integrator dependency"""
    from backend.layer2_knowledge.integration.knowledge_integrator import KnowledgeIntegrator
    triplestore = get_triplestore_manager()
    return KnowledgeIntegrator(triplestore)


# ===== API Endpoints =====

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Genesis Knowledge Framework API",
        "version": "1.0.0",
        "description": "Ontology-driven intelligent knowledge ecosystem"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        triplestore = get_triplestore_manager()
        connected = triplestore.check_connection()
        return {
            "status": "healthy" if connected else "degraded",
            "triplestore": "connected" if connected else "disconnected"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# ===== Skills API =====

@app.get("/api/skills", response_model=List[Dict])
async def get_all_skills():
    """Get all skills from knowledge graph"""
    try:
        triplestore = get_triplestore_manager()
        results = triplestore.get_all_skills()
        return results
    except Exception as e:
        logger.error(f"Failed to get skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills/{skill_id}")
async def get_skill(skill_id: str):
    """Get detailed information about a specific skill"""
    try:
        triplestore = get_triplestore_manager()
        skill_uri = f"http://gkf.org/data/Skill/{skill_id}"

        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT ?property ?value
        WHERE {{
            <{skill_uri}> ?property ?value .
        }}
        """

        results = triplestore.query(query)
        if not results:
            raise HTTPException(status_code=404, detail="Skill not found")

        return {"uri": skill_uri, "properties": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills/{skill_id}/prerequisites")
async def get_skill_prerequisites(skill_id: str):
    """Get prerequisite skills for a given skill"""
    try:
        reasoning_engine = get_reasoning_engine()
        skill_uri = f"http://gkf.org/data/Skill/{skill_id}"

        prerequisites = reasoning_engine.infer_skill_prerequisites(skill_uri)
        return {"skill_uri": skill_uri, "prerequisites": prerequisites}
    except Exception as e:
        logger.error(f"Failed to get prerequisites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills/{skill_id}/related")
async def get_related_skills(skill_id: str, depth: int = Query(2, ge=1, le=5)):
    """Get related skills"""
    try:
        reasoning_engine = get_reasoning_engine()
        skill_uri = f"http://gkf.org/data/Skill/{skill_id}"

        related = reasoning_engine.find_related_skills(skill_uri, depth)
        return {"skill_uri": skill_uri, "related_skills": related}
    except Exception as e:
        logger.error(f"Failed to get related skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Courses API =====

@app.get("/api/courses")
async def get_courses(skill: Optional[str] = None, difficulty: Optional[str] = None):
    """Get courses, optionally filtered by skill or difficulty"""
    try:
        triplestore = get_triplestore_manager()

        filters = []
        if skill:
            filters.append(f'?course gkf:teaches ?skill . ?skill gkf:skillName "{skill}"')
        if difficulty:
            filters.append(f'?course gkf:difficulty "{difficulty}"')

        filter_clause = " . ".join(filters) if filters else ""

        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT ?course ?courseName ?url ?difficulty
        WHERE {{
            ?course a gkf:Course ;
                    gkf:courseName ?courseName .
            OPTIONAL {{ ?course gkf:courseURL ?url }}
            OPTIONAL {{ ?course gkf:difficulty ?difficulty }}
            {filter_clause}
        }}
        LIMIT 100
        """

        results = triplestore.query(query)
        return results
    except Exception as e:
        logger.error(f"Failed to get courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/courses/skill/{skill_name}")
async def find_courses_for_skill(skill_name: str):
    """Find courses that teach a specific skill"""
    try:
        triplestore = get_triplestore_manager()
        results = triplestore.find_courses_for_skill(skill_name)
        return results
    except Exception as e:
        logger.error(f"Failed to find courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Jobs API =====

@app.get("/api/jobs")
async def get_jobs():
    """Get all job listings"""
    try:
        triplestore = get_triplestore_manager()

        query = """
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT ?job ?jobTitle ?salary
        WHERE {
            ?job a gkf:Job ;
                 gkf:jobTitle ?jobTitle .
            OPTIONAL { ?job gkf:salary ?salary }
        }
        LIMIT 100
        """

        results = triplestore.query(query)
        return results
    except Exception as e:
        logger.error(f"Failed to get jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}/skills")
async def get_job_required_skills(job_id: str):
    """Get skills required for a specific job"""
    try:
        triplestore = get_triplestore_manager()
        job_uri = f"http://gkf.org/data/Job/{job_id}"

        results = triplestore.get_job_required_skills(job_uri)
        return {"job_uri": job_uri, "required_skills": results}
    except Exception as e:
        logger.error(f"Failed to get job skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}/recommended-courses")
async def get_recommended_courses_for_job(job_id: str):
    """Get recommended courses for a job"""
    try:
        reasoning_engine = get_reasoning_engine()
        job_uri = f"http://gkf.org/data/Job/{job_id}"

        recommendations = reasoning_engine.recommend_courses_for_job(job_uri)
        return {"job_uri": job_uri, "recommended_courses": recommendations}
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Intelligent Recommendations API =====

@app.post("/api/recommendations/learning-path")
async def generate_learning_path(request: LearningPathRequest):
    """Generate personalized learning path"""
    try:
        reasoning_engine = get_reasoning_engine()

        learning_path = reasoning_engine.generate_learning_path(
            request.target_job_uri,
            request.current_skills
        )

        return {
            "target_job": request.target_job_uri,
            "current_skills": request.current_skills,
            "learning_path": learning_path
        }
    except Exception as e:
        logger.error(f"Failed to generate learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommendations/next-skills")
async def recommend_next_skills(request: SkillRecommendationRequest):
    """Recommend next skills to learn"""
    try:
        reasoning_engine = get_reasoning_engine()

        recommendations = reasoning_engine.recommend_next_skills(
            request.user_skills,
            request.top_k
        )

        return {
            "user_skills": request.user_skills,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Failed to recommend skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations/career-path")
async def analyze_career_path(start_job: str, end_job: str):
    """Analyze career progression path"""
    try:
        reasoning_engine = get_reasoning_engine()

        analysis = reasoning_engine.analyze_career_path(start_job, end_job)

        return {
            "start_job": start_job,
            "end_job": end_job,
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Failed to analyze career path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Experiential Knowledge API =====

@app.post("/api/interactions")
async def record_interaction(interaction: InteractionData):
    """Record user interaction (experiential knowledge)"""
    try:
        integrator = get_knowledge_integrator()

        success = integrator.add_experiential_knowledge({
            'user_id': interaction.user_id,
            'interaction_type': interaction.interaction_type,
            'entity_uri': interaction.entity_uri,
            'metadata': interaction.metadata
        })

        if success:
            return {"status": "success", "message": "Interaction recorded"}
        else:
            raise HTTPException(status_code=500, detail="Failed to record interaction")

    except Exception as e:
        logger.error(f"Failed to record interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/history")
async def get_user_learning_history(user_id: str):
    """Get user's learning history"""
    try:
        integrator = get_knowledge_integrator()
        history = integrator.get_user_learning_history(user_id)

        return {"user_id": user_id, "history": history}
    except Exception as e:
        logger.error(f"Failed to get user history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== SPARQL Endpoint =====

@app.post("/sparql")
async def sparql_query(query: str):
    """Execute raw SPARQL query"""
    try:
        triplestore = get_triplestore_manager()
        results = triplestore.query(query)
        return {"query": query, "results": results}
    except Exception as e:
        logger.error(f"SPARQL query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
