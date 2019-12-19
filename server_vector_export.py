"""
Export detections data from JSON file from credo-data-exporter.py to separated PNG files with format name:
OUTDIR/{user_id}/{device_id}/{date_time}_{detection_id}_[...}.png

Before run please check config: INDIR and OUTDIR consts
"""
import base64
from datetime import datetime
from os import listdir, makedirs
from os.path import join

import ijson

# Config
INDIR = '../source_data/detections'  # directory with input JSON files
OUTDIR = '../output_vector_server'  # directory with output PNG files

# values from JSON to export to CSV
VALUES = [
    # PNG file name
    'id',
    'user_id',
    'device_id',
    'timestamp',
    'team_id',
    'width',
    'height',
    'x',
    'y',
    'latitude',
    'longitude',
    'altitude',
    'accuracy',
    'provider',
    #'source',
    'time_received',
    #'visible'
]

# Collect all *.json files from input directory
jsons = [f for f in listdir(INDIR) if f.endswith('.json')]

# Progress runtime: stats
i = 0
count = len(jsons)

# Loop for export cosmic-ray hits to PNG files
for fn in sorted(jsons):
    i += 1
    print('Open file: %s (%d of %d)...' % (fn, i, count))

    f = join(INDIR, fn)
    with open(f, 'r') as json:
        # Load JSON file
        objects = ijson.items(json, 'detections.item')

        j = 0

        # Loop for each detection in loaded JSON file
        for o in objects:

            # Progress runtime: proceed each 10.000 detections
            j += 1
            if j % 10000 == 0:
                print('...processed %d hits' % j)

            hit_id = o.get('id')
            user_id = o.get('user_id')
            device_id = o.get('device_id')
            frame_content = o.get('frame_content')
            timestamp = o.get('timestamp')
            dt = datetime.fromtimestamp(timestamp / 1000)

            # make output directory for file if not exists
            outdir = join(OUTDIR, str(user_id), str(device_id))
            csvdir = join(OUTDIR, str(user_id))
            makedirs(outdir, exist_ok=True)

            format_dt = '%d_%02d_%02d_%02d_%02d_%02d' % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            file_name = '%s_%s.png' % (format_dt, str(hit_id))

            # extract columns from JSON
            values = [file_name]
            for v in VALUES:
                values.append(str(o.get(v)))
            #file_name = '%s_%s.png' % (format_dt, '_'.join(values))

            # write PNG file
            fn = join(outdir, file_name)
            with open(fn, 'wb') as f:
                if frame_content is None:
                    print('Hit with ID: %s is without PNG image' % str(hit_id))
                else:
                    f.write(base64.b64decode(frame_content))

            # append to CSV file
            csv = join(csvdir, '%s.csv' % str(device_id))
            with open(csv, "a") as fcsv:
                fcsv.write('%s\n' % '\t'.join(values))

        print('...finish of %s, processed %d hits' % (fn, j))
