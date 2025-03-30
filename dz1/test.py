import os
import numpy as np
import math
import plotly.graph_objects as go
from PIL import Image
import random
import matplotlib.pyplot as plt

EPS = 1e-6


class Point:

    def __init__(self, x, y, z=None):
        self.x, self.y, self.z = x, y, z

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.x == getattr(other, "x", None) and self.y == getattr(other, "y", None)

    def __ne__(self, other):
        return not (self == other)

    def dist_to(self, point):
        if self.z is not None:
            return math.hypot(self.x - point.x, self.y - point.y, self.z - point.z)
        else:
            return math.sqrt(pow(self.x - point.x, 2) + pow(self.y - point.y, 2))


ORIGIN = Point(0, 0, 0)


def onSegment(p, q, r):
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False


def orientation(p, q, r):
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if (val > 0):

        # Clockwise orientation
        return 1
    elif (val < 0):

        # Counterclockwise orientation
        return 2
    else:

        # Collinear orientation
        return 0


def doIntersect(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if p1 == p2 or p1 == q2 or q1 == p2 or q1 == q2:
        return False

    # General case
    if ((o1 != o2) and (o3 != o4)):
        return True

    # Special Cases

    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    if ((o1 == 0) and onSegment(p1, p2, q1)):
        return True

    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    if ((o2 == 0) and onSegment(p1, q2, q1)):
        return True

    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    if ((o3 == 0) and onSegment(p2, p1, q2)):
        return True

    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
    if ((o4 == 0) and onSegment(p2, q1, q2)):
        return True

    # If none of the cases
    return False


class Segment:
    def __init__(self, p1, p2):
        self.p1, self.p2 = p1, p2

    def __hash__(self):
        return hash(hash(str(self.p1)) + hash(str(self.p2)))

    def length(self):
        if self.p1.z is not None and self.p2.z is not None:
            print(f"tp: {type(self.p1.z)}")
            return Point(self.p1.x - self.p2.x, self.p1.y - self.p2.y, self.p1.z - self.p2.z).dist_to(ORIGIN)
        else:
            return Point(self.p1.x - self.p2.x, self.p1.y - self.p2.y).dist_to(ORIGIN)

    def center(self):
        return Point((self.p1.x + self.p2.x) / 2, (self.p1.y + self.p2.y) / 2)

    def normal(self):
        if self.p1.y == self.p2.y:
            normal = Point(1, 0)
        else:
            normal = Point(1, (self.p2.x - self.p1.x) / (self.p1.y - self.p2.y))
        return Point(normal.x / normal.dist_to(ORIGIN), normal.y / normal.dist_to(ORIGIN))

    def intersect(self, other_segment):
        return doIntersect(self.p1, self.p2, other_segment.p1, other_segment.p2)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            (self.p1 == getattr(other, "p1", None) and self.p2 == getattr(other, "p2", None)) or \
            (self.p1 == getattr(other, "p2", None) and self.p2 == getattr(other, "p1", None))

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return "Segment(" + str(self.p1) + ", " + str(self.p2) + ")"


class Cell:
    def __init__(self, top_left: Point, bottom_right: Point):
        self.top_left = Point(min(top_left.x, bottom_right.x), min(top_left.y, bottom_right.y))
        self.bottom_right = Point(max(top_left.x, bottom_right.x), max(top_left.y, bottom_right.y))
        self.points = []

    def contains(self, p: Point):
        return self.top_left.x <= p.x <= self.bottom_right.x and self.top_left.y <= p.y <= self.bottom_right.y

    def dist_to(self, s: Segment):
        center = Point((self.top_left.x + self.bottom_right.x) / 2, (self.top_left.y + self.bottom_right.y) / 2)
        abx = s.p2.x - s.p1.y
        aby = s.p2.y - s.p1.y
        acx = center.x - s.p1.x
        acy = center.x - s.p1.y
        coef = (abx * acx + aby * acy) / (abx * abx + aby * aby)
        height = Point(s.p1.x + abx * coef, s.p1.y + aby * coef)
        edge_height_length = center.dist_to(height)
        edge_a_length = center.dist_to(s.p1)
        edge_b_length = center.dist_to(s.p2)
        if Cell(Point(min(s.p1.x, s.p2.x), min(s.p1.y, s.p2.y)),
                Point(max(s.p1.x, s.p2.x), max(s.p1.y, s.p2.y))).contains(height):
            return edge_height_length
        else:
            return min(edge_b_length, edge_a_length)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            (self.top_left == getattr(other, "top_left", None) and self.bottom_right == getattr(other, "bottom_right",
                                                                                                None))


class Circle:
    def __init__(self, center_point, radius):
        self.center_point, self.radius = center_point, radius

    def contains_point(self, point):
        return point.dist_to(self.center_point) <= self.radius


class Bubble:

    def __init__(self, initial_segment: Segment):
        self.initial_segment = initial_segment
        self.radius = self.initial_segment.length() / 2
        self.circle = Circle(self.initial_segment.center(), self.radius)
        self.inverted = None

    def adjust(self):
        self.radius *= 1.05
        new_length = math.sqrt(self.radius ** 2 - (self.initial_segment.length() / 2) ** 2)
        coef = 1 if self.inverted is None or not self.inverted else -1
        new_center = Point(self.initial_segment.center().x + coef * self.initial_segment.normal().x * new_length,
                           self.initial_segment.center().y + coef * self.initial_segment.normal().y * new_length)
        self.circle = Circle(new_center, self.radius)

    def invert(self):
        if self.inverted:
            raise RuntimeError("Double Inversion")
        self.inverted = True
        new_length = math.sqrt(self.radius ** 2 - (self.initial_segment.length() / 2) ** 2)
        coef = 1 if self.inverted is None or not self.inverted else -1
        new_center = Point(self.initial_segment.center().x + coef * self.initial_segment.normal().x * new_length,
                           self.initial_segment.center().y + coef * self.initial_segment.normal().y * new_length)
        self.circle = Circle(new_center, self.radius)


class Triangle:
    def __init__(self, p1, p2, p3):
        self.p1, self.p2, self.p3 = p1, p2, p3

    def __str__(self):
        return "Triangle(" + str(self.p1) + ", " + str(self.p2) + ", " + str(self.p3) + ")"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.p1 == getattr(other, "p1", None) and \
            self.p2 == getattr(other, "p2", None) and \
            self.p3 == getattr(other, "p3", None)

    def __ne__(self, other):
        return not (self == other)

    def get_points(self):
        return [self.p1, self.p2, self.p3]

    def get_edges(self):
        return [Segment(self.p1, self.p2), Segment(self.p2, self.p3), Segment(self.p3, self.p1)]

    def get_circumscribed_circle(self):
        lenghts = []
        for point in self.get_points():
            lenghts.append(point.x * point.x + point.y * point.y)

        z_x = (self.p1.y - self.p2.y) * lenghts[2] + (self.p2.y - self.p3.y) * lenghts[0] + (self.p3.y - self.p1.y) * \
              lenghts[1]
        z_y = (self.p1.x - self.p2.x) * lenghts[2] + (self.p2.x - self.p3.x) * lenghts[0] + (self.p3.x - self.p1.x) * \
              lenghts[1]
        z = (self.p1.x - self.p2.x) * (self.p3.y - self.p1.y) - (self.p1.y - self.p2.y) * (self.p3.x - self.p1.x)

        a = -z_x / (2 * z)
        b = z_y / (2 * z)
        point = Point(a, b)
        return Circle(point, point.dist_to(self.p1))

    def signed_area(self):
        return (self.p2.x - self.p1.x) * (self.p3.y - self.p1.y) - (self.p2.y - self.p1.y) * (self.p3.x - self.p1.x)


def find_baseline(source_points: list[Point]):
    sorted_points = sorted(source_points, key=lambda p: p.x)
    first = sorted_points[0]
    sorted_points.remove(first)
    second = sorted(filter(lambda p: p.x == sorted_points[0].x, sorted_points), key=lambda p: abs(p.y - first.y))[0]
    return Segment(first, second)


def triangulation(source_points: list[Point]):
    source_points = list(set(source_points))

    if len(source_points) == 0:
        return []

    # baselines = [find_baseline(source_points)]
    baselines = []
    sorted_segments = []
    for outer_point in source_points:
        for inner_point in source_points:
            if inner_point != outer_point and Segment(inner_point, outer_point) not in sorted_segments:
                sorted_segments.append(Segment(inner_point, outer_point))
    sorted_segments = sorted(list(set(sorted_segments)), key=lambda p: p.length())
    for segment in sorted_segments:
        is_intersected = False
        for baseline in baselines:
            if segment.intersect(baseline):
                is_intersected = True
                break
        if not is_intersected:
            baselines.append(segment)

    return baselines


def triangulation_heights(source_points: list[Point]):
    source_points = list(set(source_points))

    if len(source_points) == 0:
        return []

    # baselines = [find_baseline(source_points)]
    baselines = []
    sorted_segments = []
    for outer_point in source_points:
        for inner_point in source_points:
            if inner_point != outer_point and Segment(inner_point, outer_point) not in sorted_segments:
                sorted_segments.append(Segment(inner_point, outer_point))
    sorted_segments = sorted(list(set(sorted_segments)), key=lambda p: p.length())
    for segment in sorted_segments:
        is_intersected = False
        for baseline in baselines:
            if segment.intersect(baseline):
                is_intersected = True
                break
        if not is_intersected:
            baselines.append(segment)

    return baselines


point_count = 40
width, height = 1000, 1000

source_points = []
source_points_height = []
source_points_3d = []

for i in range(point_count):
    random_x = np.random.randint(0, width - 1)
    random_y = np.random.randint(0, height - 1)
    source_points.append(Point(random_x, random_y))
    source_points_height.append(np.random.randint(0, 100 * point_count))
    source_points_3d.append(Point(random_x, random_y, source_points_height[-1]))

"""
naive_segments = triangulation(source_points)
print(len(naive_segments))

segments = []
x = []
y = []
z = []
buffer = []
for segment in naive_segments:
    x.append(segment.p1.x)
    x.append(segment.p2.x)
    y.append(segment.p1.y)
    y.append(segment.p2.y)
    z1 = source_points_height[source_points.index(segment.p1)]
    z2 = source_points_height[source_points.index(segment.p2)]
    z.append(z1)
    z.append(z2)
    segments.append([(segment.p1.x, segment.p2.x), (segment.p1.y, segment.p2.y), (z1, z2)])
"""

naive_height_segments = triangulation_heights(source_points_3d)
print(len(naive_height_segments))

height_segments = []
x = []
y = []
z = []
buffer = []
for segment in naive_height_segments:
    x.append(segment.p1.x)
    x.append(segment.p2.x)
    y.append(segment.p1.y)
    y.append(segment.p2.y)
    z.append(segment.p1.z)
    z.append(segment.p2.z)
    height_segments.append([(segment.p1.x, segment.p2.x), (segment.p1.y, segment.p2.y), (segment.p1.z, segment.p2.z)])


def delaunau_triangulation_gen(source_points: list[Point], superstruct_dist):
    source_points = list(set(source_points))

    if len(source_points) == 0:
        return []
    baselines = [find_baseline(source_points)]
    source_points.remove(baselines[0].p1)
    source_points.remove(baselines[0].p2)
    cells = sorted(create_cells(superstruct_dist, source_points), key=lambda cell: cell.dist_to(baselines[0]))
    triangles = []
    while len(baselines) != 0:
        baseline = baselines[0]
        baseline_bubble = Bubble(baseline)
        cells = sorted(cells, key=lambda cell: cell.dist_to(baseline))
        print(f"baseline: p1=[x={baseline.p1.x}, y= {baseline.p1.y}], p2=[x={baseline.p2.x}, y={baseline.p2.y}]")
        baselines = baselines[1:]
        min_angle_cos = 2
        max_angle_point = None
        bubble_contains_point = False
        for triangle in triangles:
            for edge in triangle.get_edges():
                points = [triangle.p1, triangle.p2, triangle.p3]
                if edge == baseline:
                    third = next(filter(lambda p: p != baseline.p1 and p != baseline.p2, points))
                    normal_point = Point(baseline.center().x + baseline.normal().x, baseline.center().y + baseline.normal().y)
                    if Triangle(baseline.p1, baseline.p2, third).signed_area() * Triangle(baseline.p1, baseline.p2, normal_point).signed_area() > 0:
                        baseline_bubble.invert()
        while baseline_bubble.circle.radius < 500 and not bubble_contains_point:
            for idx, cell in enumerate(cells):
                for point in cell.points:
                    if baseline_bubble.circle.contains_point(point):
                        bubble_contains_point = True
                        break
                if bubble_contains_point:
                    break
            if not bubble_contains_point:
                baseline_bubble.adjust()
        for idx, cell in enumerate(cells):
            for point in cell.points:
                a = Point(baseline.p1.x - point.x, baseline.p1.y - point.y)
                b = Point(baseline.p2.x - point.x, baseline.p2.y - point.y)
                point_cos = (a.x * b.x + a.y * b.y) / math.sqrt((a.x ** 2 + a.y ** 2) * (b.x ** 2 + b.y ** 2))
                if point_cos < min_angle_cos and baseline_bubble.circle.contains_point(point):
                    min_angle_cos = point_cos
                    max_angle_point = point
                    print(f"{min_angle_cos} -> {180*math.acos(min_angle_cos)/math.pi}")
            if max_angle_point is not None:
                cells[idx].points.remove(max_angle_point)
                break
        if max_angle_point is None:
            continue
        baselines += [Segment(baseline.p1, max_angle_point), Segment(baseline.p2, max_angle_point)]
        triangles.append(Triangle(baseline.p1, baseline.p2, max_angle_point))
        yield triangles, baseline_bubble

    return triangles

baseline = find_baseline(source_points)
cells = sorted(create_cells(superstruct_dist, source_points), key=lambda cell: cell.dist_to(baseline))

print(f"baseline: p1=[x={baseline.p1.x}, y= {baseline.p1.y}], p2=[x={baseline.p2.x}, y={baseline.p2.y}]")
color = True
for cell in cells:
    for point in cell.points:
        ax.scatter(point.x, point.y, color=('red' if color else 'green'))
    ax.plot([cell.top_left.x, cell.bottom_right.x, cell.bottom_right.x, cell.top_left.x],
            [cell.top_left.y, cell.top_left.y, cell.bottom_right.y, cell.bottom_right.y])
    color = not color

ax.plot([baseline.p1.x, baseline.p2.x], [baseline.p1.y, baseline.p2.y], color='orange')
