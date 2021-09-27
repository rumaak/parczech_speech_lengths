import React from 'react'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography';

export const footerHeight = {
  xs: '800px',
  md: '400px'
};

export function Footer() {
    return (
      <Box sx={{
        width: "100%",
        height: footerHeight,
      }}>
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          bgcolor: '#07426e'
        }}>
          <Typography variant='h6'>
            Footer
          </Typography>
        </Box>
      </Box>
    )
}
