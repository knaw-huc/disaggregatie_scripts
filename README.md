# Disaggregatie scripts

Use:

```python integrate.py -c configfile -i inputdir -o outputfile```

Add an extra `-d` to get lots of debug output.

Example config file:
```{
    "inputdir" : "inputdir",
    "outputfile" : "output.xlsx",
    "surface_file" : "surface_file.txt",
    "links_file" : "links_file.txt",
    "census_files" : "census_*.txt"
}```

`census_files` is given as a matching pattern.

`inputdir` and `outputfile` can be left out and given on the prompt (after `-i` and `-o`).

