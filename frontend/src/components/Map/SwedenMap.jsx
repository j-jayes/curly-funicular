import React, { useEffect, useRef } from 'react';
import { Box, Typography } from '@mui/material';
import * as d3 from 'd3';

const SwedenMap = ({ data, selectedRegion }) => {
  const svgRef = useRef();

  useEffect(() => {
    drawMap();
  }, [data, selectedRegion]);

  const drawMap = () => {
    // This is a simplified Sweden map visualization
    // In production, you would load actual GeoJSON data for Swedish regions
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 400;
    const height = 500;

    svg.attr('width', width).attr('height', height);

    // Sample regions (simplified representation)
    const regions = [
      { name: 'Stockholm', code: '01', x: 200, y: 150 },
      { name: 'Uppsala', code: '03', x: 200, y: 100 },
      { name: 'Södermanland', code: '04', x: 180, y: 180 },
      { name: 'Östergötland', code: '05', x: 180, y: 220 },
      { name: 'Jönköping', code: '06', x: 150, y: 260 },
      { name: 'Kronoberg', code: '07', x: 130, y: 300 },
      { name: 'Kalmar', code: '08', x: 180, y: 280 },
      { name: 'Gotland', code: '09', x: 250, y: 260 },
      { name: 'Blekinge', code: '10', x: 150, y: 340 },
      { name: 'Skåne', code: '12', x: 130, y: 380 },
    ];

    const circles = svg.selectAll('circle')
      .data(regions)
      .enter()
      .append('circle')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', 15)
      .attr('fill', d => {
        if (selectedRegion && d.code === selectedRegion) {
          return '#1976d2';
        }
        return '#90caf9';
      })
      .attr('stroke', '#1976d2')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this).attr('r', 20);
      })
      .on('mouseout', function(event, d) {
        d3.select(this).attr('r', 15);
      });

    svg.selectAll('text')
      .data(regions)
      .enter()
      .append('text')
      .attr('x', d => d.x)
      .attr('y', d => d.y + 30)
      .attr('text-anchor', 'middle')
      .style('font-size', '10px')
      .text(d => d.name);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Sweden Map
      </Typography>
      <Box display="flex" justifyContent="center">
        <svg ref={svgRef}></svg>
      </Box>
    </Box>
  );
};

export default SwedenMap;
