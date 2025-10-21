import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Box, Paper, Typography, CircularProgress } from '@mui/material';
import { getSkills } from '../services/api';

const KnowledgeGraphView = () => {
  const svgRef = useRef();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadGraphData = async () => {
      try {
        setLoading(true);
        const skills = await getSkills();

        // Transform API data to D3 graph format
        const nodes = skills.map((skill, index) => ({
          id: skill.skill?.value || `node-${index}`,
          name: skill.skillName?.value || 'Unknown',
          level: skill.level?.value || 'Unknown',
        }));

        // Create sample links (in production, fetch from API)
        const links = [];
        for (let i = 0; i < Math.min(nodes.length - 1, 20); i++) {
          links.push({
            source: nodes[i].id,
            target: nodes[i + 1].id,
            type: 'relatedTo',
          });
        }

        renderGraph({ nodes, links });
        setLoading(false);
      } catch (err) {
        console.error('Error loading graph:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    loadGraphData();
  }, []);

  const renderGraph = (data) => {
    const width = 900;
    const height = 600;

    // Clear previous SVG
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height]);

    // Create force simulation
    const simulation = d3
      .forceSimulation(data.nodes)
      .force(
        'link',
        d3.forceLink(data.links).id((d) => d.id).distance(100)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(50));

    // Add links
    const link = svg
      .append('g')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke-width', 2);

    // Add nodes
    const node = svg
      .append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .selectAll('circle')
      .data(data.nodes)
      .join('circle')
      .attr('r', 20)
      .attr('fill', (d) => {
        // Color by skill level
        const colors = {
          Beginner: '#4caf50',
          Intermediate: '#2196f3',
          Advanced: '#ff9800',
          Expert: '#f44336',
          Unknown: '#9e9e9e',
        };
        return colors[d.level] || colors.Unknown;
      })
      .call(drag(simulation));

    // Add labels
    const label = svg
      .append('g')
      .selectAll('text')
      .data(data.nodes)
      .join('text')
      .text((d) => d.name)
      .attr('font-size', 12)
      .attr('dx', 25)
      .attr('dy', 4);

    // Add tooltips
    node.append('title').text((d) => `${d.name}\nLevel: ${d.level}`);

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d) => d.source.x)
        .attr('y1', (d) => d.source.y)
        .attr('x2', (d) => d.target.x)
        .attr('y2', (d) => d.target.y);

      node.attr('cx', (d) => d.x).attr('cy', (d) => d.y);

      label.attr('x', (d) => d.x).attr('y', (d) => d.y);
    });

    // Drag behavior
    function drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }

      return d3.drag().on('start', dragstarted).on('drag', dragged).on('end', dragended);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Typography color="error">Error loading knowledge graph: {error}</Typography>
      </Box>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Knowledge Graph Visualization
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Interactive visualization of skills and their relationships
      </Typography>
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
        <svg ref={svgRef}></svg>
      </Box>
      <Box sx={{ mt: 2 }}>
        <Typography variant="caption">
          <strong>Legend:</strong> Green = Beginner | Blue = Intermediate | Orange = Advanced | Red = Expert
        </Typography>
      </Box>
    </Paper>
  );
};

export default KnowledgeGraphView;
