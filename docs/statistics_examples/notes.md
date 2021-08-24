# Notes on the examples

### Examples

Each example should showcase some feature we would like to have in the final visualization on the project website. Short summary for each is given below.

__JaroslavFaltynek.1962_all__: Statistics for a single member of parliament computed over the totality of data; this member of parliament spoke in multiple election periods, which is reflected in the plots.

__TomioOkamura.1972_all__: Statistics for a single member of parliament computed over the totality of data; this member of parliament spoke in multiple roles (chair, regular), which means that each statistic is plotted multiple times (once for each role).

__JaroslavFaltynek.1962_interval__: Statistics for a single member of parliament computed over a custom time interval.

__multiple_interval__: Statistics for multiple members of parliament computed over a custom time interval.

We expect there will be a one page with statistics for every member of parliament and one page for comparing multiple members of parliament. It should be clear which example above belongs to which category.

### Notes

What is missing in the examples, what will be added, in general important things to note when looking at the examples:

- the way the data is displayed on a website will probably differ from the way they are displayed here, especially the design might change significantly; however, it is desirable the examples here contain roughly the same data as the website will contain (that is what is plotted, etc.)
- the examples are missing a header with info about the speaker; will be added
- the plots are very rough (speech lengths in milliseconds,...); will make more user-friendly
- there are very little statistics right now; will add more, for example:
  - difference between the speed of speaking throughout the day (not trivial; needs to account for different speakers etc.)
  - compare the statistics between different genders, age groups, parties,...
  - ...
- currently, the statistics for multiple people are visualized only over a particular interval, as opposed to statistics for single person, which have an all-time variant
- we would like to have an example where members of parliament with most extreme values of individual metrics are shown (e.g. five fastest speakers)

