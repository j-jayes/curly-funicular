import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import WorkIcon from '@mui/icons-material/Work';

const Header = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <WorkIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Swedish Labor Market Analytics
        </Typography>
        <Typography variant="body2">
          Income & Job Statistics
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
