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

