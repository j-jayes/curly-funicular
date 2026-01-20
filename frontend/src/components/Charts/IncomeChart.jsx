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

  // Aggregate data by occupation and gender
  const aggregated = {};
  
  data.forEach(item => {
    const occupation = item.occupation || 'Unknown';
    const gender = item.gender || 'unknown';
    const salary = item.monthly_salary || 0;
    
    if (!aggregated[occupation]) {
      aggregated[occupation] = { occupation, men: 0, women: 0, menCount: 0, womenCount: 0 };
    }
    
    if (gender === 'men') {
      aggregated[occupation].men += salary;
      aggregated[occupation].menCount += 1;
    } else if (gender === 'women') {
      aggregated[occupation].women += salary;
      aggregated[occupation].womenCount += 1;
    }
  });

  // Calculate averages
  const chartData = Object.values(aggregated).map(item => ({
    occupation: item.occupation.length > 25 
      ? item.occupation.substring(0, 25) + '...' 
      : item.occupation,
    men: item.menCount > 0 ? Math.round(item.men / item.menCount) : 0,
    women: item.womenCount > 0 ? Math.round(item.women / item.womenCount) : 0,
  }));

  const formatSalary = (value) => `${Math.round(value / 1000)}k SEK`;

  return (
    <Box height="100%">
      <Typography variant="h6" gutterBottom>
        Average Monthly Salary by Occupation and Gender
      </Typography>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" tickFormatter={formatSalary} />
          <YAxis dataKey="occupation" type="category" width={150} />
          <Tooltip formatter={(value) => `${value.toLocaleString()} SEK`} />
          <Legend />
          <Bar dataKey="men" name="Men" fill="#1976d2" />
          <Bar dataKey="women" name="Women" fill="#dc004e" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default IncomeChart;
