import React from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const JobsChart = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  // Aggregate jobs by region
  const regionCounts = {};
  data.forEach(job => {
    const region = job.region || 'Unknown';
    regionCounts[region] = (regionCounts[region] || 0) + (job.number_of_vacancies || 1);
  });

  const chartData = Object.entries(regionCounts).map(([region, count]) => ({
    region,
    jobs: count
  }));

  return (
    <Box height="100%">
      <Typography variant="h6" gutterBottom>
        Number of Jobs by Region
      </Typography>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="region" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="jobs" 
            name="Number of Jobs" 
            stroke="#dc004e" 
            strokeWidth={2}
            activeDot={{ r: 8 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default JobsChart;
