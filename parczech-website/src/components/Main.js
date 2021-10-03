import React from 'react'
import {  Typography } from '@mui/material';
import { Box } from '@mui/material';
import { ToggleButton } from '@mui/material';
import { FiltersDrawer } from './FiltersDrawer';
import { StatisticPaper } from './StatisticPaper';

export function Main() {
    const [drawerOpen, setDrawerOpen] = React.useState(false);
    const [statistics, setStatistics] = React.useState({});

    return (
        <>
            <FiltersDrawer
                drawerOpen={drawerOpen}
                setDrawerOpen={setDrawerOpen}
                setStatistics={setStatistics}
            />
            <Box sx={{
                py: '50px',
                px: '10px'
            }}>
                <Box sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    pb: '10px'
                }}>
                    <Box>
                        <Box sx={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: '100%',
                        }}>
                            <Typography variant='h4' fontWeight='medium'>
                                ParCzech Audio Statistics
                            </Typography>
                        </Box>
                    </Box>
                    <Box>
                        <ToggleButton
                            value="web"
                            aria-label='list'
                            size='small'
                            selected={drawerOpen}
                            onChange={() => {setDrawerOpen(!drawerOpen);}}
                        >
                                Filters
                        </ToggleButton>
                    </Box>
                </Box>
                <Box>
                    <Typography variant='body1' align='justify'>
                        Statistics computed over czech parliamentary data corpus ParCzech.
                        To view statistics computed over a particular subset of data (e.g. over a
                        custom time period) click on the FILTERS button and set the filters to
                        appropriate values. Aggregated statistics are displayed below, one panel
                        per statistic.
                    </Typography>
                </Box>

                {
                    Object.keys(statistics).map((stat) => {
                        return (
                            <StatisticPaper
                                id={'statistic-' + stat}
                                name={stat}
                                statistics={statistics[stat]}
                            />
                        )
                    })
                }

            </Box>
        </>
    )
}
