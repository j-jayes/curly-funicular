import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';

const FilterPanel = ({ filters, occupations, regions, onFilterChange }) => {
  const genders = [
    { value: 'men', label: 'Men' },
    { value: 'women', label: 'Women' },
  ];

  const years = [
    { value: '2023', label: '2023' },
    { value: '2024', label: '2024' },
  ];

  const handleChange = (field) => (event) => {
    onFilterChange({ [field]: event.target.value });
  };

  const selectStyles = {
    borderRadius: '8px',
    '& .MuiOutlinedInput-notchedOutline': {
      borderColor: '#e5e7eb',
    },
    '&:hover .MuiOutlinedInput-notchedOutline': {
      borderColor: '#1b9e77',
    },
    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
      borderColor: '#1b9e77',
    },
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <FilterListIcon sx={{ color: '#1b9e77', fontSize: 20 }} />
        <Typography 
          variant="h6" 
          sx={{ 
            fontWeight: 600,
            fontSize: '1rem',
            color: '#374151',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
          }}
        >
          Filter Data
        </Typography>
      </Box>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel sx={{ fontSize: '0.875rem' }}>Occupation</InputLabel>
            <Select
              value={filters.occupation}
              label="Occupation"
              onChange={handleChange('occupation')}
              sx={selectStyles}
            >
              <MenuItem value="">All Occupations</MenuItem>
              {occupations.map((occ) => (
                <MenuItem key={occ.code} value={occ.code}>
                  {occ.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel sx={{ fontSize: '0.875rem' }}>Region</InputLabel>
            <Select
              value={filters.region}
              label="Region"
              onChange={handleChange('region')}
              sx={selectStyles}
            >
              <MenuItem value="">All Regions</MenuItem>
              {regions.map((region) => (
                <MenuItem key={region.code} value={region.name}>
                  {region.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel sx={{ fontSize: '0.875rem' }}>Year</InputLabel>
            <Select
              value={filters.year || ''}
              label="Year"
              onChange={handleChange('year')}
              sx={selectStyles}
            >
              <MenuItem value="">All Years</MenuItem>
              {years.map((year) => (
                <MenuItem key={year.value} value={year.value}>
                  {year.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel sx={{ fontSize: '0.875rem' }}>Gender</InputLabel>
            <Select
              value={filters.gender}
              label="Gender"
              onChange={handleChange('gender')}
              sx={selectStyles}
            >
              <MenuItem value="">All Genders</MenuItem>
              {genders.map((gender) => (
                <MenuItem key={gender.value} value={gender.value}>
                  {gender.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FilterPanel;
