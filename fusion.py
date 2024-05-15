import os

import cv2
import networkx as nx
import numpy
import numpy as np
import skimage
from matplotlib import pyplot as plt
from skimage import morphology
from sknw import sknw
from tqdm import tqdm
# import skeleton
from skan import csr
import mapextract as mpe

topo_array = []
ratio_array = []
log_name="yantian"
mylog = open(r'C:\App\Python\utils' + log_name + '.log', 'w')

def get_node(edge, pos):
    x1 = int(pos.get(edge[0])[0])
    y1 = int(pos.get(edge[0])[1])
    x2 = int(pos.get(edge[1])[0])
    y2 = int(pos.get(edge[1])[1])
    return x1,y1,x2,y2

def is_connected(edge, mask, pos):
    x1,y1,x2,y2=get_node(edge, pos)
    # centerline
    empty = np.zeros((128, 128))
    empty = cv2.line(empty, (x1, y1), (x2, y2), color=1, thickness=1)
    empty = np.flip(empty, axis=0)

    kernels = np.ones((2, 2))
    dilated = cv2.dilate(empty, kernels)

    im = morphology.thin(mask)
    thin_mask = im.astype(np.uint8)

    edge_length = np.sum(dilated[empty>0])
    pred_length = np.sum(dilated[thin_mask > 0])

    if pred_length < edge_length/2.0:
        return False, empty
    else:
        return True, empty


def fusion_yt(root, pname, maskname, label):

    mask_path=root+"/"+maskname
    label=root+"/"+label
    graymask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    thresh, mask=cv2.threshold(graymask, 0, 255, cv2.THRESH_OTSU)
    mask1=mask/255.0

    label = cv2.imread(label, cv2.IMREAD_GRAYSCALE)
    path = root + "/" + pname
    G = nx.read_gpickle(path)
    pos = nx.get_node_attributes(G, 'pos')
    blank_mask=np.zeros((128,128))
    for edge in G.edges:
        # print(edge)
        # print(pos.get(edge[0]), pos.get(edge[1]))
        flag, edge_mask=is_connected(edge, mask1, pos)
        if not flag:
            # print(pname)
            kernels = np.ones((3, 3))
            dilated_edge_mask = cv2.dilate(edge_mask, kernels)  # buffer
            # width=area/length
            area = np.sum(mask1[dilated_edge_mask > 0])
            length = np.sum(edge_mask * mask1)
            if area > 0 and length > 0:
                adap_width = area / (length)
                if adap_width > 3:
                    adap_width = 3
                if adap_width<=1:
                    adap_width = 1
                x1, y1, x2, y2 = get_node(edge, pos)
                blank_mask = cv2.line(blank_mask, (x1,y1), (x2,y2), color=1, thickness=3)

    #binary
    blank_mask=np.flip(blank_mask, axis=0)
    fusion_binary = blank_mask + mask1
    ret, fusion_mask = cv2.threshold(fusion_binary, thresh, 255, cv2.THRESH_BINARY)
    cv2.imwrite(root + "/" + pname[:-4] + "_fusion.png", fusion_mask)

    #gray
    # kernels = np.ones((3, 3))
    # blank_mask=cv2.dilate(blank_mask, kernels)
    # for i in range(blank_mask.shape[0]):
    #     for j in range(blank_mask.shape[1]):
    #         if blank_mask[i,j]>0:
    #             if graymask[i,j]>thresh/2:
    #                 graymask[i, j] = thresh
                # if graymask[i,j]<thresh/1.5 and graymask[i,j]>=thresh/1.8:
                #     graymask[i, j] += thresh/1.5
                # else:
                #     graymask[i, j] += thresh / 2

    cv2.imwrite(root + "/" + pname[:-4] + "_gray.png", graymask)
    th, binary_mask = cv2.threshold(graymask, 50, 255, cv2.THRESH_BINARY)
    # graymask=extend_line(binary_mask, graymask, 128, 128, th)
    line=thin_image(binary_mask)
    # cv2.imwrite(root + "/" + pname[:-4] + "_line.png", line)
    # topo(line, label)

    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    ax[0].imshow(line)
    ax[0].axis('off')

    print(pname)
    L = mpe.trans2graph(line)
    G2=nx.Graph(L)
    for n in G2.nodes:
        G2.nodes[n]['pos']=(n[0], 128-n[1])

    for u, v in G2.edges:
        G2.add_edge(u, v, weight=mpe.distance(u, v))
    print(G2.edges(data=True))

    for u,v in G.edges:
        p1 = (int(G.nodes[u]['pos'][0]), int(G.nodes[u]['pos'][1]))
        p2 = (int(G.nodes[v]['pos'][0]), int(G.nodes[v]['pos'][1]))

        min1=min2=9999
        n1=p1
        n2=p2
        for n in G2.nodes:
            n_pos=(n[0], 128-n[1])
            dis1 = mpe.distance(n_pos, p1)
            dis2 = mpe.distance(n_pos, p2)
            if dis1<min1:
                n1=n
                min1=dis1
            if dis2<min2:
                n2=n
                min2=dis2

        if min1>20 or min2>20:
            continue
        # if min1>20:
        #     n1=p1
        #     G2.add_node(n1)
        #     G2.nodes[n1]['pos'] = n1
        # if min2>20:
        #     n2=p2
        #     G2.add_node(n2)
        #     G2.nodes[n2]['pos'] = n2

        print(nx.has_path(G2, n1, n2))
        if not nx.has_path(G2, n1, n2):
            print(nx.node_connected_component(G2, n1))
            print("--------------")
            print(nx.node_connected_component(G2, n2))

            stand_node1=[]
            stand_node2=[]
            MIN_DIS=9999
            for k in nx.node_connected_component(G2, n1):
                pos1 = G2.nodes[k]['pos']
                for n in nx.node_connected_component(G2, n2):
                    pos2 = G2.nodes[n]['pos']
                    dis=mpe.distance(pos1, pos2)
                    if dis < MIN_DIS:
                        MIN_DIS=dis
                        stand_node2.append(k)
                        stand_node1.append(n)
            node1=stand_node1.pop()
            node2=stand_node2.pop()

            node_list=[]
            node_list.append(node1)
            node_list.append(node2)
            bound_count=0
            for node in node_list:
                if node[0]-5<0 or node[0]+5>128 or node[1]-5<0 or node[1]+5>128:
                    bound_count+=1

            if G2.degree[node1]==1 and G2.degree[node2]==1 and bound_count!=2:
                G2.add_edge(node1, node2, weight=mpe.distance(node1, node2))

            # boundary
            border_nodes2 = np.array(
                [[-1, 0], [-1, 128], [128, 128], [128, 0]])  # bottomleft topleft topright bottomright
            border_edges2 = [(0, 1), (1, 2), (2, 3), (3, 0)]
            g = nx.Graph()
            g.add_nodes_from(list(range(len(border_nodes2))))
            coord_dict = {}
            tmp = [coord_dict.update({i: (pts[1], pts[0])}) for i, pts in enumerate(border_nodes2)]
            for n, p in coord_dict.items():
                g.nodes[n]['pos'] = p
            g.add_edges_from(border_edges2)
            pos = nx.get_node_attributes(g, 'pos')

            nx.draw(g, pos, ax=ax[1], node_size=1, node_color='darkgrey', edge_color='darkgrey', width=1.5, font_size=12,
                    with_labels=False)

            options ={
                'node_color': 'red',
                'edge_color': 'black',
                'node_size' : 3,
                'width': 1
            }
            pos=nx.get_node_attributes(G2, 'pos')
            nx.draw(G2, pos=pos, ax=ax[1], **options)
            # plt.show()
            plt.savefig(root + "/" + pname[:-4] + "_g2.png")

    line_mask = np.zeros((128, 128))
    pos = nx.get_node_attributes(G2, 'pos')
    for edge in G2.edges:
        x1, y1, x2, y2 = get_node(edge, pos)
        line_mask = cv2.line(line_mask, (x1, y1), (x2, y2), color=1, thickness=1)

    line_mask = np.flip(line_mask, axis=0)
    th, line_mask=cv2.threshold(line_mask, 0.1, 255, cv2.THRESH_BINARY)
    cv2.imwrite(root + "/" + pname[:-4] + "_line.png", line_mask.astype(np.uint8))
    topo(line_mask.astype(np.uint8), label)



    # fig, ax = plt.subplots(1, 3, figsize=(15,5))# lab, seg, fusion
    # ax[0].imshow(label, cmap="gray")
    # ax[0].axis('off')
    # ax[1].imshow(mask1*255, cmap="gray")
    # ax[1].axis('off')
    # ax[2].imshow(fusion_mask, cmap="gray")
    # ax[2].axis('off')
    # plt.savefig(root+"/"+pname[:-4]+"_3.png", facecolor="black")
    # plt.close()


def remove_line(image):
    th, image=cv2.threshold(image, 0.1, 255, cv2.THRESH_BINARY)
    # make image binary
    image_binary = image >= 200

    # skeletonize; the skeleton is marked as True the other areas as False
    sk = morphology.skeletonize(image_binary).astype(bool)

    # object for all properties of the graph
    graph_class = csr.Skeleton(sk)

    # get statistics for each branch, especially relevant the length and type of branch here
    stats = csr.branch_statistics(graph_class.graph)

    # remove all branches which are shorter than the threshold value and a tip-junction (endpoint to junction) branch
    thres_min_size = 5
    for ii in range(np.size(stats, axis=0)):
        if stats[ii, 2] < thres_min_size and stats[ii, 3] == 1:
            # remove the branch
            for jj in range(np.size(graph_class.path_coordinates(ii), axis=0)):
                sk[int(graph_class.path_coordinates(ii)[jj, 0]), int(graph_class.path_coordinates(ii)[jj, 1])] = False

    # during the short branch removing process it can happen that some branches are not longer connected as the complete three branches intersection is removed
    # therefor the remaining skeleton is dilatated and then skeletonized again
    sk_dilation = morphology.binary_dilation(sk)
    sk_final = morphology.skeletonize(sk_dilation)

    # optional checks if everything worked like expected
    graph_class2 = csr.Skeleton(sk_final)
    stats2 = csr.branch_statistics(graph_class2.graph)

    return  sk_final.astype(np.uint8)*255

def extend_line(binary_image, edgeStrength, width, height, thresh):
    # th, edgeStrength = cv2.threshold(edgeStrength, 50, 255, cv2.THRESH_TRUNC)
    th2, edgeStrength = cv2.threshold(edgeStrength.astype(np.uint8), 0, thresh, cv2.THRESH_TOZERO)  # 向下截断

    for j in range(1, height-1):
        for i in range(1, width-1):
            if binary_image[j][i] == 0:
                continue
            p2 = binary_image[j][i - 1] > thresh
            p6 = binary_image[j][i + 1] > thresh

            p9 = binary_image[j-1][i - 1] > thresh
            p8 = binary_image[j-1][i] > thresh
            p7 = binary_image[j-1][i + 1] > thresh

            p3 = binary_image[j+1][i - 1] > thresh
            p4 = binary_image[j+1][i] > thresh
            p5 = binary_image[j+1][i + 1] > thresh

            if p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9 < 1:
                continue
            elif p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9 >= 2:
                continue
            if (p3 > p2) + (p4 > p3) + (p5 > p4) + (p6 > p5) + (p7 > p6) + (p8 > p7) + (p9 > p8) + (p2 > p9) > 1:
                continue

            e2 = edgeStrength[j][i - 1]
            e6 = edgeStrength[j][i + 1]

            e9 = edgeStrength[j-1][i - 1]
            e8 = edgeStrength[j-1][i]
            e7 = edgeStrength[j-1][i + 1]

            e3 = edgeStrength[j+1][i - 1]
            e4 = edgeStrength[j+1][i]
            e5 = edgeStrength[j+1][i + 1]

            if p2 and (e5 > 0 or e6 > 0 or e7 > 0):

                if e6 >= e5 and e6 >= e7:
                    binary_image[j][i + 1] = 1
                elif e7 >= e5 and e7 >= e6:
                    binary_image[j-1][i + 1] = 1
                else:
                    binary_image[j+1][i + 1] = 1

            if p3 and (e6 > 0 or e7 > 0 or e8 > 0):
                if e7 >= e6 and e7 >= e8:
                    binary_image[j-1][i + 1] = 1
                elif e6 >= e7 and e6 >= e8:
                    binary_image[j][i + 1] = 1
                else:
                    binary_image[j-1][i] = 1

            if p4 and (e7 > 0 or e8 > 0 or e9 > 0):

                if e8 >= e7 and e8 >= e9:
                    binary_image[j-1][i] = 1
                elif e7 >= e9 and e7 >= e8:
                    binary_image[j-1][i + 1] = 1
                else:
                    binary_image[j-1][i - 1] = 1

            if p5 and (e2 > 0 or e8 > 0 or e9 > 0):

                if e9 >= e2 and e9 >= e8:
                    binary_image[j-1][i - 1] = 1
                elif e2 >= e8 and e2 >= e9:
                    binary_image[j][i - 1] = 1
                else:
                    binary_image[j-1][i] = 1

            if p6 and (e2 > 0 or e9 > 0 or e3 > 0):

                if e2 >= e3 and e2 >= e9:
                    binary_image[j][i - 1] = 1
                elif e3 >= e2 and e3 >= e9:
                    binary_image[j + 1][i - 1] = 1
                else:
                    binary_image[j - 1][i - 1] = 1

            if p7 and (e2 > 0 and e4 > 0 and e3 > 0):

                if e3 >= e2 and e3 >= e4:
                    binary_image[j + 1][i - 1] = 1
                elif e2 >= e4 and e2 >= e3:
                    binary_image[j][i - 1] = 1
                else:
                    binary_image[j + 1][i] = 1

            if p8 and (e4 > 0 or e5 > 0 or e3 > 0):

                if e4 >= e5 and e4 >= e3:
                    binary_image[j+1][i] = 1
                elif e5 >= e4 and e5 >= e3:
                    binary_image[j+1][i + 1] = 1
                else:
                    binary_image[j + 1][i - 1] = 1

            if p9 and (e6 > 0 or e5 > 0 or e4 > 0):

                if e5 >= e6 and e5 >= e4:
                    binary_image[j + 1][i + 1] = 1
                elif e6 >= e5 and e6 >= e4:
                    binary_image[j][i + 1] = 1
                else:
                    binary_image[j + 1][i] = 1
    return binary_image

def thin_image(mask):
    th, line = cv2.threshold(mask, 0.1, 255, cv2.THRESH_BINARY)
    # selem = morphology.disk(1)
    # line = morphology.binary_dilation(line, selem)
    im = skimage.morphology.thin(line)
    return im.astype(np.uint8)*255


def topo(mask, label):
    """
    prediction
    label
    """

    imgp = mask
    imgl = thin_image(label)

    WIDTH=imgl.shape[0]
    HIGTH=imgl.shape[1]
    tp = 0
    fn = 0
    fp = 0
    tn = 0

    kernel3=np.ones((7,7), np.uint8)
    imgl=cv2.dilate(imgl, kernel3)
    imgp=cv2.dilate(imgp, kernel3)

    for i in range(WIDTH):
        for j in range(HIGTH):
            if imgp[i, j] == 255 and imgl[i, j] == 255:
                tp = tp + 1
            elif imgl[i, j] == 255 and imgp[i, j] == 0:
                fn = fn + 1
            elif imgl[i, j] == 0 and imgp[i, j] == 255:
                fp = fp + 1
            elif imgl[i, j] == 0 and imgp[i, j] == 0:
                tn = tn + 1
    topo_array.append((tp, fn, fp, tn))

def result_topo(topo_array):
    TP = 0
    FN = 0
    FP = 0
    TN = 0

    for tp, fn, fp, tn in topo_array:
        TP += tp
        FN += fn
        FP += fp
        TN += tn

    zq = (int(TN) + int(TP)) / (int(TP) + int(TN) + int(FP) + int(FN))
    # 精确率
    jq = int(TP) / (int(TP) + int(FP))
    # 召回率
    zh = int(TP) / (int(TP) + int(FN))
    # F1
    f1 = int(TP) * 2 / (int(TP) * 2 + int(FN) + int(FP))
    # IOU
    IOU = int(TP) / (int(TP) + int(FP) + int(FN))

    print('Accuracy：' + str(zq))
    print('Precision：' + str(jq))
    print('Recall：' + str(zh))
    print('F1：' + str(f1))
    print('IOU：' + str(IOU))

    print('Accuracy：' + str(zq), file=mylog)
    print('Precision：' + str(jq), file=mylog)
    print('Recall：' + str(zh), file=mylog)
    print('F1：' + str(f1), file=mylog)
    print('IOU：' + str(IOU), file=mylog)

def eval_conn(root, line_path, plabel):
    mask=cv2.imread(root + "/" + line_path, cv2.IMREAD_GRAYSCALE)
    mask=mask/255
    kernel3 = np.ones((7, 7), np.uint8)
    mask = cv2.dilate(mask, kernel3)

    path = root + "/" + plabel
    G = nx.read_gpickle(path)
    pos = nx.get_node_attributes(G, 'pos')

    patch_gt_number = 0
    patch_connected_number = 0
    patch_not_connected_number = 0

    patch_connected_length = 0
    patch_gt_length = 0

    for edge in G.edges:
        patch_gt_number += 1
        x1, y1, x2, y2 = get_node(edge, pos)
        #label
        base_gt_mask=np.zeros((128,128))
        base_gt_mask = cv2.line(base_gt_mask, (x1,y1), (x2,y2), color=1,thickness=1)
        base_gt_mask = np.flip(base_gt_mask, axis=0)
        #pred
        pred_seg_length = np.sum(mask[base_gt_mask > 0])

        gt_length = np.sum(base_gt_mask > 0)
        patch_gt_length += gt_length

        # connected or not
        if pred_seg_length < gt_length:
            patch_not_connected_number += 1
        else:
            patch_connected_number += 1
            patch_connected_length += gt_length

    im = (mask * 255) > 128
    selem = morphology.disk(7)
    im = morphology.binary_dilation(im, selem)
    im = morphology.thin(im)
    thin_mask = im.astype(np.uint8) * 255

    patch_pred_length = np.sum(thin_mask > 0)

    patch_pred_number = patch_pred_length / 20.0  # number of segments on the prediction graph

    ratio_array.append((patch_gt_number, patch_connected_number, patch_not_connected_number, patch_pred_number, patch_connected_length, patch_gt_length, patch_pred_length))




def result_ratio(ratio):
    total_gt_number = 0
    total_connected_number = 0
    total_not_connected_number = 0
    total_pred_number = 0

    total_connected_length = 0
    total_gt_length = 0
    total_pred_length = 0

    for patch_gt_number, patch_connected_number, patch_not_connected_number, patch_pred_number, patch_connected_length, patch_gt_length, patch_pred_length in ratio:
        total_gt_number += patch_gt_number
        total_connected_number += patch_connected_number
        total_not_connected_number += patch_not_connected_number
        total_pred_number += patch_pred_number

        total_connected_length += patch_connected_length
        total_gt_length += patch_gt_length
        total_pred_length += patch_pred_length

    # total_ratio = 2*total_connected_number/(total_gt_number+total_pred_number)
    total_ratio = 2 * total_connected_length / (total_gt_length + total_pred_length)

    print('********************************')
    print("total connected:not:total {}/{}/{}, ratio: {}".format(total_connected_number,
                                                                 total_not_connected_number,
                                                                 total_gt_number,
                                                                 round(total_ratio, 4)))
    print("total_gt_length:{}".format(total_gt_length))
    print("average gt length:{}".format(total_gt_length / total_gt_number))

    print('********************************', file=mylog)
    print("total connected:not:total {}/{}/{}, ratio: {}".format(total_connected_number,
                                                                 total_not_connected_number,
                                                                 total_gt_number,
                                                                 round(total_ratio, 4)),
          file=mylog)
    print("total_gt_length:{}".format(total_gt_length), file=mylog)
    print("average gt length:{}".format(total_gt_length / total_gt_number), file=mylog)

def ske(root, mask, label):
    graymask = cv2.imread(root + "/" + mask, cv2.IMREAD_GRAYSCALE)
    th, binary_mask = cv2.threshold(graymask, 50, 255, cv2.THRESH_BINARY)
    # print(th)
    # line2 = extend_line(binary_mask, graymask, 128, 128, th)
    # ret, line2 = cv2.threshold(line2, 0, 255, cv2.THRESH_BINARY)
    line2 = thin_image(binary_mask)
    # line2=remove_line(line2)
    L = mpe.trans2graph(line2)
    G2 = nx.Graph(L)
    for n in G2.nodes:
        G2.nodes[n]['pos']=(n[0], 128-n[1])
    line_mask = np.zeros((128, 128))
    pos = nx.get_node_attributes(G2, 'pos')
    for edge in G2.edges:
        x1, y1, x2, y2 = get_node(edge, pos)
        line_mask = cv2.line(line_mask, (x1, y1), (x2, y2), color=1, thickness=1)

    line_mask = np.flip(line_mask, axis=0)
    th, line_mask = cv2.threshold(line_mask, 0.1, 255, cv2.THRESH_BINARY)

    cv2.imwrite(root + "/" + pname[:-4] + "_line2.png", line_mask)
    label = cv2.imread(root + "/" + label, cv2.IMREAD_GRAYSCALE)
    topo(line_mask, label)

if __name__ == '__main__':
    root=r"C:\Users\lry\Desktop\fsdownload\sample"
    print("start testing...")
    for pname in tqdm(os.listdir(root)):
        if(pname.endswith("_g.p")):
            mask=pname[:-4]+"_res.png"
            label=pname[:-4]+"_lab.png"

            fusion_yt(root, pname, mask, label)
            # ske(root, mask, label)

            plabel = pname[:-4] + "_lab.p"
            fusion=pname[:-4] + "_fusion.png"
            line = pname[:-4] + "_line.png"
            line2 = pname[:-4] + "_line2.png"

            eval_conn(root, line, plabel)
            # eval_conn(root, line2, plabel)

    result_topo(topo_array)
    result_ratio(ratio_array)



