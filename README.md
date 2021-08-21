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

TODO fix the `scripts/aggregate_statistics_interval.py` so that it computes
statistics in similar manner to the second aggregation script (that computes
statistics over all election periods)

### Computing offline statistics
In the future, we might wish to present statistics computed over the dataset.
It makes sense to precompute certain statistics, as they will be used often.
We are thus going to precompute the statistics over election periods.

To do that, we use the `scripts/aggregate_statistics_all.py` and
`scripts/plot_statistics.py` scripts. The first one computes statistics over
all the available data and saves them to the specified directory. Example
usage:

```
scripts/aggregate_statistics_all.py samples/sample_audio_statistics_output samples/sample_statistics_output
```

Precomputed statistics can be found in the `precomputed/all.txt` file (path
relative to the output directory). Even though the plotting will be
probably done on the frontend of this projects website, we would like to have
some plots to present before setting up the actual website. For that, the
`scripts/plot_statistics.py` script is used - it allows us to create plots for
a particular member of parliament.

```
scripts/plot_statistics.py samples/sample_statistics_output/precomputed/all.txt samples/sample_statistics_output/precomputed/plots JaroslavFaltynek.1962
```

### Computing online statistics
TODO refer to the `scripts/aggregate_statistics_interval.py` example (will
be added ASAP)

