import pygame
import sys
import numpy as np
from utils import read_points, project_point, rotate_x_object, rotate_y_object
from constants import *


class CameraSimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Display.WIDTH, Display.HEIGHT))
        pygame.display.set_caption("3D Camera Simulation")
        self.camera_position = np.array([0.01, -50, -750])
        self.camera_rotation = np.array([0.01, 0.01, 0.01])
        self.zoom = 1
        self.f = 1000
        self.speed_up = 10
        self.display_table = False
        self.points = read_points("points.txt")
        self.font = pygame.font.Font(None, 24)

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
            self.camera_rotation[0] += 0.0001 * self.speed_up
        if keys[pygame.K_LEFT]:
            self.camera_rotation[0] -= 0.0001 * self.speed_up
        if keys[pygame.K_UP]:
            self.camera_rotation[1] += 0.0001 * self.speed_up
        if keys[pygame.K_DOWN]:
            self.camera_rotation[1] -= 0.0001 * self.speed_up
        if keys[pygame.K_w]:
            self.camera_position[1] -= 0.5
        if keys[pygame.K_s]:
            self.camera_position[1] += 0.5
        if keys[pygame.K_a]:
            self.camera_position[0] -= 0.5
        if keys[pygame.K_d]:
            self.camera_position[0] += 0.5
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

    def higher_zoom(self):
        if self.zoom < 10:
            self.zoom += 0.001

    def lower_zoom(self):
        if self.zoom > 0.001:
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
            f"Camera Rotation: {self.camera_rotation}", True, Colors.WHITE
        )
        self.screen.blit(text, (10, 130))
        text = self.font.render(f"Zoom: {self.zoom:.2f}", True, Colors.WHITE)
        self.screen.blit(text, (10, 160))
        text = self.font.render(f"Focal Length: {self.f:.2f}", True, Colors.WHITE)
        self.screen.blit(text, (10, 190))
        text = self.font.render(f"Speed Up: {self.speed_up}", True, Colors.WHITE)
        self.screen.blit(text, (10, 220))

    def draw_all_points(self):
        for key in self.points:
            projected_points = []
            figure_points = self.points[key]
            for point in figure_points:
                rotated_point = rotate_x_object(point, self.camera_rotation[0])
                rotated_point = rotate_y_object(rotated_point, self.camera_rotation[1])
                translated_point = rotated_point - self.camera_position
                calculated_f = (
                    self.f / translated_point[2] if translated_point[2] != 0 else 0.0001
                )
                projected_point = project_point(translated_point)
                x = projected_point[0] * calculated_f * self.zoom + Display.WIDTH / 2
                y = projected_point[1] * calculated_f * self.zoom + Display.HEIGHT / 2
                projected_points.append((x, y))
            for i, edge in enumerate(edges):
                self.draw_edge(edge, projected_points, Colors.WHITE)

    def draw_edge(self, edge, points, color):
        pygame.draw.line(self.screen, color, points[edge[0]], points[edge[1]])

    def reset_camera(self):
        self.camera_position = np.array([0.01, -50, -750])
        self.camera_rotation = np.array([0, 0, 0])
        self.zoom = 1
        self.f = 1000
        self.speed_up = 1

    def run_simulation(self):
        while True:
            self.screen.fill(Colors.BLACK)
            self.handle_input()
            for key in self.points:
                figure_points = self.points[key]
                self.draw_all_points()
            if self.display_table:
                self.draw_table()
            pygame.display.flip()


if __name__ == "__main__":
    simulation = CameraSimulation()
    simulation.run_simulation()
