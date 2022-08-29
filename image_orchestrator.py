from __future__ import annotations

import os
import pickle
from copy import deepcopy
from pathlib import Path
from time import time
from typing import Iterator

import cv2
import numpy as np

from constants import LOG_LIMIT, REFERENCE_FILENAME
from image import ImageSegment, get_point
from utils import (
    get_filename_from_path,
    get_image_binary,
    get_image_grayscale,
    get_image_resize,
    get_image_size,
    get_target_dir_binary,
    get_target_dir_result,
)


class AutoImageDraw:
    """
    Class to represent an image in its individual components
    - ImageSegment(s)
      - Points
    """

    def __init__(
        self,
        image: np.ndarray = None,
        image_segments: Iterator[ImageSegment] = None,
        image_size: Iterator[int] = None,
    ) -> None:
        self.image = (
            self.preprocess_image(image=image) if not image is None else None
        )
        self.image_height, self.image_width = (
            get_image_size(image=self.image)
            if not image is None
            else image_size
        )
        self.log_ctr = (self.image_height * self.image_width) // LOG_LIMIT
        self.image_segments = image_segments or []

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        image = get_image_resize(image=image)
        image = get_image_grayscale(image=image)
        return get_image_binary(image=image)

    @property
    def k_segments(self):
        """Returns all the image segments with color = BLACK"""
        return [
            image_segment
            for image_segment in self.image_segments
            if image_segment.is_black()
        ]

    @property
    def non_k_segments(self):
        """Returns all the image segments with color != BLACK"""
        return [
            image_segment
            for image_segment in self.image_segments
            if not image_segment.is_black()
        ]

    def __str__(self) -> str:
        return (
            f"{self.image_path}->({self.image_width, self.image_height})."
            f" Image segments:{len(self.image_segments)}"
        )

    def process_image(self, image: np.ndarray = None):
        """
        Saves the pkl file of the image as ImageSegments(and Points)
        """
        seen = {}
        image = image or self.image
        total = self.image_width * self.image_height
        for x in range(0, self.image_width):
            for y in range(0, self.image_height):
                curr = get_point(x, y)
                if (curr.y, curr.x) in seen:
                    continue
                # print(f"ROOT:{curr}")
                to_process = [curr]
                image_segment = ImageSegment()
                while to_process:
                    curr = to_process.pop()
                    if (curr.y, curr.x) in seen:
                        continue
                    seen[(curr.y, curr.x)] = True
                    neighbors = curr.get_valid_neighbors(
                        max_x=self.image_width,
                        max_y=self.image_height,
                        image=image,
                        similar=True,
                    )
                    to_process.extend(neighbors)
                    image_segment.add(curr, image=image)
                    # print(f"to process->{len(to_process)}:{len(seen)}")
                self.image_segments.append(image_segment)
                if len(seen) % self.log_ctr == 0:
                    print(f"Processed {len(seen)} of {total}...")

    def create_versions(
        self, target_dir_binary: str, image_path=None, versions=None
    ):
        """
        Creates colored versions of the image and saved them as pkl files
        """
        versions = versions or self.versions
        filename = get_filename_from_path(image_path, include_ext=False)
        for _ in range(versions):
            filename_version = filename + f"_{int(time()*1000)}.pkl"
            self.save(
                aid=self.create_version(),
                filename=filename_version,
                target_dir_binary=target_dir_binary,
            )

    def create_version(self) -> AutoImageDraw:
        aid = AutoImageDraw(
            image=None,
            image_segments=deepcopy(self.image_segments),
            image_size=(self.image_height, self.image_width),
        )
        for image_segment in aid.image_segments:
            image_segment.randomize_color()

        return aid

    def save(
        self, aid, filename, target_dir_binary=None, variation=True
    ) -> AutoImageDraw:
        """
        Genereates a new version of the base pkl file
        Colors the image in binary(pkl) format
        Saves it as a new file
        """
        with open(os.path.join(target_dir_binary, filename), "wb") as fh:
            pickle.dump(aid, fh)
            print(f"Saved image to -> {fh.name}")
        return aid

    @classmethod
    def load(self, file_path=None) -> AutoImageDraw:
        """
        Reads the (binary)pkl file to be loaded as a python 'AutoImageDraw' object
        """
        print(f"Loading {file_path}")
        with open(file_path, "rb") as fh:
            aid = pickle.load(fh)
            print("Loading complete")
            return aid

    def repaint(self, target_dir, target_filename):
        """
        Given a pkl file, saves it as an image in given path
        """
        filepath = os.path.join(target_dir, target_filename)
        image = self.create_image()
        print(f"Saved image to -> {filepath}")
        cv2.imwrite(filepath, image)

    def create_image(self):
        image = np.zeros((self.image_height, self.image_width, 3), np.uint8)
        for image_segment in self.image_segments:
            for point in image_segment.points:
                image[point.y][point.x] = image_segment.color
        return image

    def run(
        self,
        target_dir_binary: str,
        target_filename: str = None,
        image_path: str = None,
        base_pkl_path: str = None,
        versions: int = None,
    ):
        reference_file_path = base_pkl_path or os.path.join(
            target_dir_binary, REFERENCE_FILENAME
        )
        if os.path.exists(reference_file_path):
            print(
                f"Base binary exists -> {reference_file_path}. Will skip base"
                " processing"
            )
            aid = AutoImageDraw.load(file_path=reference_file_path)
            self.image_segments = deepcopy(aid.image_segments)
        else:
            target_filename = target_filename or REFERENCE_FILENAME
            binary_image = get_image_binary(self.image)
            self.process_image(image=binary_image)
            self.save(
                aid=self,
                filename=target_filename,
                variation=False,
                target_dir_binary=target_dir_binary,
            )

        self.create_versions(
            versions=versions or self.versions,
            image_path=image_path,
            target_dir_binary=target_dir_binary,
        )


def create_variations(image_path, count):
    image = cv2.imread(image_path)
    target_dir_binary = get_target_dir_binary(image_path)
    aid = AutoImageDraw(image=image)
    aid.run(
        versions=count,
        image_path=image_path,
        target_dir_binary=target_dir_binary,
    )


def render_variations(image_path, source_dir_binary):
    target_dir = get_target_dir_result(image_path)
    bin_filenames = [
        os.path.join(source_dir_binary, filename)
        for filename in os.listdir(source_dir_binary)
        if filename.endswith(".pkl") and filename != REFERENCE_FILENAME
    ]
    for i, bin_finename in enumerate(bin_filenames):
        aid: AutoImageDraw = AutoImageDraw.load(bin_finename)
        filename = get_filename_from_path(bin_finename)
        try:
            filename = f"{filename}.png"
            if not os.path.exists(os.path.join(target_dir, filename)):
                print(f"???Processing {i+1} of {len(bin_filenames)}")
                aid.repaint(target_filename=filename, target_dir=target_dir)
        except Exception as e:
            print(f"Failed to repaint {filename}: {e}")


if __name__ == "__main__":
    # needed to load the pkl file
    from image import Point

    image_path = ".data/images/mandala_circular.jpeg"
    create_variations(image_path=image_path, count=1)
    source_dir = ".data/images/mandala_circular/bin"
    render_variations(image_path=image_path, source_dir_binary=source_dir)
