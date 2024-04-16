import json
import numpy as np

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


def rotate_x_object(point, k):
    return rotate_y_scene(point, k)


def rotate_y_object(point, k):
    return rotate_x_scene(point, k)


def project_point(point):
    """Project a 3D point to 2D."""
    return np.dot(projection_matrix, point)
