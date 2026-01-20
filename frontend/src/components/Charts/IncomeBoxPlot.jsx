import React from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Line,
  ReferenceLine,
  ErrorBar
} from 'recharts';

// Dark2 Brewer palette colors
const COLORS = {
  men: '#1b9e77',      // Teal for men
  women: '#d95f02',    // Orange for women
  range: '#e5e7eb',    // Light gray for IQR range
  median: '#374151',   // Dark gray for median line
};

const IncomeBoxPlot = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress sx={{ color: COLORS.men }} />
      </Box>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary" sx={{ fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif' }}>
          No dispersion data available
        </Typography>
      </Box>
    );
  }

  // Transform data for visualization
  // Group by occupation and create separate bars for men/women
  const occupationData = {};
  
  data.forEach(item => {
    const occupation = item.occupation || 'Unknown';
    const shortName = occupation.length > 20 
      ? occupation.substring(0, 20) + '...' 
      : occupation;
    
    if (!occupationData[shortName]) {
      occupationData[shortName] = { 
        occupation: shortName,
        fullName: occupation,
      };
    }
    
    const gender = item.gender?.toLowerCase() || 'unknown';
    if (gender === 'men') {
      occupationData[shortName].menMedian = item.median;
      occupationData[shortName].menP25 = item.p25;
      occupationData[shortName].menP75 = item.p75;
      occupationData[shortName].menP10 = item.p10;
      occupationData[shortName].menP90 = item.p90;
      occupationData[shortName].menMean = item.mean;
    } else if (gender === 'women') {
      occupationData[shortName].womenMedian = item.median;
      occupationData[shortName].womenP25 = item.p25;
      occupationData[shortName].womenP75 = item.p75;
      occupationData[shortName].womenP10 = item.p10;
      occupationData[shortName].womenP90 = item.p90;
      occupationData[shortName].womenMean = item.mean;
    }
  });

  const chartData = Object.values(occupationData);

  const formatSalary = (value) => {
    if (!value) return '';
    return `${Math.round(value / 1000)}k`;
  };

  const CustomTooltip = ({ active, payload, label }) => {
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
          maxWidth: '300px'
        }}>
          <p style={{ 
            margin: '0 0 12px 0', 
            fontWeight: 600, 
            color: '#1f2937', 
            fontSize: '14px',
            borderBottom: '1px solid #e5e7eb',
            paddingBottom: '8px'
          }}>
            {data.fullName || label}
          </p>
          
          {data.menMedian && (
            <div style={{ marginBottom: '8px' }}>
              <p style={{ margin: 0, color: COLORS.men, fontWeight: 600, fontSize: '12px' }}>
                ♂ Men
              </p>
              <p style={{ margin: '2px 0', color: '#6b7280', fontSize: '11px' }}>
                P10-P90: {formatSalary(data.menP10)} - {formatSalary(data.menP90)} SEK
              </p>
              <p style={{ margin: '2px 0', color: '#6b7280', fontSize: '11px' }}>
                IQR (P25-P75): {formatSalary(data.menP25)} - {formatSalary(data.menP75)} SEK
              </p>
              <p style={{ margin: '2px 0', color: COLORS.men, fontWeight: 500, fontSize: '12px' }}>
                Median: {data.menMedian?.toLocaleString()} SEK
              </p>
            </div>
          )}
          
          {data.womenMedian && (
            <div>
              <p style={{ margin: 0, color: COLORS.women, fontWeight: 600, fontSize: '12px' }}>
                ♀ Women
              </p>
              <p style={{ margin: '2px 0', color: '#6b7280', fontSize: '11px' }}>
                P10-P90: {formatSalary(data.womenP10)} - {formatSalary(data.womenP90)} SEK
              </p>
              <p style={{ margin: '2px 0', color: '#6b7280', fontSize: '11px' }}>
                IQR (P25-P75): {formatSalary(data.womenP25)} - {formatSalary(data.womenP75)} SEK
              </p>
              <p style={{ margin: '2px 0', color: COLORS.women, fontWeight: 500, fontSize: '12px' }}>
                Median: {data.womenMedian?.toLocaleString()} SEK
              </p>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  // For box plot visualization, we'll use the median as the main value
  // and show the IQR as a bar range
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
        Salary Distribution by Occupation (P25-P75 Range)
      </Typography>
      <ResponsiveContainer width="100%" height="85%">
        <ComposedChart data={chartData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            type="number" 
            tickFormatter={formatSalary}
            domain={['dataMin - 5000', 'dataMax + 5000']}
            tick={{ fill: '#6b7280', fontSize: 11 }}
            axisLine={{ stroke: '#d1d5db' }}
            label={{ 
              value: 'Monthly Salary (SEK)', 
              position: 'bottom', 
              offset: -5,
              style: { fontSize: 11, fill: '#6b7280' }
            }}
          />
          <YAxis 
            dataKey="occupation" 
            type="category" 
            width={140}
            tick={{ fill: '#374151', fontSize: 10 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ 
              fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
              fontSize: '12px'
            }}
          />
          
          {/* Men's median as a bar */}
          <Bar 
            dataKey="menMedian" 
            name="Men (Median)" 
            fill={COLORS.men} 
            radius={[0, 4, 4, 0]}
            barSize={12}
          />
          
          {/* Women's median as a bar */}
          <Bar 
            dataKey="womenMedian" 
            name="Women (Median)" 
            fill={COLORS.women} 
            radius={[0, 4, 4, 0]}
            barSize={12}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default IncomeBoxPlot;
