import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, ThemeProvider, createTheme, Typography, Box, Divider } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import WorkIcon from '@mui/icons-material/Work';
import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';
import FilterPanel from './components/Filters/FilterPanel';
import SwedenMap from './components/Map/SwedenMap';
import IncomeChart from './components/Charts/IncomeChart';
import GenderScatterPlot from './components/Charts/GenderScatterPlot';
import JobsChart from './components/Charts/JobsChart';
import TopEmployersChart from './components/Charts/TopEmployersChart';
import SkillsChart from './components/Charts/SkillsChart';
import { fetchIncomeData, fetchIncomeDispersion, fetchJobAds, fetchTopEmployers, fetchSkills, fetchOccupations, fetchRegions } from './services/api';
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
    occupations: [],  // Changed from occupation (string) to occupations (array)
    region: '',
    year: '',
    gender: ''
  });
  
  const [incomeData, setIncomeData] = useState([]);
  const [dispersionData, setDispersionData] = useState([]);
  const [jobsData, setJobsData] = useState([]);
  const [topEmployers, setTopEmployers] = useState([]);
  const [skills, setSkills] = useState([]);
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
      const [income, dispersion, jobs, employers, skillsData] = await Promise.all([
        fetchIncomeData(filters),
        fetchIncomeDispersion(filters),
        fetchJobAds(filters),
        fetchTopEmployers(filters),
        fetchSkills(filters)
      ]);
      setIncomeData(income);
      setDispersionData(dispersion);
      setJobsData(jobs);
      setTopEmployers(employers);
      setSkills(skillsData);
    } catch (error) {
      console.error('Error loading filtered data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters({ ...filters, ...newFilters });
  };

  // Section header component for visual separation
  const SectionHeader = ({ icon, title, subtitle, color }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
      <Box sx={{ 
        p: 1, 
        borderRadius: '8px', 
        bgcolor: `${color}15`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        {icon}
      </Box>
      <Box>
        <Typography variant="h6" sx={{ 
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI"', 
          fontWeight: 600, 
          fontSize: '1.1rem',
          color: '#1f2937'
        }}>
          {title}
        </Typography>
        <Typography variant="caption" sx={{ color: '#6b7280', fontSize: '0.75rem' }}>
          {subtitle}
        </Typography>
      </Box>
    </Box>
  );

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

            {/* ===== INCOME STATISTICS SECTION ===== */}
            <Grid item xs={12}>
              <SectionHeader 
                icon={<TrendingUpIcon sx={{ color: '#1b9e77', fontSize: 24 }} />}
                title="Income Statistics"
                subtitle="Data source: Statistics Sweden (SCB) • Salary data by occupation and region"
                color="#1b9e77"
              />
            </Grid>

            {/* Map - Full height for Sweden's shape */}
            <Grid item xs={12} md={5}>
              <Paper sx={{ p: 3, height: '720px', bgcolor: '#fafffe' }} className="transition-shadow hover:shadow-lg">
                <SwedenMap data={incomeData} selectedRegion={filters.region} />
              </Paper>
            </Grid>

            {/* Right column: Scatter Plot + Bar Chart stacked */}
            <Grid item xs={12} md={7}>
              <Grid container spacing={3}>
                {/* Gender Salary Scatter Plot */}
                <Grid item xs={12}>
                  <Paper sx={{ p: 3, height: '400px', bgcolor: '#fafffe' }} className="transition-shadow hover:shadow-lg">
                    <GenderScatterPlot data={dispersionData} loading={loading} />
                  </Paper>
                </Grid>

                {/* Income by Region/Occupation Bar Chart */}
                <Grid item xs={12}>
                  <Paper sx={{ p: 3, height: '296px', bgcolor: '#fafffe' }} className="transition-shadow hover:shadow-lg">
                    <IncomeChart data={incomeData} loading={loading} />
                  </Paper>
                </Grid>
              </Grid>
            </Grid>

            {/* Divider between sections */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>

            {/* ===== JOB MARKET SECTION ===== */}
            <Grid item xs={12}>
              <SectionHeader 
                icon={<WorkIcon sx={{ color: '#7570b3', fontSize: 24 }} />}
                title="Job Market Data"
                subtitle="Data source: Arbetsförmedlingen (Swedish Public Employment Service) • Historical job advertisements"
                color="#7570b3"
              />
            </Grid>

            {/* Top Employers */}
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '400px', bgcolor: '#fafaff' }} className="transition-shadow hover:shadow-lg">
                <TopEmployersChart data={topEmployers} loading={loading} />
              </Paper>
            </Grid>

            {/* Skills */}
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '400px', bgcolor: '#fafaff' }} className="transition-shadow hover:shadow-lg">
                <SkillsChart data={skills} loading={loading} />
              </Paper>
            </Grid>

            {/* Jobs by Region */}
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '400px', bgcolor: '#fafaff' }} className="transition-shadow hover:shadow-lg">
                <JobsChart data={jobsData} loading={loading} />
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
