import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, ThemeProvider, createTheme } from '@mui/material';
import Header from './components/Layout/Header';
import FilterPanel from './components/Filters/FilterPanel';
import SwedenMap from './components/Map/SwedenMap';
import IncomeChart from './components/Charts/IncomeChart';
import JobsChart from './components/Charts/JobsChart';
import { fetchIncomeData, fetchJobAds, fetchOccupations, fetchRegions } from './services/api';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [filters, setFilters] = useState({
    occupation: '',
    region: '',
    ageGroup: '',
    gender: ''
  });
  
  const [incomeData, setIncomeData] = useState([]);
  const [jobsData, setJobsData] = useState([]);
  const [occupations, setOccupations] = useState([]);
  const [regions, setRegions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadFilteredData();
  }, [filters]);

  const loadInitialData = async () => {
    try {
      const [occData, regData] = await Promise.all([
        fetchOccupations(),
        fetchRegions()
      ]);
      setOccupations(occData);
      setRegions(regData);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const loadFilteredData = async () => {
    setLoading(true);
    try {
      const [income, jobs] = await Promise.all([
        fetchIncomeData(filters),
        fetchJobAds(filters)
      ]);
      setIncomeData(income);
      setJobsData(jobs);
    } catch (error) {
      console.error('Error loading filtered data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters({ ...filters, ...newFilters });
  };

  return (
    <ThemeProvider theme={theme}>
      <div className="App">
        <Header />
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Grid container spacing={3}>
            {/* Filters */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <FilterPanel
                  filters={filters}
                  occupations={occupations}
                  regions={regions}
                  onFilterChange={handleFilterChange}
                />
              </Paper>
            </Grid>

            {/* Map */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '500px' }}>
                <SwedenMap data={incomeData} selectedRegion={filters.region} />
              </Paper>
            </Grid>

            {/* Income Chart */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '500px' }}>
                <IncomeChart data={incomeData} loading={loading} />
              </Paper>
            </Grid>

            {/* Jobs Chart */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2, height: '400px' }}>
                <JobsChart data={jobsData} loading={loading} />
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </div>
    </ThemeProvider>
  );
}

export default App;
