import React, { useEffect } from 'react'
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
import { FixedSizeList } from 'react-window';

const requestUrl = 'http://127.0.0.1:8000/multiple/interval'
const speakerDataUrl = 'http://127.0.0.1:8000/data/speakers'

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

const onSubmit = async (filters, setStatistics, setLoading) => {
    setLoading(true);

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
    setLoading(false);
}

const defaultFilters = {
    speakers: [
        'JanHamacek.1978',
        'JaroslavFaltynek.1962',
        'TomioOkamura.1972',
        'VojtechFilip.1955',
        'IvanBartos.1980'
    ],
    dateStart: new Date(2015, 1, 1),
    dateEnd: new Date()
}

export function FiltersDrawer({ drawerOpen, setDrawerOpen, setStatistics, setLoading }) {
    const theme = useTheme();

    const [speakers, setSpeakers] = React.useState([]);
    const [speakersFiltered, setSpeakersFiltered] = React.useState(
        defaultFilters['speakers']
    );
    const [dateStart, setDateStart] = React.useState(
        defaultFilters['dateStart']
    );
    const [dateEnd, setDateEnd] = React.useState(
        defaultFilters['dateEnd']
    );

    const filters = { speakersFiltered, dateStart, dateEnd }

    // load speakers from backend
    useEffect(() => {
        fetch(speakerDataUrl)
            .then((response) => { return response.json() })
            .then(({ speakers }) => {
                setSpeakers(speakers)
                onSubmit(filters, setStatistics, setLoading)
            })
    // eslint-disable-next-line react-hooks/exhaustive-deps            
    }, [])

    const SpeakerRow = ({ index, style }) => (
        <div style={style}>
            {
                <MenuItem
                    key={speakers[index]}
                    value={speakers[index]}
                    onClick={() => {
                        const idx = speakersFiltered.indexOf(speakers[index])
                        let newFiltered = [...speakersFiltered]
                        if (idx > -1) {
                            newFiltered.splice(idx, 1)
                        } else {
                            newFiltered.push(speakers[index])
                        }
                        setSpeakersFiltered(newFiltered)
                    }}
                    style={styleSelectedSpeakers(speakers[index], speakersFiltered, theme)}
                >
                    {speakers[index]}
                </MenuItem>
            }
        </div>
    );

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
                                        <Chip
                                            key={value} 
                                            label={value} 
                                        />
                                    ))}
                                    </Box>
                                )
                            }}
                        >
                            <FixedSizeList
                                itemCount={speakers.length}
                                height={300}
                                width={300}
                                itemSize={46}
                                overscanCount={5}
                            >
                                { SpeakerRow }
                            </FixedSizeList>
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
                <Box sx={{py: "20px"}}>
                    <Button
                        variant='contained'
                        onClick={() => { onSubmit(filters, setStatistics, setLoading) }}
                        fullWidth
                    >
                        Submit
                    </Button>
                </Box>
            </Box>
        </Drawer>
    )
}
