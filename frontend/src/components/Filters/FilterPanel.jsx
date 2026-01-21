import React from 'react';
import { 
  Box, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Grid,
  Typography,
  Chip,
  Checkbox,
  ListItemText,
  OutlinedInput
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';

// SSYK Level 1 Categories (approximate for filtering)
const AREA_OF_WORK = [
  { code: '0', label: 'Armed Forces' },
  { code: '1', label: 'Managers' },
  { code: '2', label: 'Professionals' },
  { code: '3', label: 'Technicians' },
  { code: '4', label: 'Clerical Support' },
  { code: '5', label: 'Service & Sales' },
  { code: '6', label: 'Agriculture & Fishery' },
  { code: '7', label: 'Craft & Trades' },
  { code: '8', label: 'Plant & Machine Operators' },
  { code: '9', label: 'Elementary Occupations' },
];

const FilterPanel = ({ filters, occupations, regions, onFilterChange }) => {
  const [areaFilter, setAreaFilter] = React.useState('');
  
  // Handle multi-select occupation change
  const handleOccupationsChange = (event) => {
    const { value } = event.target;
    // value is an array of selected occupation codes
    onFilterChange({ occupations: typeof value === 'string' ? value.split(',') : value });
  };

  const handleChange = (field) => (event) => {
    onFilterChange({ [field]: event.target.value });
  };

  const handleAreaChange = (event) => {
    setAreaFilter(event.target.value);
    // Optional: Reset specific occupation when area changes
    onFilterChange({ occupations: [] });
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
  
  // Filter occupations based on Area of Work
  const filteredOccupations = React.useMemo(() => {
    if (!areaFilter) return occupations;
    
    // Filter logic: Check if occupation code starts with selected area
    return occupations.filter(occ => {
      if (occ.code) {
        return occ.code.toString().startsWith(areaFilter);
      }
      return true; // Keep occupations without code visible
    });
  }, [occupations, areaFilter]);

  // Get selected occupations array (ensure it's always an array)
  const selectedOccupations = filters.occupations || [];

  // Render value for multi-select
  const renderSelectedOccupations = (selected) => {
    if (selected.length === 0) {
      return <em style={{ color: '#9ca3af' }}>All Occupations</em>;
    }
    if (selected.length === 1) {
      const occ = occupations.find(o => o.code === selected[0] || o.name === selected[0]);
      return occ ? (occ.code ? `${occ.code} - ${occ.name}` : occ.name) : selected[0];
    }
    return `${selected.length} occupations selected`;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FilterListIcon sx={{ color: '#1b9e77', fontSize: 20 }} />
          <Typography variant="h6" sx={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI"', fontWeight: 600, fontSize: '1rem', color: '#374151', }}>
            Filters
          </Typography>
        </Box>
        {(selectedOccupations.length > 0 || filters.region || filters.year || filters.gender || areaFilter) && (
           <Chip 
             label="Clear All" 
             size="small" 
             onClick={() => {
               setAreaFilter('');
               onFilterChange({ occupations: [], region: '', year: '', gender: '' });
             }}
             sx={{ cursor: 'pointer' }}
           />
        )}
      </Box>
      
      <Grid container spacing={2}>
        {/* Area of Work Filter */}
        <Grid item xs={12} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Area of Work</InputLabel>
            <Select
              value={areaFilter}
              label="Area of Work"
              onChange={handleAreaChange}
              sx={selectStyles}
            >
              <MenuItem value=""><em>All Areas</em></MenuItem>
              {AREA_OF_WORK.map((area) => (
                <MenuItem key={area.code} value={area.code}>
                  {area.code} - {area.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Occupation Multi-Select Filter */}
        <Grid item xs={12} md={4}>
          <FormControl fullWidth size="small">
            <InputLabel>Occupation(s)</InputLabel>
            <Select
              multiple
              value={selectedOccupations}
              onChange={handleOccupationsChange}
              input={<OutlinedInput label="Occupation(s)" />}
              renderValue={renderSelectedOccupations}
              MenuProps={{ 
                PaperProps: { sx: { maxHeight: 400 } },
                anchorOrigin: { vertical: 'bottom', horizontal: 'left' },
                transformOrigin: { vertical: 'top', horizontal: 'left' },
              }}
              sx={selectStyles}
            >
              {filteredOccupations.map((occ, index) => {
                const value = occ.code || occ.name;
                return (
                  <MenuItem key={occ.id || index} value={value}>
                    <Checkbox 
                      checked={selectedOccupations.indexOf(value) > -1} 
                      sx={{ 
                        color: '#1b9e77',
                        '&.Mui-checked': { color: '#1b9e77' }
                      }}
                    />
                    <ListItemText 
                      primary={occ.code ? `${occ.code} - ${occ.name}` : occ.name} 
                      primaryTypographyProps={{ fontSize: '0.875rem' }}
                    />
                  </MenuItem>
                );
              })}
            </Select>
          </FormControl>
        </Grid>

        {/* Region Filter */}
        <Grid item xs={12} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Region</InputLabel>
            <Select
              value={filters.region || ''}
              label="Region"
              onChange={handleChange('region')}
              sx={selectStyles}
            >
              <MenuItem value=""><em>All Regions</em></MenuItem>
              {regions.map((reg, index) => (
                <MenuItem key={reg.code || index} value={reg.name}>
                  {reg.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Year Filter */}
        <Grid item xs={12} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Year</InputLabel>
            <Select
              value={filters.year || ''}
              label="Year"
              onChange={handleChange('year')}
              sx={selectStyles}
            >
              <MenuItem value=""><em>All Years</em></MenuItem>
              <MenuItem value={2023}>2023</MenuItem>
              <MenuItem value={2024}>2024</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        {/* Gender Filter */}
        <Grid item xs={12} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Gender</InputLabel>
            <Select
               value={filters.gender || ''}
               label="Gender"
               onChange={handleChange('gender')}
               sx={selectStyles}
            >
              <MenuItem value=""><em>All</em></MenuItem>
              <MenuItem value="men">Men</MenuItem>
              <MenuItem value="women">Women</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FilterPanel;
