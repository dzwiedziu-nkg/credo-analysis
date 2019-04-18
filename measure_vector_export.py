import glob
import pathlib
from os import path
from os.path import join, basename
from shutil import copyfile

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from astropy.stats import gaussian_fwhm_to_sigma
from astropy.convolution import Gaussian2DKernel
from astropy.visualization import SqrtStretch, transform
from astropy.visualization.mpl_normalize import ImageNormalize
from photutils import detect_sources, deblend_sources, source_properties

# Config
from skimage.measure import regionprops

INDIR = '../output_vector_server'  # directory with input CSV and PNG files from server_vector_export script
OUTDIR = '../output_vector_measure'  # directory with output CSV and PNG files with segmentation marks

# list all CSV files
csvs = glob.iglob(INDIR + '/**/*.csv', recursive=True)

# loop for each found CSV
for csv in csvs:
    with open(csv, 'r') as fcsv:
        # loop for reach line in CSV
        for line in fcsv:
            values = line.strip().split('\t')
            if len(values) <= 1:
                continue

            fn = values[0]
            user_id = values[2]
            device_id = values[3]

            filename = join(INDIR, user_id, device_id, fn)
            csvdir = join(OUTDIR, user_id)
            pngdir = join(OUTDIR, user_id, device_id)

            # load PNG and convert to grayscale
            img = Image.open(filename).convert('LA')
            gray, alpha = img.split()  # split array to grayscale and alpha cannel
            data = np.asarray(gray)  # convert to NumPy array
            data = np.flipud(data)  # flip by Y axis (like in screen)

            # find darkness pixel
            brightest = data.max()
            darkest = brightest

            rows = data.shape[0]
            cols = data.shape[1]
            for x in range(0, cols):
                for y in range(0, rows):
                    v = data[y, x]
                    if v:  # skip pixels with 0 bright
                        darkest = min(darkest, v)

            # set threshold as 1/8 in line segment from darkness pixel to brightness
            threshold = np.ones(data.shape) * ((brightest - darkest)/8 + darkest)

            # used parametrs from tutorial for detect_sources
            sigma = 3.0 * gaussian_fwhm_to_sigma    # FWHM = 3.
            kernel = Gaussian2DKernel(sigma, x_size=3, y_size=3)
            kernel.normalize()
            segm = detect_sources(data, threshold, npixels=5, filter_kernel=kernel)

            # notify when not found any hit
            if segm.nlabels == 0:
                print("%s: not found" % filename)
                continue

            # average bright of background
            sum_background = 0
            count_background = 0
            for x in range(0, cols):
                for y in range(0, rows):
                    c = segm.data[y, x]
                    v = data[y, x]
                    if v and not c:  # skip pixels with 0 bright
                        sum_background += v
                        count_background += 1
            background_bright = sum_background / count_background if count_background else 0

            # rozdzielenie znalezionych obiektów jednych od drugich, parametry jak w tutorialu poza npixels=200,
            # który trzeba było zwiększyć bo niepotrzebnie dzielił na kawałki długie hity, dzięki temu nie dzieli i nie odbiło
            # się to niegatywnie na wyraźnie osobnych hitach na jednym PNG
            segm_deblend = deblend_sources(data, segm, npixels=200, filter_kernel=kernel, nlevels=32, contrast=0.001)

            # analiza znalezionych obiektów (powierzchnia, eliptyczność itd.)
            cat = source_properties(segm, segm_deblend)

            # zapis wyników na dysku
            fn = filename.split("/")[-1]  # wyciągnięcie nazwy pliku PNG
            group = filename.split("/")[-2]  # wycięgnięcie podkatalogu, w którym znajduje się PNG
            # output_dir2 = join(OUTDIR, ) OUTDIR + 'detections/%s' % group  # tu zostaną wrzucone pliki
            pathlib.Path(pngdir).mkdir(parents=True, exist_ok=True)  # jeżeli to konieczne to utworzenie podkatalogów

            nth = 0
            for obj in cat:
                nth += 1
                brightest_obj = 0
                brigh_obj_sum = 0
                brightest_obj_sum = 0
                brightest_obj_count = 0

                for x in range(0, int(obj.xmax.value - obj.xmin.value + 1)):
                    for y in range(0, int(obj.ymax.value - obj.ymin.value + 1)):
                        c = obj.data_cutout[y, x]
                        v = data[int(obj.ymin.value + y), int(obj.xmin.value + x)]
                        if c:
                            brightest_obj = max(v, brightest_obj)
                            brightest_obj_sum += v
                            brightest_obj_count += 1
                            brigh_obj_sum += v - background_bright

                brightest_obj_avg = brightest_obj_sum / brightest_obj_count

                try:
                    another_props = regionprops(obj.data_cutout)[0]
                except:
                    print("%s: skip because: %d x %d" % (filename, int(obj.xmax.value - obj.xmin.value + 1), int(obj.ymax.value - obj.ymin.value + 1)))
                    continue

                # nazwa pliku oryginalnego
                # fn_out = output_dir2 + '/%.3f-%d-%s' % (obj.ellipticity.value, obj.area.value, fn)

                # nazwa pliku z wynikiem detect_sources
                # fn_sefm = output_dir2 + '/%.3f-%d-%s-segm.png' % (obj.ellipticity.value, obj.area.value, fn.replace(".png", ""))

                # wyciągnięcie parametrów z nazwy pliku PNG aby umieścić je w CSV
                # srcs = "; ".join(filename.split(".")[0].split("_"))

                # source_sum = obj.source_sum
                # print(obj.source_sum)
                # print (obj.source_sum.value)

                # wiersz CSV:
                # eliptyczność, elongacja, ekscentryczność, powierzchnia, [dane z PNG oddzielone "_"], plik wejściowy, plik wyjściowy

                nvalues = values.copy()
                nvalues.append(str(nth))
                nvalues.append(str(obj.ellipticity.value))
                nvalues.append(str(obj.elongation.value))
                nvalues.append(str(obj.eccentricity.value))
                nvalues.append(str(obj.area.value))
                nvalues.append(str(another_props.convex_area))
                nvalues.append(str(another_props.solidity))
                nvalues.append(str(obj.orientation.value))
                nvalues.append(str(obj.perimeter.value))
                nvalues.append(str(another_props.major_axis_length))
                nvalues.append(str(another_props.minor_axis_length))

                nvalues.append(str(background_bright))
                nvalues.append(str(brightest_obj))
                nvalues.append(str(brigh_obj_sum))
                nvalues.append(str(brightest_obj_avg))
                # nvalues.append(str(obj.source_sum.value))


                # print('%f; %f; %f; %d; %s; %s; %s;' % (obj.ellipticity.value, obj.elongation.value, obj.eccentricity.value, obj.area.value, srcs, filename, fn_out))

                # kopiowanie pliku wejściowego pod nazwę wyjściową
                # copyfile(filename, fn_out)

                # zapis pliku z wynikiem zamarkowania detect_sources
                pngfn = join(pngdir, fn.replace('.png', '-segm.png'))
                plt.imsave(pngfn, segm_deblend, origin='lower', cmap=segm_deblend.cmap(random_state=12345))

                # append to CSV file
                csv = join(csvdir, '%s-segm.csv' % str(device_id))
                with open(csv, "a") as fcsv:
                    fcsv.write('%s\n' % '\t'.join(nvalues))

            # if segm.nlabels > 1:
            #     #norm = ImageNormalize(stretch=SqrtStretch())
            #     fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12.5))
            #     #ax1.imshow(img) # , origin='lower', cmap='Greys_r', norm=norm
            #     ax1.imshow(data, origin='lower', cmap='Greys_r')
            #     ax1.set_title('Data')
            #     ax2.imshow(segm_deblend, origin='lower', cmap=segm_deblend.cmap(random_state=12345))
            #     ax2.set_title('Segmentation Image')
            #     plt.tight_layout()
            #     plt.show()
            #     break


