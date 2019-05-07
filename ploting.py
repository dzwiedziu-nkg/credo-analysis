import glob
from itertools import islice, cycle

from math import sin, tan, log, pi, cos
from matplotlib.colors import LogNorm
from pylab import plot, show, plt
from numpy import vstack, array, meshgrid, linspace, logspace, append, unique
from numpy.random import rand
from scipy.cluster.vq import kmeans,vq

# data generation
#data = vstack((rand(150,2) + array([.5,.5]),rand(150,2)))
from sklearn import mixture
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.preprocessing import MinMaxScaler

INDIR = '../output_vector_measure'  # directory with output CSV and PNG files with segmentation marks

# list all CSV files
csvs = glob.iglob(INDIR + '/**/*.csv', recursive=True)

data = []
# loop for each found CSV
uniq = set()
for csv in csvs:
    if '1397' in csv:
        continue
    with open(csv, 'r') as fcsv:
        # loop for reach line in CSV
        for line in fcsv:
            values = line.strip().split('\t')
            if len(values) <= 1:
                continue
            #data.append([float(values[17]), float(values[22])])
            # 17 - ellipticity
            # 22 - solidity
            # 29 - sum of bright
            # 30 - average
            # 28 - brightest pixel
            # 4 - timestamp
            # 20 - marked area
            # 24 - perimeter (pix)
            # 25 - major_axis_length (pix)
            # 26 - minor_axis_length (pix)

            # mval = float(values[4])
            # if mval < 1554854400000:
            #     continue
            #
            # if mval > 1554940800000 + 24 * 60 * 60 * 1000.0:
            #     continue

            # base = 1555718400000.0  # 2019-04-20
            # mmin = base - (7 * 24 * 60 * 60 * 1000.0)
            # mmax = base + (-6 * 24 * 60 * 60 * 1000.0)
            # mval = float(values[4])
            # if mval < mmin: # 1500000000000:
            #     #print(line)
            #     continue
            #
            # if mval > mmax: # 1500000000000:
            #     #print(line)
            #     continue
            #
            # print(mval)

            # if mval in uniq:
            #     print('duplicated: %f' % mval)
            #     continue
            # uniq.add(mval)

            data.append([
                #float(values[4]),# // (1000*60*60),
                #float(values[20]) ** 0.5,
                #sin(float(values[17]) * pi/2)**0.125,
                #cos(float(values[22]) * pi/2)**0.125,
                float(values[17]),
                float(values[22]),
                float(values[29]),
                float(values[30]),
                float(values[28]),
                float(values[20]),
                float(values[24]),
                float(values[25]),
                float(values[26]),
                #1
            ])
    #break

count_of_data = len(data)
print('Danych %d' % count_of_data)
data = array(data) # array(unique(array(data)))

#mms = MinMaxScaler()
#mms.fit(data)
#data = mms.transform(data)

xlabel = 'sin(ellipticity*pi/2)^0.125: 0 - more spot, 1 - more track/worm'
ylabel = 'cos(solidity*pi/2)^0.125: 0 - more spot/track, 1 - more worm'
#xlabel = 'ellipticity: 0 - more spot, 1 - more track/worm'
#ylabel = 'solidity: 0 - more worm, 1 - more spot/track'
title = 'all devices'

if False:
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.scatter(data[:, 0], data[:, 1], s=.1)
    plt.show()

#exit(0)
#data = mms.transform(data)
#
# Sum_of_squared_distances = []
# K = range(1,15)
# for k in K:
#     km = KMeans(n_clusters=k)
#     km = km.fit(data_transformed)
#     Sum_of_squared_distances.append(km.inertia_)
#
# plt.plot(K, Sum_of_squared_distances, 'bx-')
# plt.xlabel('k')
# plt.ylabel('Sum_of_squared_distances')
# plt.title('Elbow Method For Optimal k')
# plt.show()
#
# def aic(X):
#   range_n_clusters = range(1, 15)
#   aic_list = []
#   for n_clusters in range_n_clusters:
#      model = mixture.GaussianMixture(n_components=n_clusters, init_params='kmeans')
#      model.fit(X)
#      aic_list.append(model.aic(X))
#   plt.plot(range_n_clusters, aic_list, marker='o')
#   plt.show()
#
#
# aic(data)

K = range(1, 100)

aics = []
bics = []

for k in K:
    # now with K = 3 (3 clusters)
    #km = KMeans(n_clusters=k)
    #km = km.fit(data_transformed)
    #y_hat = km.predict(data_transformed)
    #p = km.
    #centroids2,_ = kmeans(data,3)
    model = mixture.GaussianMixture(n_components=k, init_params='kmeans', random_state=1)
    model.fit(data)


    idx = model.predict(data)

    #centroids = km.cluster_centers_
    #idx2,_ = vq(data,centroids)
    #idx = km.labels_

    #plt.scatter(data[idx==0,0],data[idx==0,1],'ob',
    #     data[idx==1,0],data[idx==1,1],'or',
    #     data[idx==2,0],data[idx==2,1],'og',
    #     data[idx==3,0],data[idx==3,1],'oy') # third cluster points
    #plot(centroids[:,0],centroids[:,1],'sm',markersize=8)

    aics.append(model.aic(data))
    bics.append(model.bic(data))
    print('Clusters: %d' % k)

    if False:
        # display predicted scores by the model as a contour plot
        # x = linspace(0., 1.)
        # y = linspace(0., 1.)
        # X, Y = meshgrid(x, y)
        # XX = array([X.ravel(), Y.ravel()]).T
        # Z = -model.score_samples(XX)
        # Z = Z.reshape(X.shape)
        #
        # CS = plt.contour(X, Y, Z,
        #                  levels=logspace(0, 3, 10))
        # CB = plt.colorbar(CS, shrink=0.8, extend='both')

        colors = array(list(islice(cycle(['#377eb8', '#ff7f00', '#4daf4a',
                                             '#f781bf', '#a65628', '#984ea3',
                                             '#999999', '#e41a1c', '#dede00']),
                                      int(max(idx) + 1))))
        # add black color for outliers (if any)
        colors = append(colors, ["#000000"])
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title('%s, clusters: %d' % (title, k))
        plt.scatter(data[:, 0], data[:, 1], s=0.1, color=colors[idx])


        #plt.scatter(data[:, 0], data[:, 1], .8)


        show()
        #exit(0)

plot(K, aics, marker='o')
plot(K, bics, marker='x')
plt.title('AIC - o, BIC - x')
show()

aic_min = aics.index(min(aics))
bic_min = bics.index(min(bics))

print(K[aic_min])
print(K[bic_min])
