import React from 'react';
import { Box, Typography, CircularProgress, Chip, Tooltip } from '@mui/material';

// Dark2 Brewer palette colors
const COLORS = {
  competency: '#1b9e77',  // Teal for technical skills
  trait: '#d95f02',       // Orange for soft skills  
  occupation: '#7570b3',  // Purple for occupations
};

const SkillsChart = ({ data, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress sx={{ color: COLORS.competency }} />
      </Box>
    );
  }

  if (!Array.isArray(data) || data.length === 0) {
    return (
      <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary" sx={{ fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif' }}>
          No skills data available
        </Typography>
        <Typography variant="caption" color="textSecondary" sx={{ mt: 1, fontFamily: '-apple-system', fontSize: '0.7rem' }}>
          Skills extraction requires running the data pipeline with enrichments enabled
        </Typography>
      </Box>
    );
  }

  // Group skills by type
  const competencies = data.filter(s => s.skill_type === 'competency');
  const traits = data.filter(s => s.skill_type === 'trait');
  const occupations = data.filter(s => s.skill_type === 'occupation');

  // Calculate max count for sizing
  const maxCount = Math.max(...data.map(s => s.occurrence_count || 1));

  const SkillChip = ({ skill, color }) => {
    const size = Math.max(0.75, Math.min(1.2, 0.75 + (skill.occurrence_count / maxCount) * 0.45));
    
    return (
      <Tooltip 
        title={`${skill.occurrence_count} job ads (${(skill.avg_probability * 100).toFixed(0)}% confidence)`}
        arrow
      >
        <Chip
          label={skill.skill}
          size="small"
          sx={{
            m: 0.5,
            bgcolor: `${color}15`,
            color: color,
            fontWeight: 500,
            fontSize: `${size * 0.75}rem`,
            fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif',
            borderColor: `${color}40`,
            border: '1px solid',
            '&:hover': {
              bgcolor: `${color}25`,
            }
          }}
        />
      </Tooltip>
    );
  };

  const SkillSection = ({ title, skills, color }) => {
    if (skills.length === 0) return null;
    
    return (
      <Box sx={{ mb: 2 }}>
        <Typography 
          variant="subtitle2" 
          sx={{ 
            fontFamily: '-apple-system', 
            fontWeight: 600, 
            color: color,
            fontSize: '0.8rem',
            mb: 1,
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
        >
          <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: color }} />
          {title}
          <Typography component="span" sx={{ color: '#9ca3af', fontWeight: 400, fontSize: '0.7rem' }}>
            ({skills.length})
          </Typography>
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0 }}>
          {skills.slice(0, 15).map((skill, index) => (
            <SkillChip key={index} skill={skill} color={color} />
          ))}
        </Box>
      </Box>
    );
  };

  return (
    <Box height="100%" display="flex" flexDirection="column">
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
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
            Most Requested Skills
          </Typography>
          <Typography 
            variant="caption" 
            sx={{ 
              color: '#6b7280', 
              display: 'block',
              fontSize: '0.7rem'
            }}
          >
            Extracted from job descriptions • Size reflects frequency
          </Typography>
        </Box>
      </Box>
      
      <Box sx={{ overflow: 'auto', flexGrow: 1 }}>
        <SkillSection 
          title="Technical Competencies" 
          skills={competencies} 
          color={COLORS.competency} 
        />
        <SkillSection 
          title="Soft Skills & Traits" 
          skills={traits} 
          color={COLORS.trait} 
        />
        <SkillSection 
          title="Related Occupations" 
          skills={occupations} 
          color={COLORS.occupation} 
        />
      </Box>
    </Box>
  );
};

export default SkillsChart;
