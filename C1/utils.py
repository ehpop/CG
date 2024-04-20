import json
import numpy as np
from numpy import cos, sin, matrix, dot

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


# Rotate the movement vectors based on camera rotation
def rotate_vector(vector, angles):
    x_angle, y_angle, z_angle = angles

    rotated_vector = vector
    rotated_vector = rotate_y_scene(rotated_vector, x_angle)
    rotated_vector = rotate_x_scene(rotated_vector, y_angle)
    rotated_vector = rotate_z_scene(rotated_vector, z_angle)
    return rotated_vector


def rotate_point(point, camera_rotation):
    """Rotate a point around the camera's position."""
    rotated_point = point.copy()  # Make a copy to avoid modifying the original point
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


def project_point(point, f):
    """Project a 3D point to 2D."""
    calculated_f = f / point[2] if point[2] != 0 else 0.0001
    projected_point = np.dot(projection_matrix, point)
    projected_point = np.dot(calculated_f, projected_point)
    return projected_point
