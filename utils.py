import math
import os
import re
from pathlib import Path
from typing import Iterator

import cv2
import numpy as np

from constants import (
    BIN_FOLDER_NAME,
    MAX_IMAGE_SIZE,
    RES_FOLDER_NAME,
    TARGET_PATH,
)
from image import ImageSegment, Point


def mkdir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def get_image_size(image: np.ndarray):
    return image.shape[:2]


def get_image_resize(
    image: np.ndarray, interpolation=cv2.INTER_AREA
) -> np.ndarray:
    height, width = get_image_size(image=image)
    size = min(MAX_IMAGE_SIZE, height, width)
    image = cv2.resize(image, (size, size), interpolation=interpolation)
    return image


def get_image_grayscale(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def get_image_binary(image: np.ndarray) -> np.ndarray:
    return cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)[1]


def sanitize_file_name(file_name):
    return file_name.replace(".", "")


def get_filename_from_path(file_path: str, include_ext: bool = True):
    filename = os.path.basename(file_path)
    if not include_ext:
        filename = os.path.splitext(filename)[0]
    return filename


def get_target_dir_binary(image_path):
    target_dir = os.path.join(
        TARGET_PATH,
        sanitize_file_name(
            get_filename_from_path(image_path, include_ext=False)
        ),
    )
    target_dir_binary = os.path.join(target_dir, BIN_FOLDER_NAME)
    mkdir(target_dir_binary)
    return target_dir_binary


def get_target_dir_result(image_path):
    target_dir = os.path.join(
        TARGET_PATH,
        sanitize_file_name(
            get_filename_from_path(image_path, include_ext=False)
        ),
    )
    target_dir_result = os.path.join(target_dir, RES_FOLDER_NAME)
    mkdir(target_dir_result)
    return target_dir_result


def get_distance(p1: Point, p2: Point) -> float:
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def comparator_img_seg_size(segment: ImageSegment):
    return len(segment.points)


def comparator_x_y(segment: ImageSegment, ref_point: Point):
    segment.sort_x()
    point = segment.points[0]
    return point.y, point.x
    return get_distance(ref_point, point)


def comparator_closest_segment(
    segment: ImageSegment, ref_segment: ImageSegment
):
    point = segment.points[0]
    ref_point = ref_segment.points[0]
    return get_distance(point, ref_point)


def comparator_alphanum(item: str):
    def tryint(item):
        try:
            return int(item)
        except:
            return item

    return [tryint(c) for c in re.split("([0-9]+)", item)]


if __name__ == "__main__":
    from image_orchestrator import Point

    points: Iterator[Point] = [
        Point(10, 10),
        Point(0, 0),
        Point(0, 5),
        Point(2, 4),
        Point(2, 0),
    ]
    # print(sorter_x(points=points))
    # print(sorter_y(points=points))
    # print(sorter_avg(points=points))
