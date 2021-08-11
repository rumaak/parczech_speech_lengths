# ParCzech speech lengths
Compute speech lengths of members of parliament.

### Examples
An example corpus file is in `samples/sample_input`. Running

```
xsltproc scripts/speech_timestamps.xsl samples/sample_input/ps2013-042-03-007-144.ana.xml > samples/sample_output/ps2013-042-03-007-144.ana.txt
```

in the root directory of this repository results in a `.txt` file in
`samples/sample_output` directory which contains extracted time-related
data about words in the corpus.

Having extracted time-related data from the original `.xml` file, running

```
scripts/per_file_statistics.py samples/sample_output/ps2013-042-03-007-144.ana.txt samples/sample_output
```

will create another output file in `samples/sample_out` directory, this
time with very simple statistics of speech lengths computed from the output
of the XSLT script. Details about what is computed are given in the script
file itself. The statistics themselves aren't computed over the TEI file
itself, but rather over audio files it contains.

It is important to note that the script takes into account existing files
with statistics. Running the script repeatedly without deleting generated
files first results in the statistics accumulating (which is not desired
behavior).

To observe how the script behaves when multiple timelines are present in a
TEI file, we first use the XSLT script to convert the TEI files in
`samples/sample_input/ps2013-042` to the `samples/sample_output/ps2013-042`
directory and then use the python script on them; we choose
`samples/sample_output/ps2013-042/audio_statistics/` as the output directory.

```
xsltproc scripts/speech_timestamps.xsl samples/sample_input/ps2013-042/ps2013-042-01-000-000.ana.xml > samples/sample_output/ps2013-042/ps2013-042-01-000-000.ana.txt
xsltproc scripts/speech_timestamps.xsl samples/sample_input/ps2013-042/ps2013-042-01-001-001.ana.xml > samples/sample_output/ps2013-042/ps2013-042-01-001-001.ana.txt
scripts/per_file_statistics.py samples/sample_output/ps2013-042/ps2013-042-01-000-000.ana.txt samples/sample_output/ps2013-042/audio_statistics
scripts/per_file_statistics.py samples/sample_output/ps2013-042/ps2013-042-01-001-001.ana.txt samples/sample_output/ps2013-042/audio_statistics
```




