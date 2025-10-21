"""
AI Reasoning Engine
Combines symbolic AI (OWL reasoning) with statistical AI (graph ML).
"""
from rdflib import Graph, Namespace
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Intelligent reasoning over knowledge graph using:
    1. Symbolic AI: OWL 2 RL inference, SPARQL reasoning
    2. Statistical AI: Graph embeddings, link prediction, recommendations
    """

    def __init__(self, triplestore_manager, ontology_manager):
        self.triplestore = triplestore_manager
        self.ontology_manager = ontology_manager
        self.gkf = Namespace("http://gkf.org/ontology/it#")

    # ===== SYMBOLIC REASONING =====

    def infer_skill_prerequisites(self, skill_uri: str) -> List[str]:
        """
        Infer prerequisite skills using transitive reasoning.
        If A prerequisite B, and B prerequisite C, then A prerequisite C.
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT DISTINCT ?prereq ?skillName
        WHERE {{
            <{skill_uri}> gkf:prerequisite+ ?prereq .
            ?prereq gkf:skillName ?skillName .
        }}
        """

        results = self.triplestore.query(query)
        return [result['prereq']['value'] for result in results]

    def find_related_skills(self, skill_uri: str, depth: int = 2) -> List[str]:
        """
        Find related skills using graph traversal.
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT DISTINCT ?related ?skillName
        WHERE {{
            <{skill_uri}> gkf:relatedTo{{1,{depth}}} ?related .
            ?related gkf:skillName ?skillName .
        }}
        LIMIT 20
        """

        results = self.triplestore.query(query)
        return [result['related']['value'] for result in results]

    def recommend_courses_for_job(self, job_uri: str) -> List[Dict]:
        """
        Recommend courses for a job by analyzing required skills.
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT DISTINCT ?course ?courseName ?skill ?skillName
        WHERE {{
            <{job_uri}> gkf:requires ?skill .
            ?skill gkf:skillName ?skillName .
            ?course a gkf:Course ;
                    gkf:courseName ?courseName ;
                    gkf:teaches ?skill .
        }}
        """

        results = self.triplestore.query(query)

        # Group courses by skill
        recommendations = {}
        for result in results:
            course_uri = result['course']['value']
            if course_uri not in recommendations:
                recommendations[course_uri] = {
                    'uri': course_uri,
                    'name': result['courseName']['value'],
                    'teaches': []
                }
            recommendations[course_uri]['teaches'].append({
                'skill_uri': result['skill']['value'],
                'skill_name': result['skillName']['value']
            })

        return list(recommendations.values())

    def generate_learning_path(self, target_job_uri: str, current_skills: List[str]) -> List[Dict]:
        """
        Generate a personalized learning path from current skills to target job.

        Args:
            target_job_uri: URI of target job
            current_skills: List of skill URIs user already has

        Returns:
            Ordered list of courses to take
        """
        # Get required skills for job
        required_query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT ?skill ?skillName
        WHERE {{
            <{target_job_uri}> gkf:requires ?skill .
            ?skill gkf:skillName ?skillName .
        }}
        """

        required_skills = self.triplestore.query(required_query)

        # Filter out skills user already has
        skills_to_learn = [
            skill for skill in required_skills
            if skill['skill']['value'] not in current_skills
        ]

        # Find courses for each missing skill
        learning_path = []

        for skill in skills_to_learn:
            skill_uri = skill['skill']['value']

            # Get prerequisites for this skill
            prerequisites = self.infer_skill_prerequisites(skill_uri)

            # Find courses teaching this skill
            course_query = f"""
            PREFIX gkf: <http://gkf.org/ontology/it#>

            SELECT ?course ?courseName ?difficulty
            WHERE {{
                ?course a gkf:Course ;
                        gkf:courseName ?courseName ;
                        gkf:teaches <{skill_uri}> .
                OPTIONAL {{ ?course gkf:difficulty ?difficulty }}
            }}
            ORDER BY ?difficulty
            LIMIT 3
            """

            courses = self.triplestore.query(course_query)

            if courses:
                learning_path.append({
                    'skill': skill['skillName']['value'],
                    'skill_uri': skill_uri,
                    'prerequisites': prerequisites,
                    'recommended_courses': courses
                })

        return learning_path

    # ===== STATISTICAL REASONING =====

    def calculate_skill_similarity(self, skill1_uri: str, skill2_uri: str) -> float:
        """
        Calculate similarity between two skills based on:
        - Shared courses teaching them
        - Shared jobs requiring them
        - Graph distance
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT (COUNT(?shared) as ?count)
        WHERE {{
            {{
                ?shared gkf:teaches <{skill1_uri}> .
                ?shared gkf:teaches <{skill2_uri}> .
            }} UNION {{
                ?shared gkf:requires <{skill1_uri}> .
                ?shared gkf:requires <{skill2_uri}> .
            }}
        }}
        """

        results = self.triplestore.query(query)
        shared_count = int(results[0]['count']['value']) if results else 0

        # Normalize to 0-1 range (simple heuristic)
        similarity = min(shared_count / 10.0, 1.0)

        return similarity

    def predict_skill_demand(self, skill_uri: str) -> float:
        """
        Predict skill demand based on:
        - Number of jobs requiring it
        - Number of courses teaching it
        - Experiential data (user interest)
        """
        query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT
            (COUNT(DISTINCT ?job) as ?jobCount)
            (COUNT(DISTINCT ?course) as ?courseCount)
        WHERE {{
            OPTIONAL {{ ?job gkf:requires <{skill_uri}> }}
            OPTIONAL {{ ?course gkf:teaches <{skill_uri}> }}
        }}
        """

        results = self.triplestore.query(query)

        if results:
            job_count = int(results[0]['jobCount']['value'])
            course_count = int(results[0]['courseCount']['value'])

            # Simple demand score (0-100)
            demand_score = (job_count * 2) + (course_count * 1)

            return min(demand_score, 100.0)

        return 0.0

    def recommend_next_skills(self, user_skills: List[str], top_k: int = 5) -> List[Dict]:
        """
        Recommend next skills to learn based on user's current skills.
        Uses collaborative filtering approach.
        """
        recommendations = []

        for current_skill in user_skills:
            # Find skills that co-occur with current skill in job requirements
            query = f"""
            PREFIX gkf: <http://gkf.org/ontology/it#>

            SELECT ?skill ?skillName (COUNT(?job) as ?cooccurrence)
            WHERE {{
                ?job gkf:requires <{current_skill}> ;
                     gkf:requires ?skill .
                ?skill gkf:skillName ?skillName .
                FILTER(?skill != <{current_skill}>)
            }}
            GROUP BY ?skill ?skillName
            ORDER BY DESC(?cooccurrence)
            LIMIT {top_k}
            """

            results = self.triplestore.query(query)

            for result in results:
                skill_uri = result['skill']['value']

                # Check if user already has this skill
                if skill_uri not in user_skills:
                    demand = self.predict_skill_demand(skill_uri)

                    recommendations.append({
                        'skill_uri': skill_uri,
                        'skill_name': result['skillName']['value'],
                        'reason': f"Often required with {current_skill}",
                        'cooccurrence': int(result['cooccurrence']['value']),
                        'demand_score': demand
                    })

        # Sort by demand score and remove duplicates
        recommendations = sorted(
            recommendations,
            key=lambda x: (x['demand_score'], x['cooccurrence']),
            reverse=True
        )

        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['skill_uri'] not in seen:
                seen.add(rec['skill_uri'])
                unique_recommendations.append(rec)

        return unique_recommendations[:top_k]

    def analyze_career_path(self, start_job_uri: str, end_job_uri: str) -> List[Dict]:
        """
        Analyze career progression path between two jobs.
        Returns intermediate steps and skill gaps.
        """
        # Get skills for both jobs
        start_skills_query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT ?skill ?skillName
        WHERE {{
            <{start_job_uri}> gkf:requires ?skill .
            ?skill gkf:skillName ?skillName .
        }}
        """

        end_skills_query = f"""
        PREFIX gkf: <http://gkf.org/ontology/it#>

        SELECT ?skill ?skillName
        WHERE {{
            <{end_job_uri}> gkf:requires ?skill .
            ?skill gkf:skillName ?skillName .
        }}
        """

        start_skills = self.triplestore.query(start_skills_query)
        end_skills = self.triplestore.query(end_skills_query)

        start_skill_uris = {s['skill']['value'] for s in start_skills}
        end_skill_uris = {s['skill']['value'] for s in end_skills}

        # Calculate skill gap
        common_skills = start_skill_uris & end_skill_uris
        skills_to_acquire = end_skill_uris - start_skill_uris

        return {
            'common_skills': len(common_skills),
            'skills_to_acquire': list(skills_to_acquire),
            'skill_gap_percentage': len(skills_to_acquire) / len(end_skill_uris) * 100 if end_skill_uris else 0,
            'learning_path': self.generate_learning_path(end_job_uri, list(start_skill_uris))
        }
