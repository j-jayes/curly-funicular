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
  const ageGroups = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+'];
  const genders = [
    { value: 'M', label: 'Male' },
    { value: 'F', label: 'Female' },
    { value: 'all', label: 'All' }
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
                <MenuItem key={region.code} value={region.code}>
                  {region.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Age Group</InputLabel>
            <Select
              value={filters.ageGroup}
              label="Age Group"
              onChange={handleChange('ageGroup')}
            >
              <MenuItem value="">All Ages</MenuItem>
              {ageGroups.map((age) => (
                <MenuItem key={age} value={age}>
                  {age}
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
