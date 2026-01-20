import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, ThemeProvider, createTheme } from '@mui/material';
import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';
import FilterPanel from './components/Filters/FilterPanel';
import SwedenMap from './components/Map/SwedenMap';
import IncomeChart from './components/Charts/IncomeChart';
import IncomeBoxPlot from './components/Charts/IncomeBoxPlot';
import JobsChart from './components/Charts/JobsChart';
import { fetchIncomeData, fetchIncomeDispersion, fetchJobAds, fetchOccupations, fetchRegions } from './services/api';
import './App.css';

// Modern Apple-inspired theme with Dark2 palette accents
const theme = createTheme({
  palette: {
    primary: {
      main: '#1b9e77', // Dark2 teal
    },
    secondary: {
      main: '#d95f02', // Dark2 orange
    },
    background: {
      default: '#f9fafb',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
          border: '1px solid #f3f4f6',
        },
      },
    },
  },
});

function App() {
  const [filters, setFilters] = useState({
    occupation: '',
    region: '',
    year: '',
    gender: ''
  });
  
  const [incomeData, setIncomeData] = useState([]);
  const [dispersionData, setDispersionData] = useState([]);
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
      const [income, dispersion, jobs] = await Promise.all([
        fetchIncomeData(filters),
        fetchIncomeDispersion(filters),
        fetchJobAds(filters)
      ]);
      setIncomeData(income);
      setDispersionData(dispersion);
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
      <div className="App min-h-screen bg-gray-50">
        <Header />
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Grid container spacing={3}>
            {/* Filters */}
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }} className="transition-shadow hover:shadow-lg">
                <FilterPanel
                  filters={filters}
                  occupations={occupations}
                  regions={regions}
                  onFilterChange={handleFilterChange}
                />
              </Paper>
            </Grid>

            {/* Map - Taller and narrower for Sweden's shape */}
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '680px' }} className="transition-shadow hover:shadow-lg">
                <SwedenMap data={incomeData} selectedRegion={filters.region} />
              </Paper>
            </Grid>

            {/* Charts Column */}
            <Grid item xs={12} md={8}>
              <Grid container spacing={3}>
                {/* Income Box Plot - Salary Distribution */}
                <Grid item xs={12}>
                  <Paper sx={{ p: 3, height: '420px' }} className="transition-shadow hover:shadow-lg">
                    <IncomeBoxPlot data={dispersionData} loading={loading} />
                  </Paper>
                </Grid>

                {/* Jobs Chart */}
                <Grid item xs={12}>
                  <Paper sx={{ p: 3, height: '240px' }} className="transition-shadow hover:shadow-lg">
                    <JobsChart data={jobsData} loading={loading} />
                  </Paper>
                </Grid>
              </Grid>
            </Grid>

            {/* Full width Income Chart by Region */}
            <Grid item xs={12}>
              <Paper sx={{ p: 3, height: '400px' }} className="transition-shadow hover:shadow-lg">
                <IncomeChart data={incomeData} loading={loading} />
              </Paper>
            </Grid>
          </Grid>
        </Container>
        <Footer />
      </div>
    </ThemeProvider>
  );
}

export default App;
