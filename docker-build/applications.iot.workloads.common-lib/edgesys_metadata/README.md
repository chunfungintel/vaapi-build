#
## Introduction
This is edge system project metadata databse (excel files) and the scripts to generate ess configuration files (yaml/json).

## How to Use
Modify the .xlsx filename below by replacing "ABC" with the right project name, e.g. nvr.

### To generate profile sets and workload metadata
```
python3 scripts/workload_yaml_generator.py excel/ABC-metadata.xlsx
```

### To generate kpi target value metadata
```
python3 scripts/kpi_metadata_generator.py excel/ABC-metadata.xlsx
```

### To generate gsteamer elements metadata
```
python3 scripts/element_metadata_generator.py excel/gst-metadata.xlsx
```
