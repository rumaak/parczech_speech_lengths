# ParCzech speech lengths
Compute speech lengths of members of parliament.

### Installation
Clone this repository, install dependencies in `requirements.txt`.

Install this package:

```
pip install -e .
```

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

Now we would like to compute some statistics from the available data. First,
we are going to compute the statistics over all the data we have. Because
this can be done in advance and the results will be probably reused many
times, we will refer to this as the _precomputation_.

```
scripts/aggregate_statistics_all.py samples/sample_audio_statistics_output samples/sample_statistics_output
```

Inside the `samples/sample_audio_statistics_output` a new directory
`precomputed` was created, with a single file - `all.txt`. This file contains
statistics for all the members of parliament. Now we would like to visualize
the results we obtained. For that, the `scripts/plot_statistics.py` script
is used.

```
scripts/plot_statistics.py samples/sample_statistics_output/precomputed/all.txt samples/sample_statistics_output/precomputed/plots/JaroslavFaltynek.1962 term JaroslavFaltynek.1962
```

The meaning of each argument is described in the script. The line above will
produce plots of the precomputed statistics for MoP with id
`JaroslavFaltynek.1962`. We can thus obtain some basic statistics about any
MoP.

Second, we would like to compute the same statistics but over a custom
time period.

```
scripts/aggregate_statistics_interval.py samples/sample_audio_statistics_output samples/sample_statistics_output 2016-03-01T13:58:00 2016-03-23T14:02:00
```

Executing the line above leads to statistics being computed in the same
manner as before, with the only difference that only the audio files from
the specified time interval are included. The results are saved into a
directory whose name reflects the time period over which the statistics
are computed.

Now we are going to plot these results. Running

```
scripts/plot_statistics.py samples/sample_statistics_output/201603011358-201603231402/all.txt samples/sample_statistics_output/201603011358-201603231402/plots/JaroslavFaltynek.1962 speaker JaroslavFaltynek.1962
```

results in plots of the statistics over the given time interval for MoP with
id `JaroslavFaltynek.1962`. Moreover, we can specify multiple MoPs:

```
scripts/plot_statistics.py samples/sample_statistics_output/201603011358-201603231402/all.txt samples/sample_statistics_output/201603011358-201603231402/plots/multiple speaker JaroslavFaltynek.1962 JiriStetina.1941
```

This enables us to compare the statistics between multiple MoPs.

Comparing between multiple selected MoPs is nice, but we would like to have
some default interesting selection of MoPs to plot the data for. Top
performers in terms of individual metrics would seem like a good start. We
are thus going to plot those:

```
scripts/plot_top.py samples/sample_statistics_output/201603011358-201603231402/all.txt samples/sample_statistics_output/201603011358-201603231402/plots/top
```

