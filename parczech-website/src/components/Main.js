import React from 'react'
import { Typography } from '@mui/material';
import { Box } from '@mui/material';
import { ToggleButton } from '@mui/material';
import { Drawer } from '@mui/material';
import { TextField } from '@mui/material';
import { Divider } from '@mui/material';
import { Paper } from '@mui/material';
import { Grid } from '@mui/material';
import { Chart } from 'react-google-charts';
import { Table, TableBody, TableHead, TableContainer, TableCell, TableRow } from '@mui/material';

const data = [
    ['City', '2010 Population', '2000 Population'],
    ['New York City, NY', 8175000, 8008000],
    ['Los Angeles, CA', 3792000, 3694000],
    ['Chicago, IL', 2695000, 2896000],
    ['Houston, TX', 2099000, 1953000],
    ['Philadelphia, PA', 1526000, 1517000],
]

const rows = data.slice(1).map((item) => {
    return {
        city: item[0], 
        population2010: item[1],
        population2000: item[2]
    };
})

export function Main() {
    const [state, setState] = React.useState({
        drawerOpen: false
    });

    return (
        <>
            <Drawer
                anchor='left'
                open={state['drawerOpen']}
                onClose={() => {setState({...state, drawerOpen: false});}}
            >
                     <Box sx={{px: "20px"}}>
                        <Box sx={{pt: "5px"}}>
                            <Typography variant='h6' fontWeight='light'>
                                Filters
                            </Typography>
                        </Box>
                        <Divider/>
                        <Box sx={{pt: "5px"}}>
                            <TextField id="standard-basic" label="Name" variant="standard" fullWidth />
                        </Box>
                        <Box sx={{pt: "5px"}}>
                            <TextField id="standard-basic" label="Age" variant="standard" fullWidth />
                        </Box>
                    </Box>
            </Drawer>
            <Box sx={{
                // bgcolor: 'lightblue',
                py: '50px',
                px: '10px'
            }}>
                <Box sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    // bgcolor: 'lightpink',
                    pb: '10px'
                }}>
                    <Box sx={{
                        // bgcolor: 'lightgray',
                    }}>
                        <Box sx={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: '100%',
                        }}>
                            <Typography variant='h5'>
                                Visualizations
                            </Typography>
                        </Box>
                    </Box>
                    <Box sx={{
                        // bgcolor: 'lightgray',
                        // pr: '10px'
                    }}>
                        <ToggleButton
                            value="web"
                            aria-label='list'
                            size='small'
                            selected={state['drawerOpen']}
                            onChange={() => {setState({...state, drawerOpen: !state['drawerOpen']});}}>
                                Filters
                        </ToggleButton>
                    </Box>
                </Box>
                <Box>
                    <Typography variant='body1' align='justify'>
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                        eiusmod tempor incididunt ut labore et dolore magna aliqua. Rhoncus
                        dolor purus non enim praesent elementum facilisis leo vel. Risus at
                        ultrices mi tempus imperdiet. Semper risus in hendrerit gravida rutrum
                        quisque non tellus. Convallis convallis tellus id interdum velit
                        laoreet id donec ultrices. Odio morbi quis commodo odio aenean sed
                        adipiscing. Amet nisl suscipit adipiscing bibendum est ultricies
                        integer quis. Cursus euismod quis viverra nibh cras. Metus vulputate
                        eu scelerisque felis imperdiet proin fermentum leo. Mauris commodo
                        quis imperdiet massa tincidunt. Cras tincidunt lobortis feugiat
                        vivamus at augue. At augue eget arcu dictum varius duis at consectetur
                        lorem. Velit sed ullamcorper morbi tincidunt. Lorem donec massa sapien
                        faucibus et molestie ac.
                    </Typography>
                </Box>
                <Box sx={{
                    px: '10px',
                    pt: '20px'
                }}>
                    <Paper elevation='5' sx={{p: "10px"}}>
                        <Typography variant='h6'>
                            Statistic 1
                        </Typography>
                        <Typography variant='body1' gutterBottom>
                            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                            eiusmod tempor incididunt ut labore et dolore magna aliqua. Rhoncus
                            dolor purus non enim praesent elementum facilisis leo vel. Risus at
                            ultrices mi tempus imperdiet. Semper risus in hendrerit gravida rutrum
                            quisque non tellus. Convallis convallis tellus id interdum velit
                            laoreet id donec ultrices. Odio morbi quis commodo odio aenean sed
                            adipiscing. Amet nisl suscipit adipiscing bibendum est ultricies
                            integer quis. Cursus euismod quis viverra nibh cras. Metus vulputate
                            eu scelerisque felis imperdiet proin fermentum leo. Mauris commodo
                            quis imperdiet massa tincidunt. Cras tincidunt lobortis feugiat
                            vivamus at augue. At augue eget arcu dictum varius duis at consectetur
                            lorem. Velit sed ullamcorper morbi tincidunt. Lorem donec massa sapien
                            faucibus et molestie ac.
                        </Typography>

                        <Grid container alignItems='center'>
                            <Grid item xs={12} lg={6}>
                                <Chart
                                    height={500}
                                    chartType="ColumnChart"
                                    loader={<div>Loading Chart</div>}
                                    data={[
                                    ['City', '2010 Population', '2000 Population'],
                                    ['New York City, NY', 8175000, 8008000],
                                    ['Los Angeles, CA', 3792000, 3694000],
                                    ['Chicago, IL', 2695000, 2896000],
                                    ['Houston, TX', 2099000, 1953000],
                                    ['Philadelphia, PA', 1526000, 1517000],
                                    ]}
                                    options={{
                                    title: 'Population of Largest U.S. Cities',
                                    chartArea: { width: '50%' },
                                    hAxis: {
                                        title: 'Total Population',
                                        minValue: 0,
                                    },
                                    vAxis: {
                                        title: 'City',
                                    },
                                    }}
                                    legendToggle
                                />
                            </Grid>
                            <Grid item xs={12} lg={6}>
                                <TableContainer component={Paper}>
                                    <Table sx={{ minWidth: 650 }} aria-label="simple table">
                                        <TableHead>
                                        <TableRow>
                                            <TableCell>City name</TableCell>
                                            <TableCell align="right">2010 population</TableCell>
                                            <TableCell align="right">2000 population</TableCell>
                                        </TableRow>
                                        </TableHead>
                                        <TableBody>
                                        {rows.map((row) => (
                                            <TableRow
                                            key={row.name}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                            >
                                            <TableCell component="th" scope="row">
                                                {row.city}
                                            </TableCell>
                                            <TableCell align="right">{row.population2010}</TableCell>
                                            <TableCell align="right">{row.population2000}</TableCell>
                                            </TableRow>
                                        ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </Grid>
                        </Grid>
                    </Paper>
                </Box>

                <Box sx={{
                    px: '10px',
                    pt: '20px'
                }}>
                    <Paper elevation='5' sx={{p: "10px"}}>
                        <Typography variant='h6'>
                            Statistic 2
                        </Typography>
                        <Typography variant='body1' gutterBottom>
                            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                            eiusmod tempor incididunt ut labore et dolore magna aliqua. Rhoncus
                            dolor purus non enim praesent elementum facilisis leo vel. Risus at
                            ultrices mi tempus imperdiet. Semper risus in hendrerit gravida rutrum
                            quisque non tellus. Convallis convallis tellus id interdum velit
                            laoreet id donec ultrices. Odio morbi quis commodo odio aenean sed
                            adipiscing. Amet nisl suscipit adipiscing bibendum est ultricies
                            integer quis. Cursus euismod quis viverra nibh cras. Metus vulputate
                            eu scelerisque felis imperdiet proin fermentum leo. Mauris commodo
                            quis imperdiet massa tincidunt. Cras tincidunt lobortis feugiat
                            vivamus at augue. At augue eget arcu dictum varius duis at consectetur
                            lorem. Velit sed ullamcorper morbi tincidunt. Lorem donec massa sapien
                            faucibus et molestie ac.
                        </Typography>

                        <Grid container alignItems='center'>
                            <Grid item xs={12} lg={6}>
                                <Chart
                                    height={500}
                                    chartType="ColumnChart"
                                    loader={<div>Loading Chart</div>}
                                    data={[
                                    ['City', '2010 Population', '2000 Population'],
                                    ['New York City, NY', 8175000, 8008000],
                                    ['Los Angeles, CA', 3792000, 3694000],
                                    ['Chicago, IL', 2695000, 2896000],
                                    ['Houston, TX', 2099000, 1953000],
                                    ['Philadelphia, PA', 1526000, 1517000],
                                    ]}
                                    options={{
                                    title: 'Population of Largest U.S. Cities',
                                    chartArea: { width: '50%' },
                                    hAxis: {
                                        title: 'Total Population',
                                        minValue: 0,
                                    },
                                    vAxis: {
                                        title: 'City',
                                    },
                                    }}
                                    legendToggle
                                />
                            </Grid>
                            <Grid item xs={12} lg={6}>
                                <TableContainer component={Paper}>
                                    <Table sx={{ minWidth: 650 }} aria-label="simple table">
                                        <TableHead>
                                        <TableRow>
                                            <TableCell>City name</TableCell>
                                            <TableCell align="right">2010 population</TableCell>
                                            <TableCell align="right">2000 population</TableCell>
                                        </TableRow>
                                        </TableHead>
                                        <TableBody>
                                        {rows.map((row) => (
                                            <TableRow
                                            key={row.name}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                            >
                                            <TableCell component="th" scope="row">
                                                {row.city}
                                            </TableCell>
                                            <TableCell align="right">{row.population2010}</TableCell>
                                            <TableCell align="right">{row.population2000}</TableCell>
                                            </TableRow>
                                        ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </Grid>
                        </Grid>
                    </Paper>
                </Box>

            </Box>
        </>
    )
}
