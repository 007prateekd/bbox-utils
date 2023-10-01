# bbox-utils

## What
Just a small utility script that contains simple functions to
- generate a binary mask and the corresponding bounding box coordinates of a subject in an image.
- do simple transformations on an image (i.e. rotation, scaling, warping, overlaying, cropping, square resize) and modify the bounding box coordinates accordingly (which could be quite challenging in some cases! For example, check [this](https://github.com/007prateekd/bbox-utils/blob/16d930da01371b558213cbf6255b4af6c8a69511/main.py#L140-L145)).

## Why
While creating a synthetic dataset for an object detection use-case, I often ran into image transformations where I had a hard time modifying the corresponding bounding box coordinates with respect to the transformation applied. So, I created these helper functions which do the same. I have used PIL and OpenCV interchangably as both have some functionalities which are easier to use.

## How
Run `python main.py` and the outputs would get saved to the [images](images) folder. If you set `display = True` [here](https://github.com/007prateekd/bbox-utils/blob/364de3cbf08a46219830aa5acd83b6e3c21db483/main.py#L283), then the outputs would also be displayed on the screen one by one. The only requirements are [OpenCV](https://pypi.org/project/opencv-python/) and [Pillow](https://pypi.org/project/Pillow/) libraries. To run the script on your own image, change this [path](https://github.com/007prateekd/bbox-utils/blob/279254da1a493803d2157de4c1cfa9190b8eb7f7/main.py#L221) to where your image is. The functions have docstrings attached and can be used individually as per requirement.

## Results
<details>
<summary>&nbspSource image</summary>
<img src=images/sample.jpg>
</details>
<details>
<summary>&nbspBinary mask of source image</summary>
<img src=images/mask.jpg>
</details>
<details>
<summary>&nbspOverlaying source image on a white background</summary>
<img src=images/overlayed.jpg>
</details>
<details>
<summary>&nbspScaled image</summary>
<img src=images/scaled.jpg>
</details>
<details>
<summary>&nbspRotated image</summary>
<img src=images/rotated.jpg>
</details>
<details>
<summary>&nbspWarped image</summary>
<img src=images/warped.jpg>
</details>
<details>
<summary>&nbspCropped image</summary>
<img src=images/cropped.jpg>
</details>
<details>
<summary>&nbspResized square image</summary>
<img src=images/resized.jpg>
</details>
<details>
<summary>&nbspFinal bounding box coordinates</summary>
<img src=images/bounding_box.jpg>
</details>