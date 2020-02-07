#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
import math
import numpy as np
from enum import Enum
from random import randint


class Element(object):
    """Abstract element class"""
    def __init__(self, structure=None, shape=None):
        self.structure = structure
        if shape is None:
            self.shape = self.structure.shape
        else:
            self.shape = shape

    def rotate(self):
        self.structure = np.rot90(self.structure)
        self.shape = (self.shape[1], self.shape[0])

    @property
    def size_x(self):
        return self.shape[1]

    @property
    def size_y(self):
        return self.shape[0]


class Line(Element):
    """Line element class
    Structure is displayed as [X|X|X|X]
    """
    def __init__(self):
        super().__init__(np.array([2, 2, 2, 2]), (1, 4))

    def rotate(self):
        if self.shape[1] == 4:
            self.structure = np.array([[2], [2], [2], [2]])
        else:
            self.structure = np.array([2, 2, 2, 2])
        self.shape = (self.shape[1], self.shape[0])


class Square(Element):
    """Square element class
    Structure is displayed as [X|X]
                              [X|X]
    """
    def __init__(self):
        super().__init__(np.array([[2, 2], [2, 2]]))


class LeftZ(Element):
    """Left 'Z' element class
    Structure is displayed as [X|X| ]
                              [ |X|X]
    """
    def __init__(self):
        super().__init__(np.array([[2, 2, 0], [0, 2, 2]]))


class RightZ(Element):
    """Right 'Z' element class
    Structure is displayed as [ |X|X]
                              [X|X|]
    """
    def __init__(self):
        super().__init__(np.array([[0, 2, 2], [2, 2, 0]]))


class LeftL(Element):
    """Left 'L' element class
    Structure is displayed as [X| | ]
                              [X|X|X]
    """
    def __init__(self):
        super().__init__(np.array([[2, 0, 0], [2, 2, 2]]))


class RightL(Element):
    """Right 'L' element class
    Structure is displayed as [ | |X]
                              [X|X|X]
    """
    def __init__(self):
        super().__init__(np.array([[0, 0, 2], [2, 2, 2]]))


class UpsideT(Element):
    """Upside-down 'T' element class
    Structure is displayed as [ |X| ]
                              [X|X|X]
    """
    def __init__(self):
        super().__init__(np.array([[0, 2, 0], [2, 2, 2]]))


class Direction(Enum):
    """Enum representing both possible and actual movement on board"""
    left = 1
    down = 2
    right = 3
    up = 4


class EndException(Exception):
    pass


class Board(object):
    """Main board area class

    Number meanings:
        - 0 -> empty field
        - 1 -> field with fixed element
        - 2 -> field with moving element
    Base playground is 14 fields height and 9 wide.
    While there's element moving on board, each board access returns copy of actual state.
    Board is merged once there's no move in any direction
    """
    def __init__(self):
        self.merged = np.zeros((14, 9))  # merged board
        self.temp = self.merged.copy()  # temporary board to move elements on
        self.available = [Line, LeftL, RightL, LeftZ, RightZ, UpsideT, Square]  # available element classes
        self.__current_element = None  # currently moving element instance
        self.__next_element = self.instantiate()  # currently moving element instance
        self.__coord = [0, 3]  # actual's element's top-left corner

    @property
    def current(self):
        return self.temp

    @property
    def small_board(self):
        board = np.zeros((4,4))
        self.__insert_internal__(self.__next_element, [0,0], board)
        return board

    def instantiate(self):
        """Create random element instance
        :return: Element instance
        """
        return self.available[randint(0, 6)]()

    def add(self):
        """Add new randomly generated element and insert it in beginning index"""
        self.__current_element = self.__next_element
        self.__next_element = self.instantiate()
        self.check_end()
        self.insert(self.__current_element)  # insert new element on board

    def check_end(self):
        to_insert = np.zeros((14, 9))
        self.__insert_internal__(self.__next_element, [0, 3], to_insert)
        if len(self.intersection(self.where_to_coords(self.merged, 1), self.where_to_coords(to_insert, 2))) is not 0:
            raise EndException

    def can_add(self):
        """Check if there isn't any existing moving element on board and new can be added"""
        return self.__current_element is None

    def insert(self, element, index=None):
        """Insert element in specific place on brand new copy of merged board

        :param element: element to put on board
        :type element: Element
        :param index: coordinates of top-left corner
        :type index: list

        """
        self.temp = self.merged.copy()
        if index is None:
            index = self.__coord
        self.__insert_internal__(element, index, self.temp)

    def __insert_internal__(self, element, index, array):
        l1 = self.where_to_coords(array, 1)
        array[index[0]:index[0]+element.size_y, index[1]:index[1]+element.size_x] = element.structure
        l2 = self.where_to_coords(array, 0)
        for coord in self.intersection(l1, l2):  # eliminate bug with replacing 1's with 0's from moving element
            array[coord[0], coord[1]] = 1

    @staticmethod
    def intersection(lst1, lst2):
        return [value for value in lst1 if value in lst2]

    def move(self, direction):
        """Move currently moving element in specified direction

        :param direction: desired move direction
        :type direction: Direction
        """
        if self.__current_element is not None:
            coords = self.where_to_coords(self.temp, 2)
            if self.can_move(direction, coords):
                if direction == Direction.left:
                    self.__coord = [self.__coord[0], self.__coord[1] - 1]
                    self.insert(self.__current_element, self.__coord)
                elif direction == Direction.right:
                    self.__coord = [self.__coord[0], self.__coord[1] + 1]
                    self.insert(self.__current_element, self.__coord)
                elif direction == Direction.up:
                    self.__current_element.rotate()
                    if 9 - self.__coord[1] < self.__current_element.size_x:
                        self.__coord = [self.__coord[0], 9 - self.__current_element.size_x]
                    self.insert(self.__current_element, self.__coord)
                else:
                    self.__coord = [self.__coord[0] + 1, self.__coord[1]]
                    self.insert(self.__current_element, self.__coord)
            else:
                if direction == Direction.down:
                    return self.merge()
        return 0

    @staticmethod
    def where_to_coords(array, num):
        """Return all coordinates with current number"""
        raw = np.where(array == num)
        return list(zip(raw[0], raw[1]))

    def can_move(self, direction, coords):
        if direction == Direction.left:
            for coord in coords:
                if coord[1] == 0:
                    return False
                if self.temp[coord[0], coord[1] - 1] == 1:
                    return False
            return True
        elif direction == Direction.right:
            for coord in coords:
                if coord[1] == 8:
                    return False
                if self.temp[coord[0], coord[1] + 1] == 1:
                    return False
            return True
        for coord in coords:
            if coord[0] == 13:
                return False
            if self.temp[coord[0] + 1, coord[1]] == 1:
                return False
        return True

    def merge(self):
        self.merged = self.temp
        self.merged = np.where(self.merged == 2, 1, self.merged)
        self.__coord = [0, 3]
        self.__current_element = None
        return self.clear_full_row()

    def clear_full_row(self):
        cleared = 0
        for row in range(14):
            if np.count_nonzero(self.merged[row]) == 9:
                self.merged[1:row+1, 0:9] = self.merged[0:row, 0:9]
                self.merged[0] = np.zeros(9)
                cleared += 1
        return cleared


class Tile(object):
    """pyGame's Surface facade to provide fixed coordinate"""
    def __init__(self, coords, offset, size=40):
        """
        :param coords: position on board
        :param offset: boards top-left corner
        """
        self.surface = pygame.Surface((size, size))
        self.coords = coords
        self.offset = offset
        self.size = size
        self.paint(Tile.colors[0])

    def paint(self, value):
        pygame.draw.rect(self.surface, value, (2, 2, self.size-4, self.size-4))

    def blit(self, screen, value):
        self.paint(Tile.colors[value])
        screen.blit(self.surface, (self.coords[0] * self.size + self.offset[0],
                                   self.coords[1] * self.size + self.offset[1]))

    colors = {0: (100, 80, 60), 1: (176, 150, 123), 2: (70, 151, 176)}


class BoardController(object):
    """Translate numpy array to print-ready surfaces"""
    def __init__(self):
        self.__board = Board()
        self.tiles = []
        for x in range(9):
            for y in range(14):
                self.tiles.append(Tile((x, y), (20, 20)))
        self.small_tiles = []
        for x in range(4):
            for y in range(4):
                self.small_tiles.append(Tile((x, y), (440, 400), 30))

    def repaint(self, screen):
        for tile in self.tiles:
            tile.blit(screen, self.__board.current[tile.coords[1]][tile.coords[0]])  # inverted!
        for tile in self.small_tiles:
            tile.blit(screen, self.__board.small_board[tile.coords[1]][tile.coords[0]])  # also inverted

    def insert(self):
        self.__board.add()

    def can_add(self):
        return self.__board.can_add()

    def move(self, direction):
        return self.__board.move(direction)


class Game(object):
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode((640, 640))
        background = pygame.Surface(screen.get_size())  # create surface for background
        background.fill((60, 90, 99))  # fill the background
        background = background.convert()  # convert surface for faster blitting

        pygame.display.set_caption("Tetris")

        self.points = 0
        self.cleared = 0

        self.controller = BoardController()
        self.screen = screen
        self.background = background
        self.blit()

    def __score__(self):
        text_color = (176, 132, 88)
        font = pygame.font.Font(None, 72)
        return font.render("{:05d}".format(self.points), True, text_color)

    def __custom__(self, custom_text):
        text_color = (176, 150, 123)
        font = pygame.font.Font(None, 48)
        return font.render(custom_text, True, text_color)

    def __add_points__(self, result):
        if result > 0:
            self.cleared += result
            self.points += math.factorial(result) * 100

    def blit(self):
        self.screen.blit(self.background, (0, 0))  # blit the background on screen (overwriting all)
        self.controller.repaint(self.screen)
        self.screen.blit(self.__score__(), (440, 100))

    def run(self):
        clock = pygame.time.Clock()  # create pygame clock object
        mainloop = True
        fps = 144
        interval = 1000
        elapsed = 0
        self.controller.insert()

        while mainloop:
            milliseconds = clock.tick(fps)  # milliseconds passed since last frame
            elapsed += milliseconds
            if elapsed >= interval - self.cleared * 25:  # next step to be done
                elapsed = 0
                self.__add_points__(self.controller.move(Direction.down))
                if self.controller.can_add():
                    try:
                        self.controller.insert()
                    except EndException:
                        mainloop = self.subloop()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # window closed by user
                    mainloop = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        mainloop = False
                    elif event.key == pygame.K_LEFT:
                        self.controller.move(Direction.left)
                    elif event.key == pygame.K_RIGHT:
                        self.controller.move(Direction.right)
                    elif event.key == pygame.K_DOWN:
                        self.__add_points__(self.controller.move(Direction.down))
                    elif event.key == pygame.K_UP:
                        self.controller.move(Direction.up)
            self.blit()
            pygame.display.flip()
        pygame.quit()  # shutdown all remaining threads

    def subloop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # window closed by user
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_RETURN:
                        self.points = 0
                        self.cleared = 0
                        self.controller = BoardController()
                        return True
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.__custom__("Zdobyto:"), (200, 250))
            self.screen.blit(self.__score__(), (300, 300))
            self.screen.blit(self.__custom__("ENTER - nowa gra"), (200, 400))
            self.screen.blit(self.__custom__("ESC - wyjdź"), (200, 450))
            pygame.display.flip()


if __name__ == '__main__':
    game = Game()
    game.run()
