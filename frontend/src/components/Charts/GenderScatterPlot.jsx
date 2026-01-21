import React from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ZAxis
} from 'recharts';

// Dark2 Brewer palette colors
const COLORS = {
  primary: '#7570b3',  // Purple for scatter points
  reference: '#e5e7eb', // Light gray for reference line
  menHigher: '#1b9e77', // Teal when men earn more
  womenHigher: '#d95f02', // Orange when women earn more
};

const GenderScatterPlot = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress sx={{ color: COLORS.primary }} />
      </Box>
    );
  }

  if (!Array.isArray(data)) {
    console.warn('GenderScatterPlot received non-array data:', data);
    return null;
  }

  if (data.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary" sx={{ fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif' }}>
          No dispersion data available for selected filters
        </Typography>
      </Box>
    );
  }

  // Transform data: pivot to have men median (x) and women median (y) per occupation
  const occupationMap = {};
  
  data.forEach(item => {
    const occupation = item.occupation || 'Unknown';
    const occupationCode = item.occupation_code || '';
    const year = item.year;
    
    if (!occupationMap[occupation]) {
      occupationMap[occupation] = { 
        occupation,
        occupationCode,
        year,
        menMedian: null, 
        womenMedian: null,
        menMean: null, womenMean: null,
        menP10: null, menP25: null, menP75: null, menP90: null,
        womenP10: null, womenP25: null, womenP75: null, womenP90: null,
      };
    }
    
    const gender = item.gender?.toLowerCase();
    
    if (gender === 'men') {
      occupationMap[occupation].menMedian = item.median;
      occupationMap[occupation].menMean = item.mean;
      occupationMap[occupation].menP10 = item.p10;
      occupationMap[occupation].menP25 = item.p25;
      occupationMap[occupation].menP75 = item.p75;
      occupationMap[occupation].menP90 = item.p90;
    } else if (gender === 'women') {
      occupationMap[occupation].womenMedian = item.median;
      occupationMap[occupation].womenMean = item.mean;
      occupationMap[occupation].womenP10 = item.p10;
      occupationMap[occupation].womenP25 = item.p25;
      occupationMap[occupation].womenP75 = item.p75;
      occupationMap[occupation].womenP90 = item.p90;
    }
  });

  // Filter to only occupations with both men and women data
  const scatterData = Object.values(occupationMap)
    .filter(item => item.menMedian && item.womenMedian)
    .map(item => ({
      ...item,
      x: item.menMedian,
      y: item.womenMedian,
      genderGap: ((item.womenMedian - item.menMedian) / item.menMedian * 100).toFixed(1),
    }));

  if (scatterData.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary" sx={{ fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif' }}>
          No occupation data with both male and female median salaries available
        </Typography>
      </Box>
    );
  }

  // Calculate domain for axes (add padding)
  const allValues = [...scatterData.map(d => d.x), ...scatterData.map(d => d.y)];
  const minVal = Math.min(...allValues) * 0.9;
  const maxVal = Math.max(...allValues) * 1.1;

  const formatSalary = (value) => `${Math.round(value / 1000)}k`;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0]?.payload;
      if (!data) return null;
      
      const genderGapNum = parseFloat(data.genderGap);
      const genderGapColor = genderGapNum >= 0 ? COLORS.womenHigher : COLORS.menHigher;
      const genderGapText = genderGapNum >= 0 
        ? `Women earn ${Math.abs(genderGapNum)}% more`
        : `Men earn ${Math.abs(genderGapNum)}% more`;
      
      const formatVal = (val) => val ? val.toLocaleString() : '—';
      
      return (
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.98)',
          padding: '16px 20px',
          border: 'none',
          borderRadius: '12px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          maxWidth: '380px'
        }}>
          <p style={{ 
            margin: '0 0 4px 0', 
            fontWeight: 600, 
            color: '#1f2937', 
            fontSize: '13px',
          }}>
            {data.occupation}
          </p>
          <p style={{ margin: '0 0 12px 0', color: '#6b7280', fontSize: '11px' }}>
            {data.occupationCode && `SSYK: ${data.occupationCode} • `}Year: {data.year || 'Latest'}
          </p>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{ borderRight: '1px solid #e5e7eb', paddingRight: '12px' }}>
              <p style={{ margin: 0, color: COLORS.menHigher, fontWeight: 600, fontSize: '12px' }}>
                Men
              </p>
              <p style={{ margin: '6px 0 2px 0', fontSize: '16px', fontWeight: 700, color: '#1f2937' }}>
                {formatVal(data.menMedian)} SEK
              </p>
              <p style={{ margin: 0, fontSize: '10px', color: '#9ca3af' }}>median</p>
              
              <div style={{ marginTop: '10px', fontSize: '11px', color: '#4b5563' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span>Mean:</span>
                  <span style={{ fontWeight: 500 }}>{formatVal(data.menMean)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span>P10:</span>
                  <span style={{ fontWeight: 500 }}>{formatVal(data.menP10)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span>P25:</span>
                  <span style={{ fontWeight: 500 }}>{formatVal(data.menP25)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span>P75:</span>
                  <span style={{ fontWeight: 500 }}>{formatVal(data.menP75)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>P90:</span>
                  <span style={{ fontWeight: 500 }}>{formatVal(data.menP90)}</span>
                </div>
              </div>
            </div>
            <div>
              <p style={{ margin: 0, color: COLORS.womenHigher, fontWeight: 600, fontSize: '12px' }}>
                Women
              </p>
              <p style={{ margin: '6px 0 2px 0', fontSize: '16px', fontWeight: 700, color: '#1f2937' }}>
                {formatVal(data.womenMedian)} SEK
              </p>
              <p style={{ margin: 0, fontSize: '10px', color: '#9ca3af' }}>median</p>
              
              <div style={{ marginTop: '10px', fontSize: '11px', color: '#4b5563' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span>Mean:</span>
                  <span style={{ fontWeight: 500 }}>{formatVal(data.womenMean)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span>P10:</span>
                  <span style={{ fontWeight: 500 }}>{formatVal(data.womenP10)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span>P25:</span>
                  <span style={{ fontWeight: 500 }}>{formatVal(data.womenP25)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span>P75:</span>
                  <span style={{ fontWeight: 500 }}>{formatVal(data.womenP75)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>P90:</span>
                  <span style={{ fontWeight: 500 }}>{formatVal(data.womenP90)}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div style={{ 
            marginTop: '12px', 
            paddingTop: '12px', 
            borderTop: '1px solid #e5e7eb',
            textAlign: 'center'
          }}>
            <span style={{ 
              color: genderGapColor, 
              fontWeight: 600, 
              fontSize: '12px' 
            }}>
              {genderGapText}
            </span>
          </div>
        </div>
      );
    }
    return null;
  };

  // Custom dot component to color by gender gap
  const CustomDot = (props) => {
    const { cx, cy, payload } = props;
    const genderGap = parseFloat(payload.genderGap);
    const color = genderGap >= 0 ? COLORS.womenHigher : COLORS.menHigher;
    
    return (
      <circle 
        cx={cx} 
        cy={cy} 
        r={8} 
        fill={color}
        fillOpacity={0.7}
        stroke={color}
        strokeWidth={2}
        style={{ cursor: 'pointer' }}
      />
    );
  };

  return (
    <Box height="100%" display="flex" flexDirection="column">
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
        <Box>
          <Typography 
            variant="h6" 
            sx={{ 
              fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
              fontWeight: 600,
              color: '#1f2937',
              fontSize: '1.1rem'
            }}
          >
            Gender Salary Comparison by Occupation
          </Typography>
          <Typography 
            variant="caption" 
            sx={{ 
              color: '#6b7280', 
              display: 'block',
              fontSize: '0.7rem'
            }}
          >
            National data • Hover for details • Points above line = women earn more
          </Typography>
        </Box>
      </Box>
      
      <Box flexGrow={1} minHeight={0}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              type="number" 
              dataKey="x" 
              name="Men Median"
              domain={[minVal, maxVal]}
              tickFormatter={formatSalary}
              tick={{ fill: '#6b7280', fontSize: 11, fontFamily: '-apple-system' }}
              axisLine={{ stroke: '#d1d5db' }}
              label={{ 
                value: 'Men Median Salary (SEK)', 
                position: 'bottom', 
                offset: 40,
                style: { 
                  fill: COLORS.menHigher, 
                  fontSize: 12, 
                  fontWeight: 500,
                  fontFamily: '-apple-system' 
                }
              }}
            />
            <YAxis 
              type="number" 
              dataKey="y" 
              name="Women Median"
              domain={[minVal, maxVal]}
              tickFormatter={formatSalary}
              tick={{ fill: '#6b7280', fontSize: 11, fontFamily: '-apple-system' }}
              axisLine={{ stroke: '#d1d5db' }}
              label={{ 
                value: 'Women Median Salary (SEK)', 
                angle: -90, 
                position: 'insideLeft',
                offset: 10,
                style: { 
                  fill: COLORS.womenHigher, 
                  fontSize: 12, 
                  fontWeight: 500,
                  fontFamily: '-apple-system',
                  textAnchor: 'middle'
                }
              }}
            />
            <ZAxis range={[100, 100]} />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
            
            {/* Parity line (x=y) */}
            <ReferenceLine 
              segment={[{ x: minVal, y: minVal }, { x: maxVal, y: maxVal }]}
              stroke="#9ca3af"
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{ 
                value: 'Equal pay', 
                position: 'end',
                style: { fill: '#9ca3af', fontSize: 10, fontFamily: '-apple-system' }
              }}
            />
            
            <Scatter 
              name="Occupations" 
              data={scatterData} 
              shape={<CustomDot />}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </Box>
      
      {/* Legend */}
      <Box sx={{ display: 'flex', gap: 3, justifyContent: 'center', mt: 1, fontSize: '0.75rem' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: COLORS.menHigher }} />
          <Typography variant="caption" sx={{ fontFamily: '-apple-system', color: '#6b7280' }}>
            Men earn more
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: COLORS.womenHigher }} />
          <Typography variant="caption" sx={{ fontFamily: '-apple-system', color: '#6b7280' }}>
            Women earn more
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Box sx={{ width: 20, height: 0, borderTop: '2px dashed #9ca3af' }} />
          <Typography variant="caption" sx={{ fontFamily: '-apple-system', color: '#6b7280' }}>
            Parity line
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default GenderScatterPlot;
