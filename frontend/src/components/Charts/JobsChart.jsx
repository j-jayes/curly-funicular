import React from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';

const COLORS = ['#1976d2', '#dc004e', '#2e7d32', '#ed6c02', '#9c27b0'];

const JobsChart = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary">No job data available</Typography>
      </Box>
    );
  }

  // Aggregate jobs by region
  const regionCounts = {};
  data.forEach(job => {
    const region = job.region || 'Unknown';
    if (!regionCounts[region]) {
      regionCounts[region] = { count: 0, vacancies: 0 };
    }
    regionCounts[region].count += 1;
    regionCounts[region].vacancies += (job.number_of_vacancies || 1);
  });

  // Sort by vacancy count and take top 10
  const chartData = Object.entries(regionCounts)
    .map(([region, stats]) => ({
      region: region.replace(' län', ''),  // Shorten region names
      ads: stats.count,
      vacancies: stats.vacancies
    }))
    .sort((a, b) => b.vacancies - a.vacancies)
    .slice(0, 10);

  return (
    <Box height="100%">
      <Typography variant="h6" gutterBottom>
        Job Ads by Region (Top 10)
      </Typography>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="region" 
            angle={-45} 
            textAnchor="end" 
            height={80}
            interval={0}
            fontSize={11}
          />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="ads" name="Job Ads" fill="#1976d2" />
          <Bar dataKey="vacancies" name="Vacancies" fill="#dc004e" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default JobsChart;
