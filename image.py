from functools import lru_cache
from math import sqrt
from random import choice, randint
from typing import Iterator

from constants import Color


class Point:
    """Class representation of a co-ordinate with helper methods"""

    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_color_same(self, point, image):
        # print(
        #     f"point:{point}, self:{type(image[self.y][self.x])},"
        #     f" image:{image[point.y][point.x]}"
        # )
        return (image[self.y][self.x] == image[point.y][point.x]).all()

    def get_all_neighbors(self, connectivity=4):
        default_neighbors = (
            get_point(self.x + 1, self.y),
            get_point(self.x - 1, self.y),
            get_point(self.x, self.y + 1),
            get_point(self.x, self.y - 1),
        )
        if connectivity == 4:
            return (*default_neighbors,)
        elif connectivity == 8:
            return *default_neighbors, *(
                get_point(self.x - 1, self.y - 1),
                get_point(self.x + 1, self.y - 1),
                get_point(self.x + 1, self.y + 1),
                get_point(self.x - 1, self.y + 1),
            )

    def get_valid_neighbors(
        self, max_x, max_y, image, connectivity=4, similar=False
    ):
        neighbors = self.get_all_neighbors(connectivity=connectivity)
        valid_neighbors = []
        for neighbor in neighbors:
            if (0 <= neighbor.x < max_x) and (0 <= neighbor.y < max_y):
                valid_neighbors.append(neighbor)
        # print(f"valid_neighbors->{valid_neighbors}")
        if similar:
            return tuple(
                [
                    neighbor
                    for neighbor in valid_neighbors
                    if self.is_color_same(neighbor, image=image)
                ]
            )
        return valid_neighbors

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return str(self)


class ImageSegment:
    def __init__(
        self, points: Iterator[Point] = None, base_color=None, color=None
    ) -> None:
        self.points = points or []
        self.base_color = base_color
        self.color = color

    def add(self, point: Point, image):
        self.points.append(point)
        if self.base_color is None:
            # print(f"Image Segment color->{image[point.y][point.x]}")
            self.set_base_color(image[point.y][point.x])

    def set_base_color(self, color):
        self.base_color = color

    def is_black(self):
        return (self.base_color == Color.BLACK).all()

    def is_eligible_for_coloring(self):
        return not self.is_black()

    def randomize_color(self, color=None):
        if self.is_eligible_for_coloring():
            self.color = color or tuple([randint(50, 255) for _ in range(3)])
        else:
            self.color = self.base_color

    def sort_x(self) -> Iterator[Point]:
        def comparator(point: Point) -> int:
            return point.x

        self.points = sorted(self.points, key=comparator)
        return self.points

    def sort_y(self) -> Iterator[Point]:
        def comparator(point: Point) -> int:
            return point.y

        self.points = sorted(self.points, key=comparator)
        return self.points

    def sort_avg(self) -> Iterator[Point]:
        def comparator(point: Point) -> int:
            return (point.x + point.y) / 2

        self.points = sorted(self.points, key=comparator)
        return self.points

    def sort_distance(self) -> Iterator[Point]:
        def comparator(point: Point) -> int:
            return sqrt(point.x**2 + point.y**2)

        self.points = sorted(self.points, key=comparator)
        return self.points

    ###implement others as needed


@lru_cache
def get_point(x, y) -> Point:
    return Point(x, y)
