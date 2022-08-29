from __future__ import annotations

import os
import pickle
from copy import deepcopy
from pathlib import Path
from time import time
from typing import Iterator

import cv2
import numpy as np

from constants import (
    ACTIVE,
    BIN_FOLDER_NAME,
    LOG_LIMIT,
    OFFLINE,
    REFERENCE_FILENAME,
    RES_FOLDER_NAME,
    TARGET_PATH,
)
from image import ImageSegment, get_point
from utils import (
    get_filename_from_path,
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
        image_path: str,
        image_segments: Iterator[ImageSegment] = None,
        versions=10,
        image=None,
        mode=OFFLINE,
        image_dimensions=None,
    ) -> None:
        self.mode = mode
        if mode == ACTIVE:
            self.image = image
        else:
            self.image_path = image_path
            self.image = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
            self.versions = versions
            self.target_dir_binary = get_target_dir_binary(self.image_path)
            self.target_dir_result = get_target_dir_result(self.image_path)
        self.image_height, self.image_width = (
            image_dimensions or self.image.shape[:2]
        )
        self.log_ctr = (self.image_height * self.image_width) // LOG_LIMIT
        self.image_segments = image_segments or []

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

    def process(
        self,
    ):
        """
        Saves the pkl file of the image as ImageSegments(and Points)
        """
        if self.mode == OFFLINE:
            reference_file_path = os.path.join(
                self.target_dir_binary, REFERENCE_FILENAME
            )
            if os.path.exists(reference_file_path):
                print(f"Refence file exists. Skipping the processing. :)")
                aid = AutoImageDraw.load(reference_file_path)
                self.image_segments = deepcopy(aid.image_segments)
                return
        self.image_binary = cv2.threshold(
            self.image, 150, 255, cv2.THRESH_BINARY
        )[1]
        seen = {}
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
                        image=self.image_binary,
                        similar=True,
                    )
                    to_process.extend(neighbors)
                    image_segment.add(curr, image=self.image_binary)
                    # print(f"to process->{len(to_process)}:{len(seen)}")
                self.image_segments.append(image_segment)
                if len(seen) % self.log_ctr == 0:
                    print(f"Processed {len(seen)} of {total}...")

        if self.mode == OFFLINE:
            self.save(filename=REFERENCE_FILENAME, variation=False)

    def create_versions(self, filename=None, versions=None):
        """
        Creates colored versions of the image and saved them as pkl files
        """
        versions = versions or self.versions
        filename = get_filename_from_path(self.image_path, include_ext=False)
        for _ in range(versions):
            filename_version = filename + f"_{int(time()*1000)}.pkl"
            self.save(filename=filename_version)

    def save(self, filename, base_folder=None, variation=True):
        """
        Genereates a new version of the base pkl file
        Colors the image in binary(pkl) format
        Saves it as a new file
        """
        base_folder = base_folder or self.target_dir_binary
        with open(os.path.join(base_folder, filename), "wb") as fh:
            aid = AutoImageDraw(
                image_path=self.image_path,
                image_segments=deepcopy(self.image_segments),
            )
            if variation:
                for image_segment in aid.image_segments:
                    image_segment.randomize_color()

            pickle.dump(aid, fh)
            print(f"Saved image to -> {fh.name}")

    def create_variation(self, mode=None):
        aid = AutoImageDraw(
            image_path=None,
            image_segments=deepcopy(self.image_segments),
            mode=mode or self.mode,
            image_dimensions=(self.image_height, self.image_width),
        )
        for image_segment in aid.image_segments:
            image_segment.randomize_color()
        return aid

    @classmethod
    def load(self, file_path=None) -> AutoImageDraw:
        """
        Reads the pkl file to be loaded as a python 'AutoImageDraw' object
        """
        print(f"Loading {file_path}")
        with open(file_path, "rb") as fh:
            aid = pickle.load(fh)
            print("Loading complete")
            return aid

    def repaint(self, target_filename, target_dir=None):
        """
        Given a pkl file, saves it as an image in given path
        """
        target_dir = target_dir or self.target_dir_result
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

    def run(self, versions: int = None):
        self.process()
        self.create_versions(versions=versions or self.versions)


def create_variations(image_path, count):
    aid = AutoImageDraw(image_path=image_path, versions=count)
    print(f"{aid.target_dir_binary}, {aid.target_dir_result}")
    aid.run()


def render_variations(source_dir_binary):
    bin_filenames = [
        os.path.join(source_dir_binary, filename)
        for filename in os.listdir(source_dir_binary)
        if filename.endswith(".pkl") and filename != REFERENCE_FILENAME
    ]
    for i, bin_finename in enumerate(bin_filenames):
        aid: AutoImageDraw = AutoImageDraw.load(bin_finename)
        filename = get_filename_from_path(bin_finename)
        try:
            file_path = f"{filename}.png"
            if not os.path.exists(file_path):
                print(f"Processing {i+1} of {len(bin_filenames)}")
                aid.repaint(file_path)
        except Exception as e:
            print(f"Failed to repaint {filename}: {e}")


if __name__ == "__main__":
    # needed to load the pkl file
    from image import Point

    image_path = ".data/images/mandala_circular.jpeg"
    create_variations(image_path=image_path, count=1)
    source_dir = ".data/images/mandala_circular/bin"
    render_variations(source_dir=source_dir)
