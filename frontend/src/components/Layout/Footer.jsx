import React from 'react';
import { Box, Container, Typography, Link, Divider, Grid } from '@mui/material';
import { 
  BarChart, 
  Map, 
  Info, 
  Launch, 
  School, 
  TrendingUp 
} from '@mui/icons-material';

const Footer = () => {
  return (
    <Box 
      component="footer" 
      sx={{ 
        bgcolor: '#f9fafb', 
        borderTop: '1px solid #e5e7eb',
        pt: 6, 
        pb: 6,
        mt: 'auto'
      }}
    >
      <Container maxWidth="xl">
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <TrendingUp sx={{ color: '#1b9e77', mr: 1 }} />
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#111827', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI"' }}>
                Swedish Labor Market Analytics
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2, maxWidth: '300px' }}>
              A comprehensive dashboard for analyzing salary trends, job vacancies, and regional distribution across Sweden's labor market.
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#111827', mb: 2 }}>
              Data Sources
            </Typography>
            <Box component="ul" sx={{ p: 0, m: 0, listStyle: 'none' }}>
              <Box component="li" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                <Link 
                  href="https://www.scb.se/en/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  color="inherit" 
                  underline="hover"
                  sx={{ display: 'flex', alignItems: 'center', fontSize: '0.875rem', color: '#4b5563' }}
                >
                  <Box component="span" sx={{ mr: 1, color: '#1b9e77' }}>●</Box>
                  Statistics Sweden (SCB) - Salary Structure
                  <Launch sx={{ fontSize: 12, ml: 0.5, color: '#9ca3af' }} />
                </Link>
              </Box>
              <Box component="li" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                <Link 
                  href="https://jobtechdev.se/en" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  color="inherit" 
                  underline="hover"
                  sx={{ display: 'flex', alignItems: 'center', fontSize: '0.875rem', color: '#4b5563' }}
                >
                  <Box component="span" sx={{ mr: 1, color: '#d95f02' }}>●</Box>
                  Arbetsförmedlingen - Historical Ads API
                  <Launch sx={{ fontSize: 12, ml: 0.5, color: '#9ca3af' }} />
                </Link>
              </Box>
              <Box component="li" sx={{ display: 'flex', alignItems: 'center' }}>
                <Link 
                  href="https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/nuts" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  color="inherit" 
                  underline="hover"
                  sx={{ display: 'flex', alignItems: 'center', fontSize: '0.875rem', color: '#4b5563' }}
                >
                  <Box component="span" sx={{ mr: 1, color: '#7570b3' }}>●</Box>
                  Eurostat - NUTS-2 Regional Data
                  <Launch sx={{ fontSize: 12, ml: 0.5, color: '#9ca3af' }} />
                </Link>
              </Box>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#111827', mb: 2 }}>
              Definitions & Notes
            </Typography>
            <Box component="ul" sx={{ p: 0, m: 0, listStyle: 'none' }}>
              <Box component="li" sx={{ mb: 1.5 }}>
                <Typography variant="caption" sx={{ display: 'block', fontWeight: 600, color: '#374151' }}>
                  Monthly Salary
                </Typography>
                <Typography variant="caption" color="text.secondary">
                   Total fixed cash salary (before tax) including fixed supplements.
                </Typography>
              </Box>
              <Box component="li" sx={{ mb: 1.5 }}>
                <Typography variant="caption" sx={{ display: 'block', fontWeight: 600, color: '#374151' }}>
                  Percentiles (P10, P90)
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  P10 is the wage below which 10% of employees fall. P90 is the wage below which 90% fall.
                </Typography>
              </Box>
              <Box component="li">
                <Typography variant="caption" sx={{ display: 'block', fontWeight: 600, color: '#374151' }}>
                  SSYK 2012
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  The Swedish Standard Classification of Occupations, based on ISCO-08.
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 4 }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
          <Typography variant="caption" color="text.secondary">
            © {new Date().getFullYear()} Labor Market Analytics. Data sources are copyright of their respective owners.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Tables: SCB AM0110A (LonYrkeRegion4AN, LoneSpridSektYrk4AN)
            </Typography>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
