import pygame
import sys
import numpy as np
from utils import read_points, project_point, rotate_point, rotate_vector, transform_point
from constants import *


class CameraSimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Display.WIDTH, Display.HEIGHT))
        pygame.display.set_caption("3D Camera Simulation")
        self.camera_position = np.array([0.0, 50, 750])
        self.camera_rotation = np.array([0.0, 0.0, 0.0])
        self.zoom = 1
        self.f = 1000
        self.speed_up = 10
        self.rotation_angle = 0.0001
        self.display_table = False
        self.points = read_points("points.txt")
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.move_vectors = {
            "forward": np.array([0.0, 0.0, -0.5]),
            "backward": np.array([0.0, 0.0, 0.5]),
            "left": np.array([0.5, 0.0, 0.0]),
            "right": np.array([-0.5, 0.0, 0.0]),
            "up": np.array([0.0, -0.5, 0.0]),
            "down": np.array([0.0, 0.5, 0.0]),
        }

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.display_table = not self.display_table

        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            self.higher_zoom()
        if keys[pygame.K_m]:
            self.lower_zoom()
        if keys[pygame.K_RIGHT]:
            self.camera_rotation[0] += self.rotation_angle * self.speed_up
        if keys[pygame.K_LEFT]:
            self.camera_rotation[0] -= self.rotation_angle * self.speed_up
        if keys[pygame.K_UP]:
            self.camera_rotation[1] += self.rotation_angle * self.speed_up
        if keys[pygame.K_DOWN]:
            self.camera_rotation[1] -= self.rotation_angle * self.speed_up
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
        if keys[pygame.K_x]:
            self.f -= 0.1
        if keys[pygame.K_z]:
            self.f += 0.1
        if keys[pygame.K_EQUALS]:
            self.speed_up = min(self.speed_up + 1, 10)
        if keys[pygame.K_MINUS]:
            self.speed_up = self.speed_up / 2 if self.speed_up > 1 else 1
        if keys[pygame.K_r]:
            self.reset_camera()

    def move_camera(self, direction):
        move = rotate_vector(self.get_move_vector(direction), self.camera_rotation)
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

    def draw_all_points(self):
        for key in self.points:
            figure_points = self.points[key]
            self.draw_figure(figure_points)

    def draw_figure(self, figure_points):
        transformed_points = []
        for point in figure_points:
            transformed_point = transform_point(point, self.camera_position, self.camera_rotation, self.f, self.zoom)
            transformed_points.append(transformed_point)
        for i, edge in enumerate(edges):
            self.draw_edge(edge, transformed_points, Colors.WHITE)

    def draw_edge(self, edge, points, color):
        pygame.draw.line(self.screen, color, points[edge[0]], points[edge[1]])

    def reset_camera(self):
        self.camera_position = np.array([0.0, 50, 750])
        self.camera_rotation = np.array([0.0, 0.0, 0.0])
        self.zoom = 1
        self.rotation_angle = 0.0001
        self.f = 1000
        self.speed_up = 10

    def run_simulation(self):
        while True:
            self.screen.fill(Colors.BLACK)
            self.handle_input()
            self.draw_all_points()
            if self.display_table:
                self.draw_table()
            pygame.display.flip()

            self.clock.tick(1000)


if __name__ == "__main__":
    simulation = CameraSimulation()
    simulation.run_simulation()
