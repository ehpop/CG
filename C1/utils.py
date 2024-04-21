import json
import numpy as np
from numpy import cos, sin, matrix, dot
from constants import Display
import math

projection_matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 0]])


def read_points(filename):
    """Read 3D points from a file."""
    with open(filename, "r") as file:
        data = json.load(file)

    return data


def rotate_x_scene(point, k):
    """Rotation matrix around the X-axis."""
    cos_k = np.cos(k)
    sin_k = np.sin(k)
    rotation_matrix = np.array([[1, 0, 0], [0, cos_k, -sin_k], [0, sin_k, cos_k]])
    return np.dot(rotation_matrix, point)


def rotate_y_scene(point, k):
    """Rotation matrix around the Y-axis."""
    cos_k = np.cos(k)
    sin_k = np.sin(k)
    rotation_matrix = np.array([[cos_k, 0, sin_k], [0, 1, 0], [-sin_k, 0, cos_k]])
    return np.dot(rotation_matrix, point)


def rotate_z_scene(point, k):
    """Rotation matrix around the Z-axis."""
    cos_k = np.cos(k)
    sin_k = np.sin(k)
    rotation_matrix = np.array([[cos_k, -sin_k, 0], [sin_k, cos_k, 0], [0, 0, 1]])
    return np.dot(rotation_matrix, point)


def rotate_vector(vector, angles):
    x_angle, y_angle, z_angle = angles

    rotated_vector = vector
    rotated_vector = rotate_y_scene(rotated_vector, x_angle)
    rotated_vector = rotate_x_scene(rotated_vector, y_angle)
    rotated_vector = rotate_z_scene(rotated_vector, z_angle)
    return rotated_vector


def rotate_point(point, camera_rotation):
    """Rotate a point around the camera's position."""
    rotated_point = point.copy()
    for axis, rotation_angle in enumerate(camera_rotation):
        if rotation_angle != 0:
            rotation_angle *= -1  # Invert the rotation angle
            if axis == 0:  # Rotate around X-axis
                rotated_point = rotate_y_scene(rotated_point, rotation_angle)
            elif axis == 1:  # Rotate around Y-axis
                rotated_point = rotate_x_scene(rotated_point, rotation_angle)
            elif axis == 2:  # Rotate around Z-axis
                rotated_point = rotate_z_scene(rotated_point, rotation_angle)
    return rotated_point


def project_point(point, f, zoom=1):
    """Project a 3D point to 2D."""
    calculated_f = f / point[2] if point[2] != 0 else 0.0001
    projected_point = np.dot(projection_matrix, point)
    projected_point = np.dot(calculated_f, projected_point)
    projected_point = np.dot(zoom, projected_point)
    return projected_point


def center_point(point):
    """Center a point in the screen."""
    return point[0] + Display.WIDTH / 2, point[1] + Display.HEIGHT / 2


def transform_point(point, camera_position, camera_rotation, f, zoom=1):
    """Transform a 3D point to a 2D point."""
    translated_point = point - camera_position
    rotated_point = rotate_point(translated_point, camera_rotation)
    projected_point = project_point(rotated_point, f, zoom)
    centered_point = center_point(projected_point)

    return centered_point


def distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))


def calculate_depth(polygon, camera_position):
    centroid = np.mean(polygon, axis=0)
    return distance(centroid, camera_position)


def get_middle_point(p1, p2):
    return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2]


def partition_polygon_single_time(points):
    p1, p2, p3, p4 = points

    mid_p1_p2 = get_middle_point(p1, p2)
    mid_p2_p3 = get_middle_point(p2, p3)
    mid_p3_p4 = get_middle_point(p3, p4)
    mid_p4_p1 = get_middle_point(p4, p1)
    mid_p1_p3 = get_middle_point(p1, p3)

    polygon_1 = [p1, mid_p1_p2, mid_p1_p3, mid_p4_p1]
    polygon_2 = [mid_p1_p2, p2, mid_p2_p3, mid_p1_p3]
    polygon_3 = [mid_p1_p3, mid_p2_p3, p3, mid_p3_p4]
    polygon_4 = [mid_p4_p1, mid_p1_p3, mid_p3_p4, p4]

    return [polygon_1, polygon_2, polygon_3, polygon_4]


def partition_polygon(points, n=1):
    if n == 0:
        return points

    polygons = partition_polygon_single_time(points)
    for _ in range(n - 1):
        new_polygons = []
        for polygon in polygons:
            new_polygons.extend(partition_polygon_single_time(polygon))
        polygons = new_polygons

    return polygons
