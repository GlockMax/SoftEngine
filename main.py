import numpy as np

from object_3d import *
from camera import *
from projection import *
import pygame as pg
import pygame_gui as pgg


class SoftwareRender:
    def __init__(self):
        """Класс рендера"""
        # Инициализируем Pygame
        pg.init()
        self.RES = self.WIDTH, self.HEIGHT = 1200, 700
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 60
        self.screen = pg.display.set_mode(self.RES)
        self.manager = pgg.UIManager(self.RES)
        self.clock = pg.time.Clock()
        self.create_objects()
        self.create_ui()

    def create_objects(self):
        """Метод создания объектов сцены"""
        self.camera = Camera(self, [-5, 6, -55])
        self.projection = Projection(self)
        self.axis = Axes(self)
        self.axis.scale(10)
        #self.object = self.get_object_from_file('resources/t_34_obj.obj')
        self.object = Object3D(self, vertices=[[1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]],
                               faces=[[0, 1, 2], [3, 4, 5], [0, 1, 4, 3], [0, 2, 5, 3], [1, 2, 5, 4]])
        self.object.scale(10)
        self.axis.movement_flag = False
        self.object.movement_flag = False
        self.object.draw_vertices = True

        #self.object.rotate_y(-math.pi / 4)

    def create_ui(self):
        """Метод создания объектов UI, контролируемых self.manager"""
        self.left_ui_rect = pgg.elements.UIWindow(pg.Rect(0, 0, 400, self.HEIGHT))
        self.translate_fields = [
            pgg.elements.UITextEntryLine(relative_rect=pg.Rect(10, 10, 50, 30), manager=self.manager,
                                         container=self.left_ui_rect,),
            pgg.elements.UITextEntryLine(relative_rect=pg.Rect(70, 10, 50, 30), manager=self.manager,
                                         container=self.left_ui_rect,),
            pgg.elements.UITextEntryLine(relative_rect=pg.Rect(130, 10, 50, 30), manager=self.manager,
                                         container=self.left_ui_rect, ),
        ]
        self.translate_button = pgg.elements.UIButton(relative_rect=pg.Rect(190, 10, 170, 30), manager=self.manager,
                                            container=self.left_ui_rect,
                                            text="Сместить на вектор")
        [i.set_allowed_characters(list("1234567890.-")) for i in self.translate_fields]

        self.rotate_fields = [
            pgg.elements.UITextEntryLine(relative_rect=pg.Rect(10, 50, 50, 30), manager=self.manager,
                                         container=self.left_ui_rect, ),
            pgg.elements.UITextEntryLine(relative_rect=pg.Rect(70, 50, 50, 30), manager=self.manager,
                                         container=self.left_ui_rect, ),
            pgg.elements.UITextEntryLine(relative_rect=pg.Rect(130, 50, 50, 30), manager=self.manager,
                                         container=self.left_ui_rect, ),
        ]
        self.rotate_button = pgg.elements.UIButton(relative_rect=pg.Rect(190, 50, 170, 30), manager=self.manager,
                                                      container=self.left_ui_rect,
                                                      text="Повернуть по осям")
        [i.set_allowed_characters(list("1234567890.-")) for i in self.rotate_fields]

        self.scale_field = pgg.elements.UITextEntryLine(relative_rect=pg.Rect(130, 90, 50, 30), manager=self.manager,
                                                        container=self.left_ui_rect, )
        self.scale_button = pgg.elements.UIButton(relative_rect=pg.Rect(190, 90, 170, 30), manager=self.manager,
                                                   container=self.left_ui_rect,
                                                   text="Масштабировать")

    def button_events(self, event):
        """Отработка событий нажатий кнопок"""
        if event.type == pgg.UI_BUTTON_PRESSED:
            if event.ui_element == self.translate_button:
                """ПЕРЕМЕЩЕНИЕ"""
                v = []
                try:
                    v = np.array([float(i.get_text()) for i in self.translate_fields])
                except ValueError:
                    pass
                self.object.translate(v)

            if event.ui_element == self.rotate_button:
                """ПОВОРОТ"""
                al, be, ga = [self.rotate_fields[i].get_text() for i in range(3)]
                al = 0 if not al else float(al)
                be = 0 if not be else float(be)
                ga = 0 if not ga else float(ga)

                #self.object.rotate_x(al)
                t = pg.time.get_ticks()
                self.object.movement_targets["rotate_x"] = al
                self.object.movement_timers["rotate_x"] = t
                self.object.movement_targets["rotate_y"] = be
                self.object.movement_timers["rotate_y"] = t
                self.object.movement_targets["rotate_z"] = ga
                self.object.movement_timers["rotate_z"] = t

                #self.object.rotate_y(be)
                #self.object.rotate_z(ga)

            if event.ui_element == self.scale_button:
                """МАСШТАБ"""
                s = 1
                try:
                    s = float(self.scale_field.get_text())
                except ValueError:
                    pass
                self.object.scale(s)
                #self.object.movement_targets["scale"] = s
                #self.object.movement_timers["scale"] = pg.time.get_ticks()

    def get_object_from_file(self, filename):
        vertex, faces = [], []
        with open(filename) as f:
            for line in f:
                if line.startswith('v '):
                    vertex.append([float(i) for i in line.split()[1:]] + [1])
                elif line.startswith('f'):
                    faces_ = line.split()[1:]
                    faces.append([int(face_.split('/')[0]) - 1 for face_ in faces_])
        return Object3D(self, vertex, faces)

    def is_typing(self):
        return any([i.is_focused for i in self.translate_fields]) and any([i.is_focused for i in self.rotate_fields])

    def draw(self):
        self.screen.fill(pg.Color('darkslategray'))
        self.object.draw()
        self.axis.draw()
        self.manager.draw_ui(self.screen)

    def run(self):
        while True:
            self.draw()
            if not self.is_typing():
                self.camera.control()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                self.button_events(event)
                self.manager.process_events(event)
            self.manager.update(self.clock.tick(self.FPS)/1000.0)
            pg.display.set_caption(str(self.clock.get_fps()))
            pg.display.flip()
            self.clock.tick(self.FPS)


if __name__ == '__main__':
    app = SoftwareRender()
    app.run()
