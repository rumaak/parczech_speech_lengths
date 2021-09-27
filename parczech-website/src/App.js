import { headerHeight, Header } from './components/Header';
import { Footer } from './components/Footer';
import Box from '@mui/material/Box';
import { Grid } from '@mui/material';
import { Main } from './components/Main';
import './App.css'

function App() {
  return (
    <>
      <Header/>

      <Grid container>
        <Grid item xs={0} sm={2}/>
        <Grid item xs={12} sm={8}>
          <Main/>
        </Grid>
        <Grid item xs={0} sm={2}/>
      </Grid>

      <Footer/>
    </>
  );
}

export default App;
