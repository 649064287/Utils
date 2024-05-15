import os

import cv2
import networkx as nx
import numpy as np

def get_node(edge, pos):
    x1 = int(pos.get(edge[0])[0])
    y1 = int(pos.get(edge[0])[1])
    x2 = int(pos.get(edge[1])[0])
    y2 = int(pos.get(edge[1])[1])
    return x1,y1,x2,y2

root=r"E:\data\zhejiang\p"
out_path=os.path.join(root, 'png')
if not os.path.exists(out_path):
    os.mkdir(out_path)
for name in os.listdir(root):
    if (name.endswith(".p")):
        graph = os.path.join(root, name)
        G = nx.read_gpickle(graph)
        pos = nx.get_node_attributes(G, 'pos')
        blank_mask = np.zeros((128, 128))
        for edge in G.edges:
            x1, y1, x2, y2 = get_node(edge, pos)
            blank_mask = cv2.line(blank_mask, (x1, y1), (x2, y2), color=1, thickness=1)

        # binary
        blank_mask = np.flip(blank_mask, axis=0)
        fusion_binary = blank_mask
        ret, fusion_mask = cv2.threshold(fusion_binary, 0.1, 255, cv2.THRESH_BINARY)
        cv2.imwrite(out_path + "/" + name[:-2] + '.png', fusion_mask)