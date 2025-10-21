import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box, Button } from '@mui/material';
import HomePage from './views/HomePage';
import SkillsExplorer from './views/SkillsExplorer';
import CoursesView from './views/CoursesView';
import JobsView from './views/JobsView';
import LearningPathGenerator from './views/LearningPathGenerator';
import KnowledgeGraphView from './components/KnowledgeGraphView';

function App() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              IT EduGraph - Genesis Knowledge Framework
            </Typography>
            <Button color="inherit" component={Link} to="/">Home</Button>
            <Button color="inherit" component={Link} to="/skills">Skills</Button>
            <Button color="inherit" component={Link} to="/courses">Courses</Button>
            <Button color="inherit" component={Link} to="/jobs">Jobs</Button>
            <Button color="inherit" component={Link} to="/learning-path">Learning Path</Button>
            <Button color="inherit" component={Link} to="/graph">Knowledge Graph</Button>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/skills" element={<SkillsExplorer />} />
            <Route path="/courses" element={<CoursesView />} />
            <Route path="/jobs" element={<JobsView />} />
            <Route path="/learning-path" element={<LearningPathGenerator />} />
            <Route path="/graph" element={<KnowledgeGraphView />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  );
}

export default App;
