# credo-analysis
Data analysis from CREDO project

Methods from this project works on data downloaded via
[credo-api-tools](https://github.com/dzwiedziu-nkg/credo-api-tools).

## Requirements

For running you must have `python3` with package manager and virtual environment like `pip` and `virtualenv`.


### Prepare to run

```bash
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```

### Prepare data

Download data from CREDO server via [credo-api-tools](https://github.com/dzwiedziu-nkg/credo-api-tools) 
and copy or link the `credo-api-tools/data-exporter/credo-data-export` dir to `../source_data`.

## server_vector_export

This script export cosmic-ray hits from JSON file to PNG file and CSV file with other parameters from JSON file.

- Input: `../source_data/detections`
- Output: `../output_vector_server`

### Output format:

- PNG file name format: `{user_id}/{device_id}/{date_time}_{detection_id}.png`
- CSV file name format: `{user_id}/{device_id}.csv`

#### CSV columns:

- PNG file name,
- `id`,
- `user_id`,
- `device_id`,
- `timestamp`,
- `team_id`,
- `width`,
- `height`,
- `x`,
- `y`,
- `latitude`,
- `longitude`,
- `altitude`,
- `accuracy`,
- `provider`,
- `time_received`.
