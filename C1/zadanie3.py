import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
import numpy as np

vertex_shader = """
#version 330
in vec3 position;
in vec3 normal;

out vec3 FragPos;
out vec3 Normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * normal;
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
"""

fragment_shader = """
#version 330 core
in vec3 FragPos;
in vec3 Normal;

out vec4 FragColor;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 ambient;
uniform vec3 diffuse;
uniform vec3 specular;
uniform float shininess;

void main()
{
    // Ambient
    float ambientStrength = 0.1;
    vec3 ambientLight = ambientStrength * lightColor * ambient;

    // Diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuseLight = diff * lightColor * diffuse;

    // Specular
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specularLight = specularStrength * spec * lightColor * specular;

    vec3 result = ambientLight + diffuseLight + specularLight;
    FragColor = vec4(result, 1.0);
}

"""


def create_sphere(radius, lat_segments, lon_segments):
    vertices = []
    normals = []
    indices = []

    for i in range(lat_segments + 1):
        theta = i * np.pi / lat_segments
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)

        for j in range(lon_segments):
            phi = j * 2 * np.pi / lon_segments
            sin_phi = np.sin(phi)
            cos_phi = np.cos(phi)

            x = cos_phi * sin_theta
            y = cos_theta
            z = sin_phi * sin_theta

            vertices.append((radius * x, radius * y, radius * z))
            normals.append((x, y, z))

    for i in range(lat_segments):
        for j in range(lon_segments):
            first = (i * (lon_segments + 1)) + j
            second = first + lon_segments + 1

            indices.append(first)
            indices.append(second)
            indices.append(first + 1)

            indices.append(second)
            indices.append(second + 1)
            indices.append(first + 1)

    return (
        np.array(vertices, dtype=np.float32),
        np.array(normals, dtype=np.float32),
        np.array(indices, dtype=np.uint32),
    )


def compile_shader_program():
    shader = compileProgram(
        compileShader(vertex_shader, GL_VERTEX_SHADER),
        compileShader(fragment_shader, GL_FRAGMENT_SHADER),
    )
    return shader


materials = {
    "metal": (
        np.array([0.25, 0.25, 0.25], dtype=np.float32),
        np.array([0.5, 0.5, 0.5], dtype=np.float32),
        np.array([0.774597, 0.774597, 0.774597], dtype=np.float32),
        80.0,
    ),
    "plastic": (
        np.array([0.0, 0.1, 0.06], dtype=np.float32),
        np.array([0.0, 0.50980392, 0.50980392], dtype=np.float32),
        np.array([0.50196078, 0.50196078, 0.50196078], dtype=np.float32),
        32.0,
    ),
    "wood": (
        np.array([0.19125, 0.0735, 0.0225], dtype=np.float32),
        np.array([0.7038, 0.27048, 0.0828], dtype=np.float32),
        np.array([0.256777, 0.137622, 0.086014], dtype=np.float32),
        12.8,
    ),
    "wall": (
        np.array([0.1, 0.1, 0.1], dtype=np.float32),
        np.array([0.6, 0.6, 0.6], dtype=np.float32),
        np.array([0.1, 0.1, 0.1], dtype=np.float32),
        8.0,
    ),
}
current_material = "metal"


def change_material(shader, material):
    ambient, diffuse, specular, shininess = materials[material]
    glUniform3fv(glGetUniformLocation(shader, "ambient"), 1, ambient)
    glUniform3fv(glGetUniformLocation(shader, "diffuse"), 1, diffuse)
    glUniform3fv(glGetUniformLocation(shader, "specular"), 1, specular)
    glUniform1f(glGetUniformLocation(shader, "shininess"), shininess)


def draw_text(x, y, text):
    font = pygame.font.SysFont("arial", 28)
    text_surface = font.render(text, False, (0, 255, 66, 255)).convert_alpha()
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(
        text_surface.get_width(),
        text_surface.get_height(),
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        text_data,
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Phong Shading in PyOpenGL")

    glClearColor(0.4, 0.9, 0.9, 1.0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    shader = compile_shader_program()

    vertices, normals, indices = create_sphere(0.5, 100, 1000)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    NBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ARRAY_BUFFER, NBO)
    glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    position = glGetAttribLocation(shader, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(position)

    glBindBuffer(GL_ARRAY_BUFFER, NBO)
    normal = glGetAttribLocation(shader, "normal")
    glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(normal)

    glBindVertexArray(0)

    projection = np.matrix(np.identity(4), dtype=np.float32)
    view = np.matrix(np.identity(4), dtype=np.float32)
    model = np.matrix(np.identity(4), dtype=np.float32)

    light_strength = 1.0
    light_pos = np.array([106.00, 100.00, -1200.00], dtype=np.float32)
    view_pos = np.array([-250.00, -900.00, -5300.00], dtype=np.float32)
    light_color = np.array([1.0, 1.0, 1.0], dtype=np.float32) * light_strength

    clock = pygame.time.Clock()
    running = True

    font = pygame.font.Font(None, 72)
    debug_mode = False

    global current_material

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_1:
                    current_material = "metal"
                elif event.key == K_2:
                    current_material = "plastic"
                elif event.key == K_3:
                    current_material = "wood"
                elif event.key == K_4:
                    current_material = "wall"
                elif event.key == K_d:
                    debug_mode = not debug_mode

        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            light_pos[0] -= 50.1
        if keys[K_RIGHT]:
            light_pos[0] += 50.1
        if keys[K_UP]:
            light_pos[1] += 50.1
        if keys[K_DOWN]:
            light_pos[1] -= 50.1
        if keys[K_PAGEUP]:
            light_pos[2] += 50.1
        if keys[K_PAGEDOWN]:
            light_pos[2] -= 50.1
        if keys[K_w]:
            view_pos[2] += 50.1
        if keys[K_s]:
            view_pos[2] -= 50.1
        if keys[K_a]:
            view_pos[0] -= 50.1
        if keys[K_d]:
            view_pos[0] += 50.1
        if keys[K_q]:
            view_pos[1] -= 50.1
        if keys[K_e]:
            view_pos[1] += 50.1
        if keys[K_EQUALS]:
            light_strength = min(light_strength + 0.01, 1.0)
            light_color = np.array([1.0, 1.0, 1.0], dtype=np.float32) * light_strength
        if keys[K_MINUS]:
            light_strength = max(light_strength - 0.01, 0.0)
            light_color = np.array([1.0, 1.0, 1.0], dtype=np.float32) * light_strength

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(shader)

        glUniformMatrix4fv(
            glGetUniformLocation(shader, "projection"), 1, GL_FALSE, projection
        )
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model)

        glUniform3fv(glGetUniformLocation(shader, "lightPos"), 1, light_pos)
        glUniform3fv(glGetUniformLocation(shader, "viewPos"), 1, view_pos)
        glUniform3fv(glGetUniformLocation(shader, "lightColor"), 1, light_color)
        glUniform3fv(
            glGetUniformLocation(shader, "objectColor"),
            1,
            np.array([1.0, 1.0, 1.0], dtype=np.float32),
        )

        change_material(shader, current_material)

        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        if debug_mode:
            draw_text(10, 10, f"Light pos: {light_pos}")
            draw_text(10, 80, f"View pos: {view_pos}")
            draw_text(10, 150, f"Light strength: {light_strength}")
            draw_text(10, 220, f"Material: {current_material}")

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
