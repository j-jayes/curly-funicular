import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import * as d3 from 'd3';

// GeoJSON URL for Swedish regions (NUTS-2 level)
const GEOJSON_URL = 'https://raw.githubusercontent.com/okfse/sweden-geojson/master/swedish_regions.geojson';

// Mapping from NUTS region names to GeoJSON feature names
const REGION_NAME_MAP = {
  'Sweden': null, // Skip national total
  'Stockholm': 'Stockholm',
  'East-Central Sweden': 'Östra Mellansverige',
  'Småland and islands': 'Småland med öarna', 
  'South Sweden': 'Sydsverige',
  'West Sweden': 'Västsverige',
  'North-Central Sweden': 'Norra Mellansverige',
  'Central Norrland': 'Mellersta Norrland',
  'Upper Norrland': 'Övre Norrland',
};

const SwedenMap = ({ data, selectedRegion, onRegionClick }) => {
  const svgRef = useRef();
  const [geoData, setGeoData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load GeoJSON on mount
  useEffect(() => {
    const loadGeoJSON = async () => {
      try {
        const response = await fetch(GEOJSON_URL);
        const geojson = await response.json();
        setGeoData(geojson);
        setLoading(false);
      } catch (error) {
        console.error('Error loading GeoJSON:', error);
        setLoading(false);
      }
    };
    loadGeoJSON();
  }, []);

  // Draw map when data or selection changes
  useEffect(() => {
    if (geoData) {
      drawMap();
    }
  }, [geoData, data, selectedRegion]);

  // Aggregate income by region
  const getRegionIncomeMap = () => {
    const regionIncome = {};
    if (data && data.length > 0) {
      data.forEach(item => {
        const region = item.region;
        const mappedName = REGION_NAME_MAP[region];
        if (mappedName && item.monthly_salary) {
          if (!regionIncome[mappedName] || item.monthly_salary > regionIncome[mappedName]) {
            regionIncome[mappedName] = item.monthly_salary;
          }
        }
      });
    }
    return regionIncome;
  };

  const drawMap = () => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 400;
    const height = 500;

    svg.attr('width', width).attr('height', height);

    // Create projection for Sweden
    const projection = d3.geoMercator()
      .center([17, 62.5])
      .scale(800)
      .translate([width / 2, height / 2]);

    const pathGenerator = d3.geoPath().projection(projection);

    // Get income data for coloring
    const regionIncome = getRegionIncomeMap();
    const incomeValues = Object.values(regionIncome);
    const minIncome = incomeValues.length > 0 ? Math.min(...incomeValues) : 40000;
    const maxIncome = incomeValues.length > 0 ? Math.max(...incomeValues) : 60000;

    // Color scale
    const colorScale = d3.scaleSequential()
      .domain([minIncome, maxIncome])
      .interpolator(d3.interpolateBlues);

    // Draw regions
    svg.selectAll('path')
      .data(geoData.features)
      .enter()
      .append('path')
      .attr('d', pathGenerator)
      .attr('fill', d => {
        const regionName = d.properties.name;
        const income = regionIncome[regionName];
        return income ? colorScale(income) : '#e0e0e0';
      })
      .attr('stroke', '#333')
      .attr('stroke-width', 0.5)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('stroke-width', 2)
          .attr('stroke', '#1976d2');
        
        // Show tooltip
        const regionName = d.properties.name;
        const income = regionIncome[regionName];
        
        svg.append('text')
          .attr('id', 'tooltip')
          .attr('x', event.offsetX || 200)
          .attr('y', event.offsetY || 250)
          .attr('text-anchor', 'middle')
          .style('font-size', '12px')
          .style('font-weight', 'bold')
          .style('fill', '#333')
          .text(`${regionName}: ${income ? `${Math.round(income).toLocaleString()} SEK` : 'No data'}`);
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('stroke-width', 0.5)
          .attr('stroke', '#333');
        svg.select('#tooltip').remove();
      })
      .on('click', function(event, d) {
        if (onRegionClick) {
          onRegionClick(d.properties.name);
        }
      });

    // Add legend
    const legendWidth = 150;
    const legendHeight = 10;
    
    const legend = svg.append('g')
      .attr('transform', `translate(20, ${height - 40})`);

    const legendScale = d3.scaleLinear()
      .domain([minIncome, maxIncome])
      .range([0, legendWidth]);

    const legendAxis = d3.axisBottom(legendScale)
      .ticks(3)
      .tickFormat(d => `${Math.round(d/1000)}k`);

    // Gradient for legend
    const gradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', 'income-gradient')
      .attr('x1', '0%')
      .attr('x2', '100%');

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', colorScale(minIncome));

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', colorScale(maxIncome));

    legend.append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#income-gradient)');

    legend.append('g')
      .attr('transform', `translate(0, ${legendHeight})`)
      .call(legendAxis);

    legend.append('text')
      .attr('x', legendWidth / 2)
      .attr('y', -5)
      .attr('text-anchor', 'middle')
      .style('font-size', '10px')
      .text('Monthly Salary (SEK)');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Average Income by Region
      </Typography>
      <Box display="flex" justifyContent="center">
        <svg ref={svgRef}></svg>
      </Box>
    </Box>
  );
};

export default SwedenMap;
