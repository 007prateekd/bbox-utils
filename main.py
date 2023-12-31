import math
import random
import numpy as np
import cv2
from PIL import Image


def imshow(img, title=""):
    """Displays an OpenCV image.

    Args:
        img (ndarray): OpenCV image or any ndarray float32 dtype.
        title (str, optional): Title of the displayed window. Defaults to "".
    """
    cv2.imshow(title, img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def cv2_to_PIL(img):
    """Converts OpenCV image to PIL's format.

    Args:
        img (ndarray): OpenCV image or any ndarray float32 dtype.

    Returns:
        PIL.Image: The input image in PIL.
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    return img


def PIL_to_cv2(img):
    """Converts PIL image to OpenCV's format.

    Args:
        img (PIL.Image): Image in PIL format.

    Returns:
        ndarray: The input image in OpenCV.
    """
    img = np.array(img) 
    if len(img.shape) == 3:
        img = img[:, :, ::-1].copy() 
    return img


def get_mask_simple(image, thresh=240):
    """Generate binary mask by thresholding by `thresh`
    and the corresponding bounding box of a subject in focus.

    Args:
        image (PIL.Image): Image in PIL format.
        thresh (int, optional): The threshold value for binarization of the image. Defaults to 240.

    Returns:
        PIL.Image: binary mask in PIL format.
        ndarray: bounding box with 4 coordinates in [top-left, top-right, bottom-right, bottom-left] format.
    """
    image = PIL_to_cv2(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = list(filter(lambda cnt: cv2.contourArea(cnt) > 500, contours))
    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
    mask = np.zeros(gray.shape, np.uint8)
    mask = cv2.fillPoly(mask, pts=[contours[1]], color=(255, 255, 255))
    mask = cv2_to_PIL(mask).convert("L")
    rect = cv2.minAreaRect(contours[1])
    box = np.int0(cv2.boxPoints(rect))
    return mask, box


def overlay(background, foreground, mask, box, shift_x, shift_y):
    """Pastes `foreground` on `background` masking the areas given by `mask`.
    The pasting coordinates start from (`shift_x`, `shift_y`).

    Args:
        background (PIL.Image): Background image in PIL format
        foreground (PIL.Image): Foreground image in PIL format.
        mask (PIL.Image): Binary mask of the foreground image in PIL format.
        box (ndarray): Bounding box coordinates.
        shift_x (_type_): Pixels to be shifted horizontally when pasting foreground on background.
        shift_y (_type_): Pixels to be shifted vertically when pasting foreground on background.

    Returns:
        PIL.Image: Background with pasted foreground.
        ndarray: Modified bounding box coordinates.
    """
    background.paste(foreground, (shift_x, shift_y), mask)
    for i in range(4):
        box[i][0] += shift_x
        box[i][1] += shift_y
    return background, box


def scale_down(image, box, factor):
    """Resizes the image down by `factor` while preserving the aspect ratio. 
    Also modifies the bounding box coordinates accordingly.

    Args:
        image (PIL.Image): Image in PIL format.
        box (ndarray): Bounding box coordinates.
        factor (float): The factor by which to scale down the image.

    Returns:
        PIL.Image: Scaled down image.
        ndarray: Modified bounding box coordinates.
    """
    h, w = image.size
    image_copy = image.copy()
    image_copy.thumbnail(size=(h / factor, w / factor))
    for i in range(len(box)):
        box[i][0] /= factor
        box[i][1] /= factor
    return image_copy, box


def rotate(image, box, angle):
    """Rotates the image by `angle`.
    Also modifies the bounding box coordinates accordingly.

    Args:
        image (PIL.Image): Image in PIL format.
        box (ndarray): Bounding box coordinates.
        angle (float): Angle to rotate the image by in degrees.

    Returns:
        PIL.Image: Rotated image.
        ndarray: Modified bounding box coordinates.
    """
    w, h = image.size
    image = image.rotate(
        angle,
        fillcolor=(0, 0, 0)
    )
    box_new = []
    x0, y0 = image.size[0] / 2, image.size[1] / 2
    for i in range(4):
        x, y = box[i]
        theta = (math.pi / 180) * (360 - angle)
        x_new = x * math.cos(theta) - y * math.sin(theta) + x0 * (1 - math.cos(theta)) + y0 * math.sin(theta) + (w / 2 - x0)
        y_new = y * math.cos(theta) + x * math.sin(theta) + y0 * (1 - math.cos(theta)) - x0 * math.sin(theta) + (h / 2 - y0)
        box_new.append([x_new, y_new])
    return image, box_new


def warp(image, box, warp_x=15, warp_y=15):
    """Warps an image by a maximum of `warp_x` horizontally and `warp_y` vertically.
    Also modifies the bounding box coordinates accordingly.

    Args:
        image (PIL.Image): Image in PIL format.
        box (ndarray): Bounding box coordinates.
        warp_x (float): The maximum value by which image will be warped along x-axis. 
        warp_y (float): The maximum value by which image will be warped along y-axis. 

    Returns:
        PIL.Image: Warped image.
        ndarray: Modified bounding box coordinates.
    """
    image = PIL_to_cv2(image)
    box_noisy = []
    for i in range(len(box)):
        box_noisy.append([
            box[i][0] + random.randint(-warp_x, warp_x),
            box[i][1] + random.randint(-warp_y, warp_y)
        ])
    src = np.float32(box)
    dst = np.float32(box_noisy)
    M = cv2.getPerspectiveTransform(src, dst)
    image = cv2.warpPerspective(image, M, image.shape[:2][::-1])
    return cv2_to_PIL(image), box_noisy
 

def crop_center(image, box, crop):
    """Crops the image to the center with `crop` pixels being cut from each side of the image.

    Args:
        image (PIL.Image): Image in PIL format.
        box (ndarray): Bounding box coordinates.
        crop (int): Number of pixels to be cut from each side.

    Returns:
        PIL.Image: Cropped image.
        ndarray: Modified bounding box coordinates.
    """
    w, h = image.size
    image = image.crop((crop, crop, w - crop, h - crop))
    for i in range(len(box)):
        box[i][0] -= crop
        box[i][1] -= crop
    return image, box


def resize_and_pad_square(image, box, size):
    """Resizes the image to a square of side `size` with zero-padding to preserve aspect ratio.

    Args:
        image (ndaray): Image in OpenCV format.
        box (ndarray): Bounding box coordinates.
        size (tuple): Tuple containing target (height, width).

    Returns:
        ndaray: Square and padded image.
        ndarray: Modified bounding box coordinates.
    """
    h, w = image.shape[:2]
    c = image.shape[2] if len(image.shape) > 2 else 1
    if h == w: 
        return cv2.resize(image, size, cv2.INTER_AREA)
    dif = h if h > w else w
    interpolation = cv2.INTER_AREA if dif > (size[0] + size[1]) // 2 else cv2.INTER_CUBIC
    x_pos = (dif - w) // 2
    y_pos = (dif - h) // 2
    if len(image.shape) == 2:
        mask = np.zeros((dif, dif), dtype=image.dtype)
        mask[y_pos:y_pos+h, x_pos:x_pos+w] = image
    else:
        mask = np.zeros((dif, dif, c), dtype=image.dtype)
        mask[y_pos:y_pos+h, x_pos:x_pos+w, :] = image
    image = cv2.resize(mask, size, interpolation)
    box_new = []
    for i in range(4):
        x_new = round((box[i][0] + x_pos) * (size[0] / dif))
        y_new = round((box[i][1] + y_pos) * (size[0] / dif))
        box_new.append([x_new, y_new])
    return image, box_new


def draw_box(image, box):
    """Draws the 4 corners of the bounding box on the image.

    Args:
        image (PIL.Image): Image in PIL format.
        box (ndarray): Bounding box coordinates.

    Returns:
        ndarray: Modified image with the 4 corners drawn in OpenCV format.
    """
    draw = PIL_to_cv2(image)
    for i in range(4):
        draw = cv2.circle(draw, (round(box[i][0]), round(box[i][1])), 10, (0, 255, 0), -1)
    return draw


def main(path, display, save):
    img = Image.open(path)
    background = Image.new("RGB", (2 * img.size[0], 2 * img.size[1]), (255, 255, 255))
    mask, box = get_mask_simple(img, thresh=150)
    overlayed, box = overlay(background, img, mask, box, shift_x=250, shift_y=250)
    scaled, box = scale_down(overlayed, box, factor=2.5)
    rotated, box = rotate(scaled, box, angle=70)
    warped, box = warp(rotated, box)
    cropped, box = crop_center(warped, box, crop=100)
    resized, box = resize_and_pad_square(PIL_to_cv2(cropped), box, size=(768, 768))
    draw = draw_box(cv2_to_PIL(resized), box)

    if display:
        imshow(PIL_to_cv2(img), "Image")
        imshow(PIL_to_cv2(mask), "Mask")
        imshow(PIL_to_cv2(overlayed), "Overlayed")
        imshow(PIL_to_cv2(scaled), "Scaled")
        imshow(PIL_to_cv2(rotated), "Rotated")
        imshow(PIL_to_cv2(warped), "Warped")
        imshow(PIL_to_cv2(cropped), "Cropped")
        imshow(resized, "Resized")
        imshow(draw, "Bounding Box")
    if save:
        cv2.imwrite("images/mask.jpg", PIL_to_cv2(mask))
        cv2.imwrite("images/overlayed.jpg", PIL_to_cv2(overlayed))
        cv2.imwrite("images/scaled.jpg", PIL_to_cv2(scaled))
        cv2.imwrite("images/rotated.jpg", PIL_to_cv2(rotated))
        cv2.imwrite("images/warped.jpg", PIL_to_cv2(warped))
        cv2.imwrite("images/cropped.jpg", PIL_to_cv2(cropped))
        cv2.imwrite("images/resized.jpg", resized)
        cv2.imwrite("images/bounding_box.jpg", draw)


if __name__ == "__main__":
    path = "images/sample.jpg"
    display = False
    save = True
    main(path, display, save)