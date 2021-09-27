import React from 'react'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography';

export const headerHeight = {
  xs: '140px',
  md: '70px'
};

export function Header() {
    return (
      <Box sx={{
        width: "100%",
        height: headerHeight,
      }}>
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          bgcolor: '#39688b'
        }}>
          <Box>
            <Typography variant='h6'>
              Header
            </Typography>
          </Box>
        </Box>
      </Box>
    )
}
