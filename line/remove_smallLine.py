import numpy as np
from skan import csr
from skimage import io, morphology
import cv2

# loading image
image = io.imread(r'C:\App\Python\utils\line\sample_0_line.png')

# make image binary
image_binary = image >= 200

# skeletonize; the skeleton is marked as True the other areas as False
sk = morphology.skeletonize(image_binary).astype(bool)

# object for all properties of the graph
graph_class = csr.Skeleton(sk)

# get statistics for each branch, especially relevant the length and type of branch here
stats = csr.branch_statistics(graph_class.graph)

# remove all branches which are shorter than the threshold value and a tip-junction (endpoint to junction) branch
thres_min_size = 10
for ii in range(np.size(stats, axis=0)):
    if stats[ii,2] < thres_min_size and stats[ii,3] == 1:
        # remove the branch
        for jj in range(np.size(graph_class.path_coordinates(ii), axis=0)):
            sk[int(graph_class.path_coordinates(ii)[jj,0]), int(graph_class.path_coordinates(ii)[jj,1])] = False

# during the short branch removing process it can happen that some branches are not longer connected as the complete three branches intersection is removed
# therefor the remaining skeleton is dilatated and then skeletonized again
sk_dilation = morphology.binary_dilation(sk)
sk_final = morphology.skeletonize(sk_dilation)

# optional checks if everything worked like expected
graph_class2 = csr.Skeleton(sk_final)
stats2 = csr.branch_statistics(graph_class2.graph)

cv2.imwrite(r"C:\App\Python\utils\line\out.png", sk_final.astype(np.uint8)*255)