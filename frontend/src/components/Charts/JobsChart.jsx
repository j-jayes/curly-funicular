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

// Dark2 Brewer palette colors
const COLORS = {
  men: '#1b9e77',      // Teal for men
  women: '#d95f02',    // Orange for women
  ads: '#7570b3',      // Purple for job ads  
  vacancies: '#e7298a' // Pink for vacancies
};

const JobsChart = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress sx={{ color: COLORS.ads }} />
      </Box>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary" sx={{ fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif' }}>
          No job data available
        </Typography>
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
              {entry.name}: {entry.value.toLocaleString()}
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
        Job Ads by Region (Top 10)
      </Typography>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="region" 
            angle={-45} 
            textAnchor="end" 
            height={80}
            interval={0}
            tick={{ fill: '#374151', fontSize: 10 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <YAxis 
            tick={{ fill: '#6b7280', fontSize: 11 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ 
              fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
              fontSize: '12px'
            }}
          />
          <Bar dataKey="ads" name="Job Ads" fill={COLORS.ads} radius={[4, 4, 0, 0]} />
          <Bar dataKey="vacancies" name="Vacancies" fill={COLORS.vacancies} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default JobsChart;
