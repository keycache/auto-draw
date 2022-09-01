import os
from pathlib import Path
from time import time
from typing import Iterator

import cv2
import numpy as np

from constants import (
    DEFAULT_SNAPSHOT_COUNTER,
    FRAME_RATE,
    LARGE_SEGMENT_PIXEL_COUNT,
    SNAPSHOT_TIMES,
    SNAPSHOTS_FOLDER_NAME,
    Render,
)
from image import ImageSegment
from image_orchestrator import AutoImageDraw
from utils import (
    comparator_closest_segment,
    comparator_img_seg_size,
    get_filename_from_path,
    mkdir,
)


class Sketcher:
    def __init__(
        self, binary_filepath: str, snanpshot_times=None, mode: str = None
    ) -> None:
        self.aid = AutoImageDraw.load(binary_filepath)
        self.binary_filepath = binary_filepath
        self.snanpshot_times = snanpshot_times or SNAPSHOT_TIMES
        self.image = np.zeros(
            (self.aid.image_height, self.aid.image_width, 3), np.uint8
        )
        self.image.fill(255)
        print(
            "Created empty image"
            f" ({self.aid.image_height, self.aid.image_width})"
        )
        self.snapshot_counter = DEFAULT_SNAPSHOT_COUNTER
        self.frame_rate = FRAME_RATE
        # 1000 represents the millseconds
        # delay represents the time in ms to wait for opencv
        self.delay = int(1000 / self.frame_rate)
        self.target_dir = None
        self.mode = mode or Render.ACTIVE
        self.setup()

    def setup(self):
        target_dir = os.path.join(
            Path(self.binary_filepath).parents[1], SNAPSHOTS_FOLDER_NAME
        )
        mkdir(target_dir)
        self.target_dir = target_dir

    def paint(self):
        self.paint_non_k_segments()
        self.paint_k_segments()

    def get_snapshot_counter(self, segment: ImageSegment) -> int:
        """Calculate image snapshot counter based on config"""
        for segment_pixel_count, snapshot_ctr in self.snanpshot_times:
            if len(segment.points) <= segment_pixel_count:
                return snapshot_ctr
        return self.snapshot_counter

    def get_file_name(self):
        file_name = "_".join(
            get_filename_from_path(
                self.binary_filepath, include_ext=False
            ).split("_")[:-1]
        )
        return f"{file_name}_{int(time()*1000)}"

    def paint_segments(self, image_segments: Iterator[ImageSegment]):
        for i, image_segment in enumerate(image_segments):
            snapshot_counter = self.get_snapshot_counter(image_segment)
            print(
                f"Snapshot Counter for seg_id({i+1}/{len(image_segments)}) ->"
                f" {snapshot_counter} -> {len(image_segment.points)}"
            )
            count = 0
            file_name = self.get_file_name()
            for j, point in enumerate(image_segment.points):
                x, y = point.x, point.y
                self.image[y, x] = image_segment.color
                if count % snapshot_counter == 1:
                    self.process_image(file_name=f"{file_name}_{i}_{j}.png")
                count += 1

    def show_image_snapshot(self, image: np.ndarray):
        cv2.imshow("default", image)
        cv2.waitKey(self.delay)

    def save_image_snapshot(
        self, file_name: str, target_dir: str = None, image: np.ndarray = None
    ):
        file_path = os.path.join(target_dir or self.target_dir, file_name)
        if not os.path.exists(file_path):
            image = image if image is not None else self.image
            cv2.imwrite(file_path, image)

    def process_image(self, file_name: str):
        if self.mode == Render.ACTIVE:
            self.show_image_snapshot(image=self.image)
        if self.mode == Render.OFFLINE:
            self.save_image_snapshot(
                image=self.image,
                target_dir=self.target_dir,
                file_name=file_name,
            )

    def partition_segments(
        self, segments: Iterator[ImageSegment]
    ) -> Iterator[Iterator[ImageSegment]]:
        """
        * Partitions image segments based on threshold
          defined in LARGE_SEGMENT_PIXEL_COUNT
        * Large partitions are sorted based on the count of points
        * Non large partition sort is based on min distance
          btween the image segments
        """
        temp_non_large_segments = []
        large_segments = []
        # Split the segments in to 2 categories based on pixel count
        for segment in segments:
            if len(segment.points) > LARGE_SEGMENT_PIXEL_COUNT:
                large_segments.append(segment)
            else:
                temp_non_large_segments.append(segment)

        # Sort the large segments
        large_segments = sorted(
            large_segments, reverse=False, key=comparator_img_seg_size
        )

        # Sort the non large sements based on the image segment proximity
        ctr = 0
        total_non_large_segments = len(temp_non_large_segments)
        non_large_segments = []
        while ctr < total_non_large_segments:
            ref_segment = temp_non_large_segments.pop(0)
            non_large_segments.append(ref_segment)
            temp_non_large_segments = sorted(
                temp_non_large_segments,
                key=lambda segment: comparator_closest_segment(
                    segment, ref_segment
                ),
            )
            ctr += 1
        return large_segments, non_large_segments

    def paint_k_segments(self):
        """
        Paint all outlined segments
        """
        k_segments = self.aid.k_segments
        large_segments, non_large_segments = self.partition_segments(
            segments=k_segments
        )
        for segments in (
            non_large_segments,
            large_segments,
        ):
            print(f"Painting {len(segments)} outline segments")
            self.paint_segments(segments)

    def paint_non_k_segments(self):
        """
        Paint all colored segments
        """
        non_k_segments: Iterator[ImageSegment] = self.aid.non_k_segments

        large_segments, non_large_segments = self.partition_segments(
            segments=non_k_segments
        )

        for segments in (
            non_large_segments,
            large_segments,
        ):
            print(f"Painting {len(segments)} colored segments")
            self.paint_segments(segments)
            for segment in segments:
                segment.sort_avg()


def run():
    binary_filepath = (
        ".data/images/mandala-ganesha/bin/mandala-ganesha_1661924904338.pkl"
    )
    sketcher = Sketcher(
        binary_filepath=binary_filepath,
        snanpshot_times=None,
        mode=Render.OFFLINE,
    )
    sketcher.paint()


if __name__ == "__main__":
    run()
