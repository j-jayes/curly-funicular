import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import * as d3 from 'd3';

// Eurostat NUTS-2 GeoJSON - proper Swedish regions  
const GEOJSON_URL = 'https://raw.githubusercontent.com/eurostat/Nuts2json/master/pub/v2/2021/4326/20M/nutsrg_2.json';

// Dark2 Brewer color palette
const DARK2 = ['#1b9e77','#d95f02','#7570b3','#e7298a','#66a61e','#e6ab02','#a6761d','#666666'];

// Mapping from API region names (English) to GeoJSON region names (Swedish)
const REGION_NAME_MAP = {
  'Sweden': null, // Skip national total
  'Stockholm': 'SE11',
  'East-Central Sweden': 'SE12',
  'Småland and islands': 'SE21', 
  'South Sweden': 'SE22',
  'West Sweden': 'SE23',
  'North-Central Sweden': 'SE31',
  'Central Norrland': 'SE32',
  'Upper Norrland': 'SE33',
};

// Reverse mapping for display: NUTS code to Swedish name
const NUTS_TO_NAME = {
  'SE11': 'Stockholm',
  'SE12': 'Östra Mellansverige',
  'SE21': 'Småland med öarna',
  'SE22': 'Sydsverige',
  'SE23': 'Västsverige',
  'SE31': 'Norra Mellansverige',
  'SE32': 'Mellersta Norrland',
  'SE33': 'Övre Norrland',
};

const SwedenMap = ({ data, selectedRegion, onRegionClick }) => {
  const svgRef = useRef();
  const containerRef = useRef();
  const [geoData, setGeoData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load GeoJSON on mount - filter to Sweden only
  useEffect(() => {
    const loadGeoJSON = async () => {
      try {
        const response = await fetch(GEOJSON_URL);
        const geojson = await response.json();
        // Filter to Swedish regions only (SE*)
        const swedenFeatures = geojson.features.filter(f => 
          f.properties.id && f.properties.id.startsWith('SE')
        );
        setGeoData({
          type: 'FeatureCollection',
          features: swedenFeatures
        });
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

  // Aggregate income by region - map to NUTS codes
  const getRegionIncomeMap = () => {
    const regionIncome = {};
    if (Array.isArray(data) && data.length > 0) {
      data.forEach(item => {
        const region = item.region;
        const nutsCode = REGION_NAME_MAP[region];
        if (nutsCode && item.monthly_salary) {
          if (!regionIncome[nutsCode] || item.monthly_salary > regionIncome[nutsCode]) {
            regionIncome[nutsCode] = item.monthly_salary;
          }
        }
      });
    }
    return regionIncome;
  };

  const drawMap = () => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Improved dimensions - Sweden is tall and narrow
    const width = 320;
    const height = 600;

    svg.attr('width', width).attr('height', height);

    // Create projection for Sweden - adjusted for NUTS-2 regions
    const projection = d3.geoMercator()
      .center([17, 62.5])
      .scale(1100)
      .translate([width / 2, height / 2]);

    const pathGenerator = d3.geoPath().projection(projection);

    // Get income data for coloring
    const regionIncome = getRegionIncomeMap();
    const incomeValues = Object.values(regionIncome);
    const minIncome = incomeValues.length > 0 ? Math.min(...incomeValues) : 40000;
    const maxIncome = incomeValues.length > 0 ? Math.max(...incomeValues) : 60000;

    // Use Dark2-inspired sequential color scale (teal to orange)
    const colorScale = d3.scaleSequential()
      .domain([minIncome, maxIncome])
      .interpolator(t => d3.interpolateRgb(DARK2[0], DARK2[1])(t));

    // Draw regions
    svg.selectAll('path')
      .data(geoData.features)
      .enter()
      .append('path')
      .attr('d', pathGenerator)
      .attr('fill', d => {
        const nutsCode = d.properties.id;
        const income = regionIncome[nutsCode];
        return income ? colorScale(income) : '#e5e7eb';
      })
      .attr('stroke', '#1f2937')
      .attr('stroke-width', 1)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('stroke-width', 2.5)
          .attr('stroke', DARK2[2]);
        
        // Show tooltip
        const nutsCode = d.properties.id;
        const regionName = NUTS_TO_NAME[nutsCode] || d.properties.na;
        const income = regionIncome[nutsCode];
        
        // Remove any existing tooltip
        svg.select('#tooltip-bg').remove();
        svg.select('#tooltip').remove();
        
        const tooltipText = `${regionName}: ${income ? `${Math.round(income).toLocaleString()} SEK` : 'No data'}`;
        const tooltipX = width / 2;
        const tooltipY = 30;
        
        // Add tooltip background
        svg.append('rect')
          .attr('id', 'tooltip-bg')
          .attr('x', tooltipX - 80)
          .attr('y', tooltipY - 15)
          .attr('width', 160)
          .attr('height', 24)
          .attr('rx', 4)
          .attr('fill', 'rgba(31, 41, 55, 0.9)');
        
        svg.append('text')
          .attr('id', 'tooltip')
          .attr('x', tooltipX)
          .attr('y', tooltipY)
          .attr('text-anchor', 'middle')
          .style('font-size', '12px')
          .style('font-weight', '500')
          .style('fill', '#fff')
          .style('font-family', '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif')
          .text(tooltipText);
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('stroke-width', 1)
          .attr('stroke', '#1f2937');
        svg.select('#tooltip-bg').remove();
        svg.select('#tooltip').remove();
      })
      .on('click', function(event, d) {
        if (onRegionClick) {
          // Map back to English name for API
          const nutsCode = d.properties.id;
          const englishName = Object.keys(REGION_NAME_MAP).find(
            key => REGION_NAME_MAP[key] === nutsCode
          );
          onRegionClick(englishName || d.properties.na);
        }
      });

    // Add legend
    const legendWidth = 140;
    const legendHeight = 12;
    
    const legend = svg.append('g')
      .attr('transform', `translate(${width - legendWidth - 20}, ${height - 50})`);

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
      .attr('stop-color', DARK2[0]);

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', DARK2[1]);

    legend.append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .attr('rx', 2)
      .style('fill', 'url(#income-gradient)');

    legend.append('g')
      .attr('transform', `translate(0, ${legendHeight})`)
      .style('font-family', '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif')
      .style('font-size', '10px')
      .call(legendAxis);

    legend.append('text')
      .attr('x', legendWidth / 2)
      .attr('y', -8)
      .attr('text-anchor', 'middle')
      .style('font-size', '11px')
      .style('font-weight', '500')
      .style('fill', '#374151')
      .style('font-family', '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif')
      .text('Monthly Salary (SEK)');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress sx={{ color: DARK2[0] }} />
      </Box>
    );
  }

  return (
    <Box ref={containerRef} sx={{ height: '100%' }}>
      <Typography 
        variant="h6" 
        gutterBottom
        sx={{ 
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          fontWeight: 600,
          color: '#1f2937',
          fontSize: '1.1rem'
        }}
      >
        Average Income by Region
      </Typography>
      <Box display="flex" justifyContent="center">
        <svg ref={svgRef}></svg>
      </Box>
    </Box>
  );
};

export default SwedenMap;
