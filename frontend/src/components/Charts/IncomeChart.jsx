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
  ResponsiveContainer
} from 'recharts';

const IncomeChart = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  // Transform data for chart
  const chartData = data.map(item => ({
    occupation: item.occupation || 'Unknown',
    median: item.median_income || 0,
    p10: item.income_percentile_10 || 0,
    p90: item.income_percentile_90 || 0
  }));

  return (
    <Box height="100%">
      <Typography variant="h6" gutterBottom>
        Income Spread by Occupation
      </Typography>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="occupation" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="p10" name="10th Percentile" fill="#90caf9" />
          <Bar dataKey="median" name="Median" fill="#1976d2" />
          <Bar dataKey="p90" name="90th Percentile" fill="#0d47a1" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default IncomeChart;
