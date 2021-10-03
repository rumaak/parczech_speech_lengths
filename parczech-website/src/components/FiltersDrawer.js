import React from 'react'
import { useTheme } from '@mui/material/styles';
import { Button, Typography } from '@mui/material';
import { Box } from '@mui/material';
import { Drawer } from '@mui/material';
import { TextField } from '@mui/material';
import { Divider } from '@mui/material';
import { FormControl } from '@mui/material';
import { InputLabel } from '@mui/material';
import { Select } from '@mui/material';
import { OutlinedInput } from '@mui/material';
import { Chip } from '@mui/material';
import { MenuItem } from '@mui/material';
import { DateTimePicker } from '@mui/lab';
import { formatISO } from 'date-fns';

const requestUrl = 'http://127.0.0.1:8000/multiple/interval'

const speakers = [
    'JanHamacek.1978',
    'JaroslavFaltynek.1962',
    'TomioOkamura.1972'
]

function styleSelectedSpeakers(speaker, speakersFiltered, theme) {
  return {
    fontWeight:
      speakersFiltered.indexOf(speaker) === -1
        ? theme.typography.fontWeightRegular
        : theme.typography.fontWeightMedium,
  };
}

const createRequest = async ({ speakersFiltered, dateStart, dateEnd }) => {
    let request = {
        data: {
            interval: {
                start: formatISO(dateStart),
                end: formatISO(dateEnd)
            }
        }
    }

    if (speakersFiltered.length !== 0) {
        request['speakers'] = {
            static: {
                MoPs: speakersFiltered
            }
        }
    }

    return request
}

const onSubmit = async (filters, setStatistics) => {
    const request = await createRequest(filters)

    const options = {
        method: 'POST',
        body: JSON.stringify(request),
        headers: {
            'Content-Type': 'application/json'
        }
    }

    const res = await fetch(requestUrl, options)
    const stats = await res.json()

    setStatistics(stats)
}

export function FiltersDrawer({ drawerOpen, setDrawerOpen, setStatistics }) {
    const theme = useTheme();

    const [speakersFiltered, setSpeakersFiltered] = React.useState([]);
    const [dateStart, setDateStart] = React.useState(new Date());
    const [dateEnd, setDateEnd] = React.useState(new Date());

    const filters = { speakersFiltered, dateStart, dateEnd }

    return (
        <Drawer
            anchor='left'
            open={drawerOpen}
            onClose={() => { setDrawerOpen(false); }}
            sx={{
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: '300px' },
            }}
        >
            <Box sx={{px: "20px"}}>
                <Box sx={{pt: "5px"}}>
                    <Typography variant='h6' fontWeight='light'>
                        Filters
                    </Typography>
                </Box>
                <Divider/>

                <Box sx={{pt: "15px"}}>
                    <FormControl fullWidth>
                        <InputLabel htmlFor="speakers">Speakers</InputLabel>
                        <Select
                            id="speakers"
                            label='Speakers'
                            multiple
                            value={speakersFiltered}
                            onChange={(event) => {
                                const { target: { value } } = event;
                                setSpeakersFiltered(value);
                            }}
                            input={<OutlinedInput id="select-speakers" label="Speakers" />}
                            renderValue={(selected) => { 
                                return (
                                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                    {selected.map((value) => (
                                        <Chip key={value} label={value} />
                                    ))}
                                    </Box>
                                )
                            }}
                        >
                        {
                            speakers.map((speaker) => {
                                return (
                                    <MenuItem
                                        key={speaker}
                                        value={speaker}
                                        style={styleSelectedSpeakers(speaker, speakersFiltered, theme)}
                                    >
                                        {speaker}
                                    </MenuItem>
                                )
                            })
                        }
                        </Select>
                    </FormControl>
                </Box>
                <Box sx={{pt: "20px"}}>
                    <DateTimePicker
                        id="datetime-start"
                        renderInput={(props) => <TextField {...props} />}
                        label="Datetime start"
                        value={dateStart}
                        onChange={(newValue) => { setDateStart(newValue); }}
                    />
                </Box>
                <Box sx={{pt: "20px"}}>
                    <DateTimePicker
                        id="datetime-end"
                        renderInput={(props) => <TextField {...props} />}
                        label="Datetime end"
                        value={dateEnd}
                        onChange={(newValue) => { setDateEnd(newValue); }}
                    />
                </Box>
                <Box sx={{pt: "20px"}}>
                    <Button
                        variant='contained'
                        onClick={() => { onSubmit(filters, setStatistics) }}
                        fullWidth
                    >
                        Submit
                    </Button>
                </Box>
            </Box>
        </Drawer>
    )
}
