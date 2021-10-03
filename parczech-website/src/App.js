import DateAdapter from '@mui/lab/AdapterDateFns';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Grid } from '@mui/material';
import { Main } from './components/Main';
import { LocalizationProvider } from '@mui/lab';
import './App.css'

function App() {
  return (
    <LocalizationProvider dateAdapter={DateAdapter}>
      <Header/>

      <Grid container>
        <Grid item xs={0} sm={2}/>
        <Grid item xs={12} sm={8}>
          <Main/>
        </Grid>
        <Grid item xs={0} sm={2}/>
      </Grid>

      <Footer/>
    </LocalizationProvider>
  );
}

export default App;
