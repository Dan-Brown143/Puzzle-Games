import pygame
import random
import json
import sys
from typing import List, Dict, Tuple, Optional 

#Initialise pygame
pygame.init()

#Constants
windowWidth = 200
windowHeight = 800
cellSize = 40
gridSize = 15
gridOffsetX = 50
gridOffsetY = 100

#Light Mode Colours
Light_Colours = {
    'background': (250, 250, 250),
    'grid_bg': (255, 255, 255),
    'grid_lines': (200, 200, 200),
    'text': (30, 30, 30),
    'cell_filled': (240, 240, 240),
    'cell_blocked': (50, 50, 50),
    'cell_selected': (100, 150, 255),
    'cell_correct': (144, 238, 144),
    'cell_incorrect': (255, 160, 160),
    'number_text': (100, 100, 100),
    'button': (70, 130, 180),
    'button_hover': (100, 160, 210),
    'button_text': (255, 255, 255),
}

#Dark Mode Colours

Dark_Colours = {
    'background': (30, 30, 35),
    'grid_bg': (45, 45, 50),
    'grid_lines': (70, 70, 75),
    'text': (230, 230, 230),
    'cell_filled': (55, 55, 60),
    'cell_blocked': (20, 20, 25),
    'cell_selected': (80, 120, 200),
    'cell_correct': (60, 140, 60),
    'cell_incorrect': (180, 60, 60),
    'number_text': (150, 150, 150),
    'button': (60, 100, 150),
    'button_hover': (80, 120, 170),
    'button_text': (240, 240, 240),
}

