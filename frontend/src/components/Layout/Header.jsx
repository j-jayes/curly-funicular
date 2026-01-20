import React from 'react';
import { AppBar, Toolbar, Typography, Box, Chip } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const Header = () => {
  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        background: 'linear-gradient(135deg, #1b9e77 0%, #0d7c5c 100%)',
        borderBottom: '1px solid rgba(255,255,255,0.1)'
      }}
    >
      <Toolbar className="px-6 py-3">
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <TrendingUpIcon sx={{ fontSize: 28 }} />
          <Box>
            <Typography 
              variant="h5" 
              component="div" 
              sx={{ 
                fontWeight: 600,
                letterSpacing: '-0.02em',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
              }}
            >
              Swedish Labor Market Analytics
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                opacity: 0.9,
                fontWeight: 400,
                fontSize: '0.85rem'
              }}
            >
              Income & job statistics for ICT and data science occupations
            </Typography>
          </Box>
        </Box>
        <Box sx={{ flexGrow: 1 }} />
        <Chip 
          label="Data from SCB & Arbetsförmedlingen" 
          size="small"
          sx={{ 
            backgroundColor: 'rgba(255,255,255,0.15)',
            color: 'white',
            fontWeight: 500,
            fontSize: '0.75rem',
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.25)'
            }
          }}
        />
      </Toolbar>
    </AppBar>
  );
};

export default Header;
