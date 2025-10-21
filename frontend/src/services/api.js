import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Skills API
export const getSkills = async () => {
  const response = await api.get('/api/skills');
  return response.data;
};

export const getSkill = async (skillId) => {
  const response = await api.get(`/api/skills/${skillId}`);
  return response.data;
};

export const getSkillPrerequisites = async (skillId) => {
  const response = await api.get(`/api/skills/${skillId}/prerequisites`);
  return response.data;
};

export const getRelatedSkills = async (skillId, depth = 2) => {
  const response = await api.get(`/api/skills/${skillId}/related`, { params: { depth } });
  return response.data;
};

// Courses API
export const getCourses = async (filters = {}) => {
  const response = await api.get('/api/courses', { params: filters });
  return response.data;
};

export const getCoursesForSkill = async (skillName) => {
  const response = await api.get(`/api/courses/skill/${skillName}`);
  return response.data;
};

// Jobs API
export const getJobs = async () => {
  const response = await api.get('/api/jobs');
  return response.data;
};

export const getJobRequiredSkills = async (jobId) => {
  const response = await api.get(`/api/jobs/${jobId}/skills`);
  return response.data;
};

export const getRecommendedCoursesForJob = async (jobId) => {
  const response = await api.get(`/api/jobs/${jobId}/recommended-courses`);
  return response.data;
};

// Recommendations API
export const generateLearningPath = async (targetJobUri, currentSkills) => {
  const response = await api.post('/api/recommendations/learning-path', {
    target_job_uri: targetJobUri,
    current_skills: currentSkills,
  });
  return response.data;
};

export const recommendNextSkills = async (userSkills, topK = 5) => {
  const response = await api.post('/api/recommendations/next-skills', {
    user_skills: userSkills,
    top_k: topK,
  });
  return response.data;
};

export const analyzeCareerPath = async (startJob, endJob) => {
  const response = await api.get('/api/recommendations/career-path', {
    params: { start_job: startJob, end_job: endJob },
  });
  return response.data;
};

// Interactions API
export const recordInteraction = async (interactionData) => {
  const response = await api.post('/api/interactions', interactionData);
  return response.data;
};

export const getUserLearningHistory = async (userId) => {
  const response = await api.get(`/api/users/${userId}/history`);
  return response.data;
};

// SPARQL API
export const executeSparqlQuery = async (query) => {
  const response = await api.post('/sparql', { query });
  return response.data;
};

// Health Check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
