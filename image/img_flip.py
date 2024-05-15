import cv2


img = cv2.imread('0000000004_proj_sg.png', cv2.IMREAD_COLOR)
imgflip = cv2.flip(img, 0)#延x轴翻转
cv2.imwrite('4.png', imgflip, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])