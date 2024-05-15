import cv2
import torch
import numpy as np
import os
import torchvision

c_mean = [0.4914, 0.4822, 0.4465]
c_std = [0.2023, 0.1994, 0.2010]
de_mean = [-mean / std for mean, std in zip(c_mean, c_std)]
de_std = [1 / std for std in c_std]
normalize = torchvision.transforms.Normalize(c_mean, c_std)
denormalize = torchvision.transforms.Normalize(de_mean, de_std)


def ndarray2tensor(img):
    img = cv2.resize(img, (256, 256))
    img = img / 255.
    img = torch.tensor(img, dtype=torch.float32)
    img = img.unsqueeze(0)
    img = img.permute(0, 3, 1, 2)
    img = normalize(img)
    return img


def torch2ndarray_save(input: torch.Tensor, filename, denormal=True):
    assert (len(input.shape) == 4 and input.shape[0] == 1)
    input = input.clone().detach()
    if input.is_cuda == True:
        input = input.to(torch.device('cpu'))
    if denormal:
        input = denormalize(input) * 255
    input = torch.tensor(input, dtype=torch.int)
    img = input.permute(0, 2, 3, 1)
    img = torch.reshape(img, (img.shape[1], img.shape[2], img.shape[3])).numpy()
    cv2.imwrite(filename, img)