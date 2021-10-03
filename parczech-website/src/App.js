import DateAdapter from '@mui/lab/AdapterDateFns';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Grid } from '@mui/material';
import { Box } from '@mui/material';
import { Main } from './components/Main';
import { LocalizationProvider } from '@mui/lab';
import './App.css'

function App() {
  return (
    <LocalizationProvider dateAdapter={DateAdapter}>
      <Box sx={{
        position: 'absolute',
        minHeight: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
      }}>
        <Box>
          <Header/>

          <Grid container>
            <Grid item xs={0} sm={2}/>
            <Grid item xs={12} sm={8}>
              <Main/>
            </Grid>
            <Grid item xs={0} sm={2}/>
          </Grid>
        </Box>

        <Footer/>
      </Box>
    </LocalizationProvider>
  );
}

export default App;
