import random

import pygame
import sys
import numpy as np
from utils import read_points, transform_point, rotate_vector, calculate_depth, \
    partition_polygon
from constants import *


class Figure:
    def __init__(self, points, edges, walls, name):
        self.points = points
        self.edges = edges
        self.walls = walls
        self.name = name

    def get_walls(self):
        walls_as_points = []
        for wall in self.walls:
            walls_as_points.append([self.points[point] for point in wall])

        return walls_as_points

    def get_edges(self):
        edges_as_points = []
        for edge in self.edges:
            edges_as_points.append([self.points[point] for point in edge])

        return edges_as_points


class CameraSimulation:
    def __init__(self, partition_factor=3):
        pygame.init()
        self.screen = pygame.display.set_mode((Display.WIDTH, Display.HEIGHT))
        pygame.display.set_caption("3D Camera Simulation")
        self.camera_position = np.array([0.0, 50, 750])
        self.camera_rotation = np.array([0.0, 0.0, 0.0])
        self.zoom = 1
        self.partition_factor = partition_factor
        self.f = 1000
        self.speed_up = 75
        self.rotation_angle = 0.0001
        self.display_table = False
        self.draw_edges = True
        self.draw_walls = True
        self.draw_solid_walls = True
        self.color_walls = True
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.points = read_points("points.txt")
        self.figures = self.create_figures()
        self.walls = self.get_walls()
        self.partitioned_walls = self.partition_walls()
        self.light_strength = 1
        self.move_vectors = {
            "forward": np.array([0.0, 0.0, -0.05]),
            "backward": np.array([0.0, 0.0, 0.05]),
            "left": np.array([0.05, 0.0, 0.0]),
            "right": np.array([-0.05, 0.0, 0.0]),
            "up": np.array([0.0, -0.05, 0.0]),
            "down": np.array([0.0, 0.05, 0.0]),
        }

    def create_figures(self):
        figures = []
        for figure_id, key in enumerate(self.points):
            figure_points = self.points[key]
            figure_edges = []
            figure_walls = []
            for i, edge in enumerate(edges):
                figure_edges.append(edge)
            for i, wall in enumerate(walls):
                figure_walls.append(wall)
            figures.append(Figure(figure_points, figure_edges, figure_walls, key))

        return figures

    def get_walls(self):
        figure_walls = []

        for figure_id, figure in enumerate(self.figures):
            figure_walls.extend([(figure_id, wall) for wall in figure.get_walls()])

        return figure_walls

    def partition_walls(self):
        partitioned_walls = []

        for figure_id, wall in self.walls:
            partitioned_walls.extend(
                [(figure_id, smaller_wall) for smaller_wall in partition_polygon(wall, self.partition_factor)])

        return partitioned_walls

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.display_table = not self.display_table
                if event.key == pygame.K_1:
                    self.draw_edges = not self.draw_edges
                if event.key == pygame.K_2:
                    self.draw_solid_walls = not self.draw_solid_walls
                if event.key == pygame.K_3:
                    self.draw_walls = not self.draw_walls
                if event.key == pygame.K_4:
                    self.color_walls = not self.color_walls
                if event.key == pygame.K_x:
                    self.partition_factor = max(1, self.partition_factor - 1)
                    self.walls = self.get_walls()
                    self.partitioned_walls = self.partition_walls()
                if event.key == pygame.K_z:
                    self.partition_factor += 1
                    self.walls = self.get_walls()
                    self.partitioned_walls = self.partition_walls()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            self.higher_zoom()
        if keys[pygame.K_m]:
            self.lower_zoom()
        if keys[pygame.K_RIGHT]:
            self.camera_rotation[0] += (self.rotation_angle * self.get_speed_up()) % (2 * np.pi)
        if keys[pygame.K_LEFT]:
            self.camera_rotation[0] -= (self.rotation_angle * self.get_speed_up()) % (2 * np.pi)
        if keys[pygame.K_UP]:
            self.camera_rotation[1] += (self.rotation_angle * self.get_speed_up()) % (2 * np.pi)
        if keys[pygame.K_DOWN]:
            self.camera_rotation[1] -= (self.rotation_angle * self.get_speed_up()) % (2 * np.pi)
        if keys[pygame.K_w]:
            self.move_camera("forward")
        if keys[pygame.K_s]:
            self.move_camera("backward")
        if keys[pygame.K_a]:
            self.move_camera("left")
        if keys[pygame.K_d]:
            self.move_camera("right")
        if keys[pygame.K_q]:
            self.move_camera("up")
        if keys[pygame.K_e]:
            self.move_camera("down")
        if keys[pygame.K_c]:
            self.light_strength += 0.01
        if keys[pygame.K_v]:
            self.light_strength = max(0.01, self.light_strength - 0.01)
        if keys[pygame.K_EQUALS]:
            self.speed_up = self.speed_up * 1.01 if self.speed_up < 1000 else 1000
        if keys[pygame.K_MINUS]:
            self.speed_up = self.speed_up / 1.01 if self.speed_up > 1 else 1
        if keys[pygame.K_r]:
            self.reset_camera()

    def move_camera(self, direction):
        move = rotate_vector(self.get_move_vector(direction), self.camera_rotation)
        move = move * self.get_speed_up()
        self.camera_position += move

    def get_move_vector(self, direction):
        return self.move_vectors[direction]

    def higher_zoom(self):
        if self.zoom < 10:
            self.zoom += 0.001

    def lower_zoom(self):
        if self.zoom > 0.1:
            self.zoom -= 0.001

    def draw_table(self):
        text = self.font.render("Camera Position:", True, Colors.WHITE)
        self.screen.blit(text, (10, 10))
        text = self.font.render(f"X: {self.camera_position[0]:.2f}", True, Colors.WHITE)
        self.screen.blit(text, (10, 40))
        text = self.font.render(f"Y: {self.camera_position[1]:.2f}", True, Colors.WHITE)
        self.screen.blit(text, (10, 70))
        text = self.font.render(f"Z: {self.camera_position[2]:.2f}", True, Colors.WHITE)
        self.screen.blit(text, (10, 100))
        text = self.font.render(
            f"Camera Rotation: {'°, '.join([str(round(float(i) * 180, 2)) for i in self.camera_rotation])}",
            True,
            Colors.WHITE,
        )
        self.screen.blit(text, (10, 130))
        text = self.font.render(f"Zoom: {self.zoom:.2f}", True, Colors.WHITE)
        self.screen.blit(text, (10, 160))
        text = self.font.render(f"Focal Length: {self.f:.2f}", True, Colors.WHITE)
        self.screen.blit(text, (10, 190))
        text = self.font.render(f"Speed Up: {self.speed_up}", True, Colors.WHITE)
        self.screen.blit(text, (10, 220))
        text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, Colors.WHITE)
        self.screen.blit(text, (10, 250))
        text = self.font.render(f"Draw edges: {self.draw_edges}", True, Colors.WHITE)
        self.screen.blit(text, (10, 280))
        text = self.font.render(f"Draw solid walls: {self.draw_solid_walls} [2]", True, Colors.WHITE)
        self.screen.blit(text, (10, 310))
        text = self.font.render(f"Draw walls: {self.draw_walls} [3]", True, Colors.WHITE)
        self.screen.blit(text, (10, 340))
        text = self.font.render(f"Draw color walls: {self.color_walls} [4]", True, Colors.WHITE)
        self.screen.blit(text, (10, 370))
        text = self.font.render(f"Partition factor: {self.partition_factor} [z/x]", True, Colors.WHITE)
        self.screen.blit(text, (10, 400))
        text = self.font.render(f"Light strength: {self.light_strength:.2f} [c/v]", True, Colors.WHITE)
        self.screen.blit(text, (10, 430))
        text = self.font.render("Press H to hide this table", True, Colors.WHITE)
        self.screen.blit(text, (10, 470))

    def draw_all_walls(self):
        self.partitioned_walls.sort(key=lambda pair: calculate_depth(pair[1], self.camera_position), reverse=True)

        if self.color_walls:
            self.draw_color_walls()
        else:
            self.draw_mono_walls()

    def draw_color_walls(self):
        for figure_id, wall in self.partitioned_walls:
            transformed_wall = self.transform_points(wall)

            if self.draw_walls:
                if self.draw_solid_walls:
                    self.draw_wall(transformed_wall, figure_id)
                else:
                    self.draw_wall_see_through(transformed_wall, figure_id)

    def draw_mono_walls(self):
        # Length to the first wall
        distance = calculate_depth(self.partitioned_walls[-1][1], self.camera_position)

        # Total number of objects to draw
        total_objects = len(self.partitioned_walls)

        for i, pair in enumerate(self.partitioned_walls):
            figure_id, wall = pair

            transformed_wall = self.transform_points(wall)

            # Calculate darkness based on distance
            darkness = min(255, max(0, (255 - (distance // 5) / self.light_strength)))

            if self.draw_walls:
                if self.draw_solid_walls:
                    # Draw wall with current darkness
                    self.draw_wall_with_color(transformed_wall, [darkness, darkness, darkness])
                else:
                    # Draw wall see-through with current darkness
                    self.draw_wall_see_through_with_color(transformed_wall, [darkness, darkness, darkness])

            # Calculate distance for the next object
            if i < total_objects - 1:
                next_wall = self.partitioned_walls[i + 1][1]
                distance = calculate_depth(next_wall, self.camera_position)

    def transform_points(self, points):
        transformed_points = []
        for i, point in enumerate(points):
            transformed_point = transform_point(point, self.camera_position, self.camera_rotation, self.f, self.zoom)
            transformed_points.append(transformed_point)

        return transformed_points

    def draw_wall(self, points, color_id):
        color = [Colors.RED, Colors.GREEN, Colors.BLUE, Colors.PURPLE][color_id]
        pygame.draw.polygon(self.screen, color, points)

    def draw_wall_see_through(self, points, color_id, alpha=50):
        color = [Colors.RED, Colors.GREEN, Colors.BLUE, Colors.PURPLE][color_id]

        # Create a surface for drawing the transparent wall
        wall_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)

        # Draw the polygon on the surface with the specified color and alpha
        pygame.draw.polygon(wall_surface, (*color, alpha), points)

        # Blit the transparent surface onto the main screen
        self.screen.blit(wall_surface, (0, 0))

    def draw_wall_with_color(self, points, color):
        pygame.draw.polygon(self.screen, color, points)

    def draw_wall_see_through_with_color(self, points, color, alpha=50):
        # Create a surface for drawing the transparent wall
        wall_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)

        # Draw the polygon on the surface with the specified color and alpha
        pygame.draw.polygon(wall_surface, (*color, alpha), points)

        # Blit the transparent surface onto the main screen
        self.screen.blit(wall_surface, (0, 0))

    def reset_camera(self):
        self.camera_position = np.array([0.0, 50, 750])
        self.camera_rotation = np.array([0.0, 0.0, 0.0])
        self.zoom = 1
        self.rotation_angle = 0.0001
        self.f = 1000
        self.speed_up = 75

    def run_simulation(self):
        while True:
            self.screen.fill(Colors.BLACK)
            self.handle_input()
            self.draw_all_walls()
            if self.display_table:
                self.draw_table()

            pygame.display.flip()

            self.clock.tick()

    def calculated_fps_slow_down(self):
        return 75 / self.clock.get_fps() if self.clock.get_fps() != 0 else 1

    def get_speed_up(self):
        return self.speed_up * self.calculated_fps_slow_down()


if __name__ == "__main__":
    simulation = CameraSimulation(partition_factor=2)
    simulation.run_simulation()
