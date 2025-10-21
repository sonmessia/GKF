import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Chip,
  Divider
} from '@mui/material';
import { generateLearningPath } from '../services/api';

const LearningPathGenerator = () => {
  const [targetJob, setTargetJob] = useState('');
  const [currentSkills, setCurrentSkills] = useState('');
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGeneratePath = async () => {
    try {
      setLoading(true);
      setError(null);

      const skillsArray = currentSkills
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0)
        .map(s => `http://gkf.org/data/Skill/${s}`);

      const result = await generateLearningPath(targetJob, skillsArray);
      setLearningPath(result);
      setLoading(false);
    } catch (err) {
      console.error('Error generating learning path:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Learning Path Generator
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Generate a personalized learning roadmap from your current skills to your target job.
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <TextField
          fullWidth
          label="Target Job URI"
          placeholder="http://gkf.org/data/Job/software-engineer"
          value={targetJob}
          onChange={(e) => setTargetJob(e.target.value)}
          sx={{ mb: 2 }}
        />
        <TextField
          fullWidth
          label="Current Skills (comma-separated IDs)"
          placeholder="python, javascript, html"
          value={currentSkills}
          onChange={(e) => setCurrentSkills(e.target.value)}
          sx={{ mb: 2 }}
          multiline
          rows={2}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleGeneratePath}
          disabled={loading || !targetJob}
        >
          Generate Learning Path
        </Button>
      </Paper>

      {loading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Paper elevation={2} sx={{ p: 2, bgcolor: '#ffebee', mb: 3 }}>
          <Typography color="error">Error: {error}</Typography>
        </Paper>
      )}

      {learningPath && learningPath.learning_path && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Your Personalized Learning Path
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Target Job: <strong>{learningPath.target_job}</strong>
          </Typography>

          <Divider sx={{ my: 2 }} />

          <List>
            {learningPath.learning_path.map((step, index) => (
              <ListItem
                key={index}
                sx={{
                  display: 'block',
                  mb: 2,
                  bgcolor: '#f5f5f5',
                  borderRadius: 1,
                  p: 2
                }}
              >
                <Typography variant="h6" gutterBottom>
                  Step {index + 1}: {step.skill}
                </Typography>

                {step.prerequisites && step.prerequisites.length > 0 && (
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Prerequisites:
                    </Typography>
                    {step.prerequisites.map((prereq, i) => (
                      <Chip
                        key={i}
                        label={prereq}
                        size="small"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                )}

                <Typography variant="body2" fontWeight="bold" gutterBottom>
                  Recommended Courses:
                </Typography>
                <List dense>
                  {step.recommended_courses && step.recommended_courses.map((course, i) => (
                    <ListItem key={i}>
                      <ListItemText
                        primary={course.courseName?.value || 'Course'}
                        secondary={`Difficulty: ${course.difficulty?.value || 'N/A'}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default LearningPathGenerator;
