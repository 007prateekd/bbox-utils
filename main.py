import math
import random
import numpy as np
import cv2
from PIL import Image


def imshow(img, title=""):
    cv2.imshow(title, img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def cv2_to_PIL(img):
    img = cv2.cv2tColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    return img


def PIL_to_cv2(img):
    img = np.array(img) 
    if len(img.shape) == 3:
        img = img[:, :, ::-1].copy() 
    return img


def get_mask(image):
    image = PIL_to_cv2(image)
    gray = cv2.cv2tColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    mask = np.zeros(gray.shape, np.uint8)
    mask = cv2.fillPoly(mask, pts=[contours[-1]], color=(255, 255, 255))
    rect = cv2.minAreaRect(contours[-1])
    box = np.int0(cv2.boxPoints(rect))
    return mask, box


def scale_relative(image, pts, qf):
    h, w = image.size
    image.thumbnail(size=(h / qf, w / qf))
    for i in range(len(pts)):
        pts[i][0] /= qf
        pts[i][1] /= qf
    return image, pts


def rotate(image, pts, rot_angle): 
    w, h = image.size
    image = image.rotate(
        rot_angle,
        fillcolor=(0, 0, 0)
    )
    pts_new = []
    x0, y0 = image.size[0] / 2, image.size[1] / 2
    for i in range(4):
        x, y = pts[i]
        theta = (math.pi / 180) * (360 - rot_angle)
        x_ = x * math.cos(theta) - y * math.sin(theta) + x0 * (1 - math.cos(theta)) + y0 * math.sin(theta) + (w / 2 - x0)
        y_ = y * math.cos(theta) + x * math.sin(theta) + y0 * (1 - math.cos(theta)) - x0 * math.sin(theta) + (h / 2 - y0)
        pts_new.append([x_, y_])
    return image, pts_new


def warp(image, pts):
    image = PIL_to_cv2(image)
    pts_noisy = []
    for i in range(len(pts)):
        pts_noisy.append([
            pts[i][0] + random.randint(-15, 15),
            pts[i][1] + random.randint(-15, 15)
        ])
    src = np.float32(pts)
    dst = np.float32(pts_noisy)
    M = cv2.getPerspectiveTransform(src, dst)
    image = cv2.warpPerspective(image, M, image.shape[:2][::-1])
    return cv2_to_PIL(image), pts_noisy
    

def overlay(background, image, mask, pts, shift_x, shift_y):
    background.paste(image, (shift_x, shift_y), mask)
    for i in range(4):
        pts[i][0] += shift_x
        pts[i][1] += shift_y
    return background, pts