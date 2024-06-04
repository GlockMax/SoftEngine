import pygame as pg
from matrix_functions import *
from numba import njit


@njit(fastmath=True)
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))


SPEED = 0.0000005


class Object3D:
    def __init__(self, render, vertices='', faces=''):
        self.render = render
        self.vertices = np.array(vertices)
        self.faces = faces
        #self.translate([0.0001, 0.0001, 0.0001])

        self.font = pg.font.SysFont('Arial', 30, bold=True)
        self.color_faces = [(pg.Color('orange'), face) for face in self.faces]
        self.movement_flag, self.draw_vertices = True, False
        self.label = ''
        self.angle_x = 0
        self.start_ax = 0
        self.movement_type = {
            "translate": self.translate,
            "scale": self.scale,
            "rotate_x": self.rotate_x,
            "rotate_y": self.rotate_y,
            "rotate_z": self.rotate_z
        }
        self.movement_timers = {
            "translate": 0,
            "scale": 0,
            "rotate_x": 0,
            "rotate_y": 0,
            "rotate_z": 0,
        }
        self.movement_targets = {
            "translate": [],
            "scale": 0,
            "rotate_x": 0,
            "rotate_y": 0,
            "rotate_z": 0
        }

    def draw(self):
        self.screen_projection()
        self.movement()

    def movement(self):
        #if self.movement_flag:
            #self.rotate_y(-(pg.time.get_ticks() % 0.005))

        '''if self.angle_x > 0:
            #print(self.angle_x, pg.time.get_ticks() - self.start_ax)
            phi = SPEED * (pg.time.get_ticks() - self.start_ax)**2
            if self.angle_x - phi > 0:
                self.rotate_x(phi)
                self.angle_x -= phi
            else:
                self.rotate_x(self.angle_x)
                self.angle_x = 0
            print("->", self.angle_x, pg.time.get_ticks() - self.start_ax)'''
        for mt in self.movement_type.keys():
            if type(self.movement_targets[mt]) != list:
                ed = 0 if mt != "scale" else 1
                if self.movement_targets[mt] > ed:
                    start = self.movement_timers[mt]
                    phi = SPEED * (pg.time.get_ticks() - start) ** 2
                    if self.movement_targets[mt] - phi > ed:
                        self.movement_type[mt](phi)
                        self.movement_targets[mt] -= phi
                    else:
                        self.movement_type[mt](self.movement_targets[mt])
                        self.movement_targets[mt] = ed

    def screen_projection(self):
        vertices = self.vertices @ self.render.camera.camera_matrix()
        vertices = vertices @ self.render.projection.projection_matrix
        vertices /= vertices[:, -1].reshape(-1, 1)
        vertices[(vertices > 2) | (vertices < -2)] = 0
        vertices = vertices @ self.render.projection.to_screen_matrix
        vertices = vertices[:, :2]

        for index, color_face in enumerate(self.color_faces):
            color, face = color_face
            polygon = vertices[face]
            if not any_func(polygon, self.render.H_WIDTH, self.render.H_HEIGHT):
                pg.draw.polygon(self.render.screen, color, polygon, 1)
                if self.label:
                    text = self.font.render(self.label[index], True, pg.Color('white'))
                    self.render.screen.blit(text, polygon[-1])

        if self.draw_vertices:
            for vertex in vertices:
                if not any_func(vertex, self.render.H_WIDTH, self.render.H_HEIGHT):
                    pg.draw.circle(self.render.screen, pg.Color('white'), vertex, 2)

    def translate(self, pos):
        self.vertices = self.vertices @ translate(pos)

    def scale(self, scale_to):
        self.vertices = self.vertices @ scale(scale_to)

    def rotate_x(self, angle):
        self.vertices = self.vertices @ rotate_x(angle)

    def rotate_y(self, angle):
        self.vertices = self.vertices @ rotate_y(angle)

    def rotate_z(self, angle):
        self.vertices = self.vertices @ rotate_z(angle)


class Axes(Object3D):
    def __init__(self, render):
        t_vertices = np.array([(0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
        t_faces = np.array([(0, 1), (0, 2), (0, 3)])
        super().__init__(render, t_vertices, t_faces)
        self.colors = [pg.Color('red'), pg.Color('green'), pg.Color('blue')]
        self.color_faces = [(color, face) for color, face in zip(self.colors, self.faces)]
        self.draw_vertices = False
        self.label = 'XYZ'
