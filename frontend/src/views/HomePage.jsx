import React from 'react';
import { Typography, Box, Paper, Grid, Card, CardContent } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import WorkIcon from '@mui/icons-material/Work';
import TimelineIcon from '@mui/icons-material/Timeline';
import AccountTreeIcon from '@mui/icons-material/AccountTree';

const HomePage = () => {
  return (
    <Box>
      <Typography variant="h3" gutterBottom>
        Welcome to IT EduGraph
      </Typography>
      <Typography variant="h6" color="text.secondary" paragraph>
        Your intelligent companion for IT learning and career development
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 4, bgcolor: '#e3f2fd' }}>
        <Typography variant="body1" paragraph>
          IT EduGraph is powered by the <strong>Genesis Knowledge Framework (GKF)</strong> - an
          ontology-driven knowledge ecosystem that combines foundational knowledge from global
          datasets with experiential knowledge from community interactions.
        </Typography>
        <Typography variant="body2">
          Explore skills, discover courses, analyze career paths, and generate personalized learning
          roadmaps using semantic web technologies and AI reasoning.
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <SchoolIcon fontSize="large" color="primary" sx={{ mr: 2 }} />
                <Typography variant="h5">Skills Explorer</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Browse and explore IT skills, their prerequisites, and relationships in the
                knowledge graph.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <WorkIcon fontSize="large" color="primary" sx={{ mr: 2 }} />
                <Typography variant="h5">Job Analyzer</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Analyze job requirements, discover skill gaps, and get course recommendations for
                your target role.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TimelineIcon fontSize="large" color="primary" sx={{ mr: 2 }} />
                <Typography variant="h5">Learning Paths</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Generate personalized learning roadmaps from your current skills to your career
                goals.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AccountTreeIcon fontSize="large" color="primary" sx={{ mr: 2 }} />
                <Typography variant="h5">Knowledge Graph</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Visualize the entire IT knowledge ecosystem with interactive graph visualization.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HomePage;
