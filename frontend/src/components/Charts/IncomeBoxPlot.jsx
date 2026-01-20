import React from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Dark2 Brewer palette colors
const COLORS = {
  men: '#1b9e77',      // Teal for men
  women: '#d95f02',    // Orange for women
  range: '#e5e7eb',    // Light gray for guide lines
  grid: '#e5e7eb',
};

// Custom shape to draw the dot plot for a single occupation row
const DotPlotShape = (props) => {
  const { y, width, height, payload, xAxis } = props;
  
  // Calculate X coordinates for salary values using the xAxis scale
  const scale = xAxis.scale;
  
  const drawGenderPlot = (gender, yOffset) => {
    const median = gender === 'men' ? payload.menMedian : payload.womenMedian;
    const p25 = gender === 'men' ? payload.menP25 : payload.womenP25;
    const p75 = gender === 'men' ? payload.menP75 : payload.womenP75;
    const p10 = gender === 'men' ? payload.menP10 : payload.womenP10;
    const p90 = gender === 'men' ? payload.menP90 : payload.womenP90;
    
    const color = gender === 'men' ? COLORS.men : COLORS.women;
    
    if (!median) return null;

    const medX = scale(median);
    const p25X = p25 ? scale(p25) : null;
    const p75X = p75 ? scale(p75) : null;
    const p10X = p10 ? scale(p10) : null;
    const p90X = p90 ? scale(p90) : null;

    return (
      <g>
        {/* Connection line for IQR (P25-P75) */}
        {p25X && p75X && (
          <line 
            x1={p25X} y1={y + yOffset} 
            x2={p75X} y2={y + yOffset} 
            stroke={color} strokeWidth={1.5} opacity={0.4} 
          />
        )}
        
        {/* Full range line (P10-P90) - thinner */}
        {p10X && p90X && (
          <line 
            x1={p10X} y1={y + yOffset} 
            x2={p90X} y2={y + yOffset} 
            stroke={color} strokeWidth={1} opacity={0.2} strokeDasharray="2 2"
          />
        )}

        {/* P10 & P90 dots (Smallest) */}
        {p10X && <circle cx={p10X} cy={y + yOffset} r={2} fill={color} opacity={0.5} />}
        {p90X && <circle cx={p90X} cy={y + yOffset} r={2} fill={color} opacity={0.5} />}

        {/* P25 & P75 dots (Medium) */}
        {p25X && <circle cx={p25X} cy={y + yOffset} r={3.5} fill={color} opacity={0.7} />}
        {p75X && <circle cx={p75X} cy={y + yOffset} r={3.5} fill={color} opacity={0.7} />}

        {/* Median dot (Large) */}
        <circle cx={medX} cy={y + yOffset} r={6} fill={color} stroke="white" strokeWidth={1.5} />
      </g>
    );
  };

  // Draw Men and Women centered vertically in the band
  // Row height is 'height', center is y + height/2.
  // We can offset them slightly or put them on the same line if we prefer.
  // Putting them on the same line makes comparison easier, but might overlap.
  // User asked for "different colors", overlapping is acceptable or we can offset slightly.
  // Let's offset slightly (6px) to avoid total occlusion.
  const offset = height * 0.15; // small offset
  const centerY = height / 2;
  
  return (
    <g>
      {drawGenderPlot('men', centerY - offset)}
      {drawGenderPlot('women', centerY + offset)}
    </g>
  );
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

  // Transform and aggregate data
  const occupationMap = {};
  
  data.forEach(item => {
    const occupation = item.occupation || 'Unknown';
    // Use slightly longer limit for visualization
    const shortName = occupation.length > 30 
      ? occupation.substring(0, 30) + '...' 
      : occupation;
    
    if (!occupationMap[shortName]) {
      occupationMap[shortName] = { 
        occupation: shortName,
        fullName: occupation,
        menMedian: null, womenMedian: null,
        totalMedian: 0, count: 0 
      };
    }
    
    const entry = occupationMap[shortName];
    const gender = item.gender?.toLowerCase();
    
    if (gender === 'men') {
      entry.menMedian = item.median;
      entry.menP10 = item.p10;
      entry.menP25 = item.p25;
      entry.menP75 = item.p75;
      entry.menP90 = item.p90;
      if (item.median) {
        entry.totalMedian += item.median;
        entry.count++;
      }
    } else if (gender === 'women') {
      entry.womenMedian = item.median;
      entry.womenP10 = item.p10;
      entry.womenP25 = item.p25;
      entry.womenP75 = item.p75;
      entry.womenP90 = item.p90;
      if (item.median) {
        entry.totalMedian += item.median;
        entry.count++;
      }
    }
  });

  // Calculate average median for sorting (descending)
  Object.values(occupationMap).forEach(item => {
    if (item.count > 0) {
      item.avgMedian = item.totalMedian / item.count;
    } else {
      item.avgMedian = 0;
    }
  });

  const chartData = Object.values(occupationMap)
    .sort((a, b) => b.avgMedian - a.avgMedian);

  // Dynamic height calculation
  const chartHeight = Math.max(400, chartData.length * 60);

  const formatSalary = (value) => {
    if (!value) return '';
    return `${Math.round(value / 1000)}k`;
  };

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
          maxWidth: '350px'
        }}>
          <p style={{ 
            margin: '0 0 12px 0', 
            fontWeight: 600, 
            color: '#1f2937', 
            fontSize: '14px',
            borderBottom: '1px solid #e5e7eb',
            paddingBottom: '8px'
          }}>
            {data.fullName}
          </p>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {data.menMedian && (
              <div>
                <p style={{ margin: 0, color: COLORS.men, fontWeight: 600, fontSize: '13px', display: 'flex', alignItems: 'center' }}>
                  <span style={{width: 8, height: 8, borderRadius: '50%', backgroundColor: COLORS.men, marginRight: 6}}></span>
                  Men
                </p>
                <div style={{ marginTop: 4, fontSize: '11px', color: '#4b5563' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>P90:</span> <span>{data.menP90?.toLocaleString()}</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>P75:</span> <span>{data.menP75?.toLocaleString()}</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600, color: COLORS.men }}><span>Median:</span> <span>{data.menMedian?.toLocaleString()}</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>P25:</span> <span>{data.menP25?.toLocaleString()}</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>P10:</span> <span>{data.menP10?.toLocaleString()}</span></div>
                </div>
              </div>
            )}
            
            {data.womenMedian && (
              <div>
                <p style={{ margin: 0, color: COLORS.women, fontWeight: 600, fontSize: '13px', display: 'flex', alignItems: 'center' }}>
                  <span style={{width: 8, height: 8, borderRadius: '50%', backgroundColor: COLORS.women, marginRight: 6}}></span>
                  Women
                </p>
                <div style={{ marginTop: 4, fontSize: '11px', color: '#4b5563' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>P90:</span> <span>{data.womenP90?.toLocaleString()}</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>P75:</span> <span>{data.womenP75?.toLocaleString()}</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600, color: COLORS.women }}><span>Median:</span> <span>{data.womenMedian?.toLocaleString()}</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>P25:</span> <span>{data.womenP25?.toLocaleString()}</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>P10:</span> <span>{data.womenP10?.toLocaleString()}</span></div>
                </div>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  const RenderLegend = () => (
    <Box sx={{ display: 'flex', gap: 3, justifyContent: 'center', mt: 1, fontSize: '0.75rem', color: '#666' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: COLORS.men }} />
        <Typography variant="caption" sx={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI"' }}>Men</Typography>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: COLORS.women }} />
        <Typography variant="caption" sx={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI"' }}>Women</Typography>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 1 }}>
         <svg width="80" height="14" style={{ overflow: 'visible' }}>
            <circle cx="6" cy="7" r="2" fill="#999" opacity="0.5" />
            <circle cx="18" cy="7" r="3.5" fill="#999" opacity="0.7" />
            <circle cx="32" cy="7" r="6" fill="#666" stroke="none" />
            <text x="44" y="11" fontSize="10" fill="#666" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI"' }}>P10 • P25 • Median</text>
         </svg>
      </Box>
    </Box>
  );

  return (
    <Box height="100%" display="flex" flexDirection="column">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
        <Typography 
          variant="h6" 
          sx={{ 
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            fontWeight: 600,
            color: '#1f2937',
            fontSize: '1.1rem'
          }}
        >
          Salary Distribution (P10-P90)
        </Typography>
      </Box>
      
      <Box flexGrow={1} minHeight={0} overflow="auto">
        <Box height={Math.max(400, chartHeight)}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart 
              data={chartData} 
              layout="vertical"
              margin={{ top: 10, right: 30, left: 20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={true} stroke="#f0f0f0" />
              <XAxis 
                type="number" 
                tickFormatter={formatSalary}
                domain={['auto', 'auto']}
                tick={{ fill: '#6b7280', fontSize: 11, fontFamily: '-apple-system' }}
                axisLine={{ stroke: '#d1d5db' }}
              />
              <YAxis 
                dataKey="occupation" 
                type="category" 
                width={180}
                tick={{ fill: '#374151', fontSize: 11, width: 170, fontFamily: '-apple-system' }}
                axisLine={{ stroke: '#d1d5db' }}
                interval={0}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
              
              {/* Invisible bar to act as the canvas for the Custom DotPlot shape */}
              <Bar 
                dataKey="avgMedian" 
                shape={<DotPlotShape />} 
                isAnimationActive={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </Box>
      </Box>
      <RenderLegend />
    </Box>
  );
};

export default IncomeBoxPlot;
