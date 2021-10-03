import React from 'react'
import {  Typography, useMediaQuery } from '@mui/material';
import { Box } from '@mui/material';
import { Paper } from '@mui/material';
import { Chart } from 'react-google-charts';
import { Table, TableBody, TableHead, TableContainer, TableCell, TableRow } from '@mui/material';
import { useTheme } from '@mui/material/styles';

const statisticNames = {
    speaking_time: 'Total speaking time',
    relative_diff: 'Relative difference between metrics',
    unanchored: 'Ratio of unanchored words',
    wpm: 'Words per minute'
}

const statisticUnits = {
    speaking_time: 'hours',
    relative_diff: '%',
    unanchored: '%',
    wpm: 'word/minute'
}

const roles = {
    regular: 'Regular',
    chair: 'Chair',
    guest: 'Guest'
}

const statisticDesc = {
    speaking_time:
        'Total time the selected members of parliament spent speaking ' +
        'in the parliament according to the available data. The time can be measured ' +
        'several ways - per word, sentence, paragraph or whole utterance.',
    relative_diff:
        'As different ways of measuring how long the members of parliament spoke ' +
        'lead to different results, we might wish to explore how big those differences ' +
        'are. We will look at the relative difference between such results, i.e. the ' +
        'difference scaled between zero and one.',
    unanchored:
        "Related to the previous statistic is the number of words that weren't anchored " +
        "in the dataset, i.e. beginning or ending anchor was not available for the given " +
        "word. High number of unanchored words might explain the difference between the " +
        "total speech length of a member of parliament when measured in different ways.",
    wpm:
        'How many words per minute do these members of parliament say on average. ' +
        'Speaking speed, computed using from the number of words and total time spent ' +
        'speaking as measured over utterances.'
}

const roleDesc =  (statistic, role) => {
    const desc = {
        speaking_time:
            `The time these members of parliament spent speaking in the ${role} role.`,
        relative_diff:
            `The relative difference between results computed across data where the ` +
            `members of parliament spoke in the ${role} role.`,
        unanchored:
            `The percentage of unanchored words of these members of parliament when they` +
            `spoke in the ${role} role.`,
        wpm:
            `Speaking speed of these members of parliament when speaking in the ${role} role.`
    }
    return desc[statistic]
}

export function StatisticPaper({ name, statistics }) {
    const theme = useTheme();
    const big = useMediaQuery(theme.breakpoints.up('sm'))

    let chartWidth = big ? '75%' : '100%'

    return (
        <Box sx={{
            px: '10px',
            pt: '20px'
        }}>
            <Paper elevation='5' sx={{p: "10px"}}>
                <Typography variant='h5' fontWeight='medium'>
                    {statisticNames[name]}
                </Typography>

                <Typography variant='body1' align='justify' gutterBottom>
                    {statisticDesc[name]}
                </Typography>

                {
                    Object.keys(statistics).map((roleStat) => {
                        return (
                            <>
                                <Typography variant='h6' fontWeight='medium'>
                                    {roles[roleStat]}
                                </Typography>

                                <Typography variant='body1' align='justify' gutterBottom>
                                    {roleDesc(name, roleStat)}
                                </Typography>

                                <Box sx={{
                                    px: '20px'
                                }}>
                                    <Chart
                                        height={500}
                                        chartType="ColumnChart"
                                        loader={<div>Loading Chart</div>}
                                        data={statistics[roleStat]}
                                        options={{
                                            // title: statisticNames[name],
                                            chartArea: {
                                                width: chartWidth,
                                                height: '75%'
                                            },
                                            hAxis: {
                                                title: 'Speakers',
                                                minValue: 0,
                                            },
                                            vAxis: {
                                                title: `${statisticNames[name]} [${statisticUnits[name]}]`,
                                            },
                                        }}
                                        legendToggle
                                    />
                                </Box>

                                <Box sx={{
                                    py: '20px',
                                    px: '20px'
                                }}>
                                    <TableContainer component={Paper}>
                                        <Table size="small">
                                            <TableHead>
                                            <TableRow>
                                                {
                                                    statistics[roleStat][0].map((col) => {
                                                        return <TableCell>{col}</TableCell>
                                                    })
                                                }
                                            </TableRow>
                                            </TableHead>
                                            <TableBody>
                                            {statistics[roleStat].slice(1).map((row) => (
                                                <TableRow
                                                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                                >
                                                    {
                                                        row.map((item) => {
                                                            return (
                                                                <TableCell>
                                                                    {isNaN(item) ? item : Math.round((item + Number.EPSILON) * 1000) / 1000}
                                                                </TableCell>
                                                            )
                                                        })
                                                    }
                                                </TableRow>
                                            ))}
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </Box>
                            </>
                        )
                    })
                }
            </Paper>
        </Box>
    )
}
