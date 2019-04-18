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
INDIR = '../output_vector_server'  # directory with input CSV and PNG files from server_vector_export script
OUTDIR = '../output_vector_ellipse'  # directory with output CSV and PNG files with segmentation marks

# wszystkie pliki PNG w katalogu "png/" z uwzględnieniem podkatalogów
csvs = glob.iglob(INDIR + '/**/*.csv', recursive=True)

for csv in csvs:
    with open(csv, 'r') as fcsv:
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

            # wczytanie pliku PNG z konwersją do grayscale
            img = Image.open(filename).convert('LA')
            gray, alpha = img.split()  # oddzielenie kanały grayscale od alpha
            data = np.asarray(gray)  # konwersja do tablicy NumPy
            data = np.flipud(data)  # lustrzane odbicie tablicy w pionie by była taka sama jak w pliku PNG

            # próg detekcji ustalany jako 1/8 w drodze od najciemniejszego do najjaśniejszego pixela, dobrane eksperymentalnie
            # prór można ustalić osobny dla każdego piksela, tutaj wszystkie maja jeden próg
            threshold = np.ones(data.shape) * ((data.max() - data.min())/8 + data.min())

            # parametry dla detect_sources z tutoriala, detect_sources - wyszukuje obiektów gwiazdowych i mgławicowych
            sigma = 3.0 * gaussian_fwhm_to_sigma    # FWHM = 3.
            kernel = Gaussian2DKernel(sigma, x_size=3, y_size=3)
            kernel.normalize()
            segm = detect_sources(data, threshold, npixels=5, filter_kernel=kernel)

            # jeżeli nic nie znaleziono, dalsze przetwarzanie nie ma sensu. Jeżeli nic nie znaleziono to może być zbyt wysoki
            # próg detekcji
            if segm.nlabels == 0:
                print("%s: no found" % filename)
                continue

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
                nvalues.append(str(obj.orientation.value))
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


