import React from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

// Dark2 Brewer palette colors
const COLORS = {
  primary: '#7570b3',  // Purple for employers
  secondary: '#e7298a', // Pink for vacancies
  gradient: ['#7570b3', '#a855f7', '#c084fc'], // Purple gradient
};

const TopEmployersChart = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress sx={{ color: COLORS.primary }} />
      </Box>
    );
  }

  if (!Array.isArray(data)) {
    console.warn('TopEmployersChart received non-array data:', data);
    return null;
  }

  if (data.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary" sx={{ fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif' }}>
          No employer data available for selected filters
        </Typography>
      </Box>
    );
  }

  // Prepare chart data - shorten employer names
  const chartData = data.slice(0, 12).map((employer, index) => ({
    ...employer,
    shortName: employer.employer.length > 22 
      ? employer.employer.substring(0, 22) + '...' 
      : employer.employer,
    // Calculate color intensity based on rank
    colorIntensity: 1 - (index / 12) * 0.4,
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0]?.payload;
      if (!data) return null;
      
      return (
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.98)',
          padding: '16px 20px',
          border: 'none',
          borderRadius: '12px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          maxWidth: '280px'
        }}>
          <p style={{ 
            margin: '0 0 8px 0', 
            fontWeight: 600, 
            color: '#1f2937', 
            fontSize: '13px',
          }}>
            {data.employer}
          </p>
          
          <div style={{ fontSize: '12px', color: '#4b5563' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span>Job Ads:</span>
              <span style={{ fontWeight: 600, color: COLORS.primary }}>{data.ad_count.toLocaleString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span>Total Vacancies:</span>
              <span style={{ fontWeight: 600, color: COLORS.secondary }}>{data.total_vacancies.toLocaleString()}</span>
            </div>
            {data.primary_region && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Primary Region:</span>
                <span style={{ fontWeight: 500 }}>{data.primary_region}</span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <Box height="100%" display="flex" flexDirection="column">
      <Box mb={1}>
        <Typography 
          variant="h6" 
          sx={{ 
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            fontWeight: 600,
            color: '#1f2937',
            fontSize: '1.1rem'
          }}
        >
          Top Employers by Job Ads
        </Typography>
        <Typography 
          variant="caption" 
          sx={{ 
            color: '#6b7280', 
            display: 'block',
            fontSize: '0.7rem'
          }}
        >
          Ranked by number of job advertisements posted
        </Typography>
      </Box>
      
      <Box flexGrow={1} minHeight={0}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart 
            data={chartData} 
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={true} vertical={false} />
            <XAxis 
              type="number" 
              tick={{ fill: '#6b7280', fontSize: 10, fontFamily: '-apple-system' }}
              axisLine={{ stroke: '#d1d5db' }}
            />
            <YAxis 
              dataKey="shortName" 
              type="category" 
              width={140}
              tick={{ fill: '#374151', fontSize: 10, fontFamily: '-apple-system' }}
              axisLine={{ stroke: '#d1d5db' }}
              interval={0}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
            <Bar 
              dataKey="ad_count" 
              name="Job Ads" 
              radius={[0, 4, 4, 0]}
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={COLORS.primary}
                  fillOpacity={entry.colorIntensity}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};

export default TopEmployersChart;
