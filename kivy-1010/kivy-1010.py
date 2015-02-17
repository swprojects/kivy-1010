# -*- coding: utf-8 -*-

from random import randint

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.config import Config
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty


SHAPES = [dict(cols=5, rows=1, array=[1, 1, 1, 1, 1]),
          dict(cols=4, rows=1, array=[1, 1, 1, 1]),
          dict(cols=3, rows=1, array=[1, 1, 1]),
          dict(cols=2, rows=1, array=[1, 1]),
          dict(cols=1, rows=5, array=[1, 1, 1, 1, 1]),
          dict(cols=1, rows=4, array=[1, 1, 1, 1]),
          dict(cols=1, rows=3, array=[1, 1, 1]),
          dict(cols=1, rows=2, array=[1, 1]),
          dict(cols=1, rows=1, array=[1]),

          dict(cols=2, rows=2, array=[1, 1, 1, 1]),
          dict(cols=3, rows=3, array=[1, 1, 1,
                                      1, 1, 1,
                                      1, 1, 1]),

          dict(cols=2, rows=2, array=[1, 1, 0, 1]),
          dict(cols=2, rows=2, array=[1, 0, 1, 1]),
          dict(cols=2, rows=2, array=[1, 1, 1, 0]),
          dict(cols=2, rows=2, array=[0, 1, 1, 1]),

          dict(cols=3, rows=3, array=[1, 1, 1,
                                      1, 0, 0,
                                      1, 0, 0]),
          dict(cols=3, rows=3, array=[1, 1, 1,
                                      0, 0, 1,
                                      0, 0, 1]),
          dict(cols=3, rows=3, array=[1, 0, 0,
                                      1, 0, 0,
                                      1, 1, 1]),
          dict(cols=3, rows=3, array=[0, 0, 1,
                                      0, 0, 1,
                                      1, 1, 1])]

COLOR = [get_color_from_hex('DC6554'),
         get_color_from_hex('5BBEE5'),
         get_color_from_hex('EC9449'),
         get_color_from_hex('FAC73D'),
         get_color_from_hex('97DB55'),
         get_color_from_hex('58CB85'),
         get_color_from_hex('5AC986'),
         get_color_from_hex('7B8ED4'),
         get_color_from_hex('E86981'),
         get_color_from_hex('ED954B')]


def get_color(obj):
    obj_color = filter(lambda x: str(x).find('Color') != -1, obj.canvas.before.children)[0]
    return obj_color


def set_color(obj, color):
    obj_color = get_color(obj)
    obj_color.rgba = color


def shape_on_box(shape, label_index):
    shape_box_on_board = []
    line_left = (label_index / 10) * 10
    if shape.cols <= (label_index - line_left + 1):
        for i in range(0, shape.rows):
            row = range(label_index + i * 10, (label_index + i * 10) - shape.cols, -1)
            row.reverse()
            shape_box_on_board.extend(row)
    return shape_box_on_board


def check_occupied(board, board_row, shape_objs):
    occupied = False
    if not board_row:
        occupied = True
    index = 0
    for i in board_row:
        board_label = board.children[i]
        color = get_color(board_label)
        if color.rgba != get_color_from_hex('E2DDD5'):
            if str(shape_objs[index]).find('Label') != -1:
                occupied = True
        index += 1
    return occupied


def get_lines(indexes):
    lines = []
    for i in indexes:
        tmp_cols = range(i % 10, 100, 10)
        tmp_rows = range((i / 10) * 10, (i / 10) * 10 + 10, 1)
        try:
            lines.index(tmp_cols)
        except ValueError:
            lines.append(tmp_cols)
        try:
            lines.index(tmp_rows)
        except ValueError:
            lines.append(tmp_rows)
    return lines


def free_positions(board, shape):
    pos_on_board = filter(lambda x: get_color(x).rgba == get_color_from_hex('E2DDD5'), board.children)
    place = None
    for pos in pos_on_board:
        label_index = board.children.index(pos)
        shape_objs = shape.children
        try:
            shape_box_on_board = shape_on_box(shape, label_index)
            occupied = check_occupied(board, shape_box_on_board, shape_objs)
            if occupied:
                raise IndexError
            place = True
            break
        except:
            pass
    return bool(place)


class Shape(GridLayout):
    def __init__(self):
        super(Shape, self).__init__()
        shape = SHAPES[randint(0, len(SHAPES) - 1)]
        color = COLOR[randint(0, len(COLOR) - 1)]
        self.rows = shape['rows']
        self.cols = shape['cols']
        self.array = shape['array']
        self.color = color

    def get_colors(self, *args):
        result = []
        for ch in self.children:
            if str(ch).find('Label') != -1:
                result.append(get_color(ch))
        return result


class CustomAnimation(Animation):
    def on_complete(self, widget):
        super(CustomAnimation, self).stop(widget)
        self.stop(widget)
        if str(widget).find('Color') == -1:
            scatters = widget.parent
            active_shapes = map(lambda x: x[0],
                                filter(lambda x: x, map(lambda x: x.children[0].children, scatters.children)))

            possible_places = False
            for shape in active_shapes:
                result = free_positions(scatters.parent.board, shape)
                possible_places = possible_places or result
            if not possible_places:
                CustomScatter.change_movement(scatters.parent)


class CustomScatter(ScatterLayout):
    def on_transform_with_touch(self, touch):
        super(CustomScatter, self).on_transform_with_touch(touch)
        if self.do_translation_x and self.do_translation_y:
            shape = self.children[0].children[0]
            for label in shape.children:
                label.size = (30, 30)
            shape.spacing = (3, 3)

    def on_bring_to_front(self, touch):
        super(CustomScatter, self).on_bring_to_front(touch)

    def on_touch_up(self, touch):
        super(CustomScatter, self).on_touch_up(touch)
        self.reset_shape()
        self.position_calculation()

    def on_touch_down(self, touch):
        super(CustomScatter, self).on_touch_down(touch)

    def reset_shape(self):
        try:
            if self.do_translation_x and self.do_translation_y:
                shape = self.children[0].children[0]
                for label in shape.children:
                    label.size = (25, 25)
                shape.spacing = (1, 1)
        except IndexError:
            pass

    def position_calculation(self):
        try:
            board = self.parent.parent.board
            labels = board.children
            obj_x, obj_y = self.pos
            flag = False
            for label in labels:
                pos_x, pos_y = label.pos
                lbl_wid, lbl_hei = label.size
                pos_x_check = pos_x <= obj_x <= pos_x + lbl_wid
                pos_y_check = pos_y <= obj_y <= pos_y + lbl_hei
                if pos_x_check and pos_y_check:
                    # position is possible or not?
                    lbl_index = board.children.index(label)
                    line_left = (lbl_index / 10) * 10
                    shape = self.children[0].children[0]
                    if shape.cols <= (lbl_index - line_left + 1):
                        self.get_colored_area(board, label)
                        flag = True
                        break
            if not flag:
                raise IndexError
        except AttributeError:
            pass
        except IndexError:
            anim = CustomAnimation(x=self.pre_pos[0], y=self.pre_pos[1], t='linear', duration=.2)
            anim.start(self)

    def get_colored_area(self, board, label, **kwargs):
        try:
            shape = kwargs.get('shape', self.children[0].children[0])
            shape_objs = shape.children
            shape_color = shape.color
            label_index = board.children.index(label)
            shape_box_on_board = shape_on_box(shape, label_index)
            occupied = check_occupied(board, shape_box_on_board, shape_objs)

            # Set color and remove shape
            if not occupied:
                index = plus_score = 0
                board_labels = []
                for i in shape_objs:
                    if str(i).find('Label') != -1:
                        board_label = board.children[shape_box_on_board[index]]
                        set_color(board_label, shape_color)
                        plus_score += 1
                        board_labels.append(shape_box_on_board[index])

                    index += 1

                parent = self.children[0]
                parent.clear_widgets()
                root_class = parent.parent.parent.parent
                Clock.schedule_once(lambda dt: self.update_score(root_class, plus_score), .01)
                lines = get_lines(board_labels)
                self.clear_lines(lines)
                if not filter(lambda x: x, map(lambda x: x.children[0].children, parent.parent.parent.children)):
                    root_class.coming_shapes()
            else:
                raise IndexError
        except IndexError:
            anim = CustomAnimation(x=self.pre_pos[0], y=self.pre_pos[1], t='linear', duration=.2)
            anim.start(self)

    def update_score(self, scored_class, point):
        if point > 0:
            scored_class.score += 1
            Clock.schedule_once(lambda dt: self.update_score(scored_class, point - 1), .01)

    def clear_lines(self, lines):
        board = self.parent.parent.board
        for line in lines:
            flag = True
            colored_labels = []
            for index in line:
                label = board.children[index]
                color = filter(lambda x: str(x).find('Color') != -1, label.canvas.before.children)[0]
                colored_labels.append(color)
                if color.rgba == get_color_from_hex('E2DDD5'):
                    flag = False
                    break
            if flag:
                for i in colored_labels:
                    anim = CustomAnimation(rgba=get_color_from_hex('E2DDD5'), d=.5, t='in_circ')
                    anim.start(i)
                Clock.schedule_once(lambda dt: self.update_score(board.parent, 10), .01)

    @staticmethod
    def change_movement(board):
        scatters = [board.comingLeft, board.comingMid, board.comingRight]
        for scatter in scatters:
            scatter.do_translation_x = not scatter.do_translation_x
            scatter.do_translation_y = not scatter.do_translation_y


class Kivy1010(GridLayout):
    score = NumericProperty(0)

    def __init__(self):
        super(Kivy1010, self).__init__()
        self.refresh_board()
        self.coming_shapes()

    def refresh_board(self):
        self.board.clear_widgets()
        for i in range(0, 100):
            label = Label(color=(0, 0, 0, 1), size_hint=(None, None), size=(30, 30))
            self.board.add_widget(label)

    def coming_shapes(self):

        scatters = [self.comingLeft, self.comingMid, self.comingRight]
        for scatter in scatters:
            scatter.clear_widgets()
            scatter.pos = scatter.pre_pos
        for scatter in scatters:
            shape = Shape()
            width = 0
            height = 0
            index = 0
            for i in shape.array:
                if i == 1:
                    box = Label(size_hint=(None, None), size=(25, 25), index=index)
                    set_color(box, get_color_from_hex('F0F0F0'))

                    # color = filter(lambda x: str(x).find('Color') != -1, box.canvas.before.children)[0]
                    #color.rgba = shape.color
                else:
                    box = Image(source='assets/trans.png', size_hint=(None, None), size=(25, 25), index=index)
                index += 1
                if index % shape.cols == 0:
                    height += 26

                if index % shape.rows == 0:
                    width += 26
                shape.add_widget(box)
            shape.spacing = (1, 1)
            scatter.size_hint = (None, None)
            scatter.size = (width, height)
            scatter.add_widget(shape)
            label_colors = shape.get_colors()
            for color in label_colors:
                anim = CustomAnimation(rgba=shape.color, d=.3, t='in_circ')
                anim.start(color)

                #shape.set_color()


class KivyMinesApp(App):
    def __init__(self, **kwargs):
        super(KivyMinesApp, self).__init__(**kwargs)
        Builder.load_file('assets/1010.kv')
        self.title = 'Kivy 1010'
        # self.icon = 'assets/mine.png'

    def build(self):
        mines = Kivy1010()
        return mines


if __name__ == '__main__':
    Window.clearcolor = (get_color_from_hex('F0F0F0'))
    Window.size = (520, 600)
    Config.set('kivy', 'desktop', 1)
    Config.set('graphics', 'fullscreen', 0)
    Config.set('graphics', 'resizable', 0)
    KivyMinesApp().run()