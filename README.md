# ParCzech speech lengths
Compute speech lengths of members of parliament.

### Examples
An example of corpus data is available in the `samples/sample_input`
directory. To apply XSLT transformation extracting time-related data
from the sample, execute the `scripts/xslt_apply.sh` script in the root
of the repository. An example of this, where the time spent on the execution
is also measured, can be seen below.

```
[rumaak@rumaak parczech_speech_lengths]$ time scripts/xslt_apply.sh "samples/sample_input/ps2013-042" "samples/sample_xslt_output/ps2013-042"

real	198m6.457s
user	197m44.984s
sys	0m6.407s
[rumaak@rumaak parczech_speech_lengths]$ time scripts/xslt_apply.sh "samples/sample_input/ps2017-002" "samples/sample_xslt_output/ps2017-002"

real	3m9.099s
user	3m8.534s
sys	0m0.320s
```

The script takes two arguments - input data source directory (is expected
to contain zero or more xml files) and output directory (a single `.txt` file
is created for every `.xml` file).

Having extracted the time-related data, we can proceed to per-audio
statistics. For that, we are going to use the `per_file_statistics.py` python
script. An example of usage can be seen below.

```
(venv) [rumaak@rumaak parczech_speech_lengths]$ time scripts/per_file_statistics.py "samples/sample_xslt_output/ps2013-042/*" samples/sample_audio_statistics_output

real	0m39.421s
user	0m39.262s
sys	0m0.728s
(venv) [rumaak@rumaak parczech_speech_lengths]$ time scripts/per_file_statistics.py "samples/sample_xslt_output/ps2017-002/*" samples/sample_audio_statistics_output

real	0m3.475s
user	0m3.641s
sys	0m0.499s
```

First, note that we are using virtual environment with packages specified
in the `requirements.txt` file. Next, notice that even though there is an
asterisk in the first argument, it is not actually used for shell pattern
matching, as there are quotes around the first argument. Rather, pattern
matching is implemented in the python script itself. Last, it is important
to note that the script accumulates statistics; running it multiple times
without deleting previously generated output thus leads to wrong results.

Now we would like to compute statistics over some time interval. For that,
we are going to use the `scripts/aggregate_statistics.py` python script.
We need to tell the script where the audio statistics data are stored
(`samples/sample_audio_statistics_output`), where it should output the
computed statistics and plots
(`samples/sample_statistics_output/201603011358-201603231402`) and
what is the interval over which we want to compute the statistics (note
that the interval over which we compute the statistics is reflected
in the output directory name).

```
scripts/aggregate_statistics.py samples/sample_audio_statistics_output samples/sample_statistics_output/201603011358-201603231402 2016-03-01T13:58:00 2016-03-23T14:02:00
```

Executing the line above leads to statistics being generated into the specified
output directory. The statistics are computed over the interval starting at
`2016-03-01T13:58:00` and ending at `2016-03-23T14:02:00`.

### Computing offline statistics
In the future, we might wish to present statistics computed over the dataset.
It makes sense to precompute certain statistics, as they will be used often.
We are thus going to precompute the statistics over election periods.

TODO precomputing offline statistics over election periods

### Computing online statistics
It is not feasible to compute the statistics over all the possible time
intervals. For that purpose, we will use the `scripts/aggregate_statistics.py`
script as shown in the Examples section whenever we are asked for statistics
over a partilar time period (for example when requested from a web client).

