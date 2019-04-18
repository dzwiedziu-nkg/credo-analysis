# credo-analysis
Data analysis from CREDO project

Methods from this project works on data downloaded via
[credo-api-tools](https://github.com/dzwiedziu-nkg/credo-api-tools).

## Requirements

For running you must have `python3` with package manager and virtual environment like `pip` and `virtualenv`.

Originally running on Python 3.6.

### Prepare to run

```bash
virtualenv -p python3 env
source env/bin/activate
pip install numpy==1.15.2  # fix for build wheel for astropy
pip install -r requirements.txt
```

### Prepare data

Download data from CREDO server via [credo-api-tools](https://github.com/dzwiedziu-nkg/credo-api-tools) 
and copy or link the `credo-api-tools/data-exporter/credo-data-export` dir to `../source_data`.

## server_vector_export script

This script export cosmic-ray hits from JSON file to PNG file and CSV file with other parameters from JSON file.

- Input: `../source_data/detections`
- Output: `../output_vector_server`

### Output format:

- PNG file name format: `{user_id}/{device_id}/{date_time}_{detection_id}.png`
- CSV file name format: `{user_id}/{device_id}.csv`

#### CSV columns:

- [1] PNG file name,
- [2] `id`,
- [3] `user_id`,
- [4] `device_id`,
- [5] `timestamp`,
- [6] `team_id`,
- [7] `width`,
- [8] `height`,
- [9] `x`,
- [10] `y`,
- [11] `latitude`,
- [12] `longitude`,
- [13] `altitude`,
- [14] `accuracy`,
- [15] `provider`,
- [16] `time_received`.


## measure_vector_export script

This script analyse image of cosmic-ray hit and append measured parameters to CSV file.

- Input: `../output_vector_server`
- Output: `../output_vector_measure`

### Output format:

- PNG with marked area file name format: `{user_id}/{device_id}/{date_time}_{detection_id}-segm.png`
- CSV file name format: `{user_id}/{device_id}.csv`

#### New CSV columns:

- [17] nth in image
- [18] ellipticity (0.0-1.0)
- [19] elongation (0.0-1.0)
- [20] eccentricity (0.0-1.0)
- [21] marked area (pix^2)
- [22] convex area (pix^2)
- [23] solidity (div marked per convex)
- [24] orientation (rad)
- [25] perimeter (pix)
- [26] major_axis_length (pix)
- [27] minor_axis_length (pix)
- [28] average background bright (0-255)
- [29] brightest pixel (0-255)
- [30] sum of (bright of pixel minus average background bright)
- [31] average hit bright
