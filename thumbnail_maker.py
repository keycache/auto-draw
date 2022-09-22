import os

import click
import cv2
import numpy as np

from utils import create_empty_image, get_image_resize, get_image_size


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(
        image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR
    )
    return result


def create_thumbnail(
    src_image_path, filled_image_path, tgt_image_dir, preview=False
) -> np.ndarray:
    src_image = cv2.imread(src_image_path)
    filled_image = cv2.imread(filled_image_path)
    image_size = get_image_size(filled_image)
    src_image = get_image_resize(src_image, resize=image_size)
    image = create_empty_image(size=image_size)
    half_1 = src_image[0 : image_size[0], 0 : int(image_size[1] / 2)]
    half_2 = filled_image[0 : image_size[0], int(image_size[1] / 2) :]
    image[0 : image_size[0], 0 : int(image_size[1] / 2)] = half_1
    image[0 : image_size[0], int(image_size[1] / 2) :] = half_2
    tgt_image_path = os.path.join(tgt_image_dir, "thumbnail.jpg")
    src_image_path = os.path.join(tgt_image_dir, "reference.jpg")
    filled_image_path = os.path.join(tgt_image_dir, "filled.jpg")
    cv2.imwrite(tgt_image_path, image)
    cv2.imwrite(src_image_path, src_image)
    cv2.imwrite(filled_image_path, filled_image)
    image = rotate_image(image=image, angle=20)
    if preview:
        print("Press any key on the preview image to continue")
        cv2.imshow("default", image)
        cv2.waitKey(0)


@click.command()
@click.option(
    "--base-image",
    required=True,
    type=str,
    help="Path to the raw image",
)
@click.option(
    "--rendered-image",
    required=True,
    type=str,
    help="Path to the rendered image.",
)
@click.option(
    "--target-dir",
    required=True,
    type=str,
    help="Target directory to store the thumbnail",
)
@click.option(
    "--preview",
    required=False,
    type=bool,
    help="Option to see final rendered image",
)
def run(base_image, rendered_image, target_dir, preview):
    """
    Create a thumbnail given two images
    """
    create_thumbnail(
        src_image_path=base_image,
        filled_image_path=rendered_image,
        tgt_image_dir=target_dir,
        preview=preview,
    )


if __name__ == "__main__":
    run()
