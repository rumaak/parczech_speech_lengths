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
```

First, note that we are using virtual environment with packages specified
in the `requirements.txt` file. Next, notice that even though there is an
asterisk in the first argument, it is not actually used for shell pattern
matching, as there are quotes around the first argument. Rather, pattern
matching is implemented in the python script itself. Last, it is important
to note that the script accumulates statistics; running it multiple times
without deleting previously generated output thus leads to wrong results.


