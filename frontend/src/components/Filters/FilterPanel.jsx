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

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Filters
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Occupation</InputLabel>
            <Select
              value={filters.occupation}
              label="Occupation"
              onChange={handleChange('occupation')}
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
          <FormControl fullWidth>
            <InputLabel>Region</InputLabel>
            <Select
              value={filters.region}
              label="Region"
              onChange={handleChange('region')}
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
          <FormControl fullWidth>
            <InputLabel>Year</InputLabel>
            <Select
              value={filters.year || ''}
              label="Year"
              onChange={handleChange('year')}
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
          <FormControl fullWidth>
            <InputLabel>Gender</InputLabel>
            <Select
              value={filters.gender}
              label="Gender"
              onChange={handleChange('gender')}
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
