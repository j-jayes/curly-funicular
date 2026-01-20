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

// Dark2 Brewer palette colors
const COLORS = {
  men: '#1b9e77',      // Teal for men
  women: '#d95f02',    // Orange for women
  ads: '#7570b3',      // Purple for job ads  
  vacancies: '#e7298a' // Pink for vacancies
};

const IncomeChart = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress sx={{ color: COLORS.men }} />
      </Box>
    );
  }

  // Aggregate data by occupation and gender
  const aggregated = {};
  
  if (!Array.isArray(data)) {
    console.warn('IncomeChart received non-array data:', data);
    return null;
  }
  
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

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          padding: '12px 16px',
          border: 'none',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }}>
          <p style={{ margin: 0, fontWeight: 600, color: '#1f2937', fontSize: '13px' }}>{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ 
              margin: '4px 0 0 0', 
              color: entry.color,
              fontSize: '12px',
              fontWeight: 500
            }}>
              {entry.name}: {entry.value.toLocaleString()} SEK
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <Box height="100%">
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
        Average Monthly Salary by Occupation and Gender
      </Typography>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            type="number" 
            tickFormatter={formatSalary}
            tick={{ fill: '#6b7280', fontSize: 11 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <YAxis 
            dataKey="occupation" 
            type="category" 
            width={150}
            tick={{ fill: '#374151', fontSize: 11 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ 
              fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
              fontSize: '12px'
            }}
          />
          <Bar dataKey="men" name="Men" fill={COLORS.men} radius={[0, 4, 4, 0]} />
          <Bar dataKey="women" name="Women" fill={COLORS.women} radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default IncomeChart;
