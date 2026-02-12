import pygame
import random
import json
import sys
from typing import List, Dict, Tuple, Optional 

#Initialise pygame
pygame.init()

#Constants
WINDOW_WIDTH = 200
WINDOW_HEIGHT = 800
CELL_SIZE = 40
GRID_SIZE = 15
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 100

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

class CrosswordWord:
    def __init__(self, word: str, clue: str, row: int, col: int, direction: str, number: int):
        self.word = word.upper()
        self.clue = clue
        self.row = row
        self.col = col
        self.direction = direction
        self.number = number

class CrosswordGenerator:
    def __init__(self, words_data: List[Dict], grid_size: int = 15):
        self.words_data = words_data
        self.grid_size = grid_size
        self.grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        self.placed_words: List[CrosswordWord] = []
        self.word_number = 1

    def can_place_word(self, word: str, row: int, col: int, direction: str) -> bool:
        #Check if a word can be placed
        if direction == 'across':
            if col + len(word) > self.grid_size:
                return False
            #Check if the cell before or after is blocked
            if col > 0 and self.grid[row][col - 1] != ' ' and self.grid[row][col - 1] != '#':
                return False
            if col + len(word) < self.grid_size and self.grid[row][col + len(word)] != ' ' and self.grid[row][col + len(word)] != '#':
                return False
            
            for i, letter in enumerate(word):
                current_col = col + i
                cell = self.grid[row][current_col]

                if cell != ' ' or cell == '#':
                    return False
                
                #Check perpendicular issues
                if cell == ' ' or cell == '#':
                    if row > 0 and self.grid[row - 1][current_col] not in [' ', '#']:
                        return False
                    if row < self.grid_size - 1 and self.grid[row + 1][current_col] not in [' ', '#']:
                        return False
                
        else: #Down
            if row + len(word) > self.grid_size:
                return False
            #Check if the cell before and after is blocked
            if row > 0 and self.grid[row - 1][col] != ' ' and self.grid[row-1][col] != '#':
                return False
            if row + len(word) < self.grid_size and self.grid[row + len(word)][col] != ' ' and self.grid[row+len(word)][col] != '#':
                return False
            
            for i, letter in enumerate(word):
                current_row = row + i
                cell = self.grid[current_row][col]

                if cell != ' ' and cell != letter and cell != '#':
                    return False
                
                #Check perpendicular issues
                if cell == ' ' or cell == '#':
                    if col > 0 and self.grid[current_row][col - 1] not in [' ', '#']:
                        return False
                    if col < self.grid_size - 1 and self.grid[current_row][col + 1] not in [' ', '#']:
                        return False

        return True

    def place_word(self, word: str, clue: str, row: int, col: int, direction: str):
        number = self.word_number
        self.word_number += 1

        if direction == 'across':
            for i, letter in enumerate(word):
                self.grid[row][col + i] = letter
        else: 
            for i, letter in enumerate(word):
                self.grid[row + i][col] = letter

        self.placed_words.append(CrosswordWord(word, clue, row, col, direction, number))

    def find_intersections(self, word: str) -> List[Tuple[int, int, str]]:
        positions = []

        for placed_word in self.place_word:
            for i, letter1 in enumerate(word):
                for j, letter2 in enumerate(placed_word.word):
                    if letter1 == letter2:
                        if placed_word.direction == 'across':
                            new_row = placed_word.row - i
                            new_col = placed_word.col + j
                            if 0 <= new_row < self.grid_size:
                                positions.append((new_row, new_col, 'down'))
                        else:
                            new_row = placed_word.row + j
                            new_col = placed_word.col - i
                            if 0 <= new_col < self.grid_size:
                                positions.append((new_row, new_col, 'across')) 

        return positions
    
    def generate(self, num_words: int = 15) -> bool:
        if not self.words_data or num_words == 0:
            return False
        
        #Select random words
        selected = random.sample(self.words_data, min(num_words, len(self.words_data)))
        #Sort them by length so the longer words are placed in first
        selected.sort(key=lambda x: len(x['word']), reverse=True)

        #First word goes in the center
        first_word_data = selected[0]
        first_word = first_word_data['word'].upper()
        start_row = self.grid_size // 2
        start_col = (self.grid_size - len(first_word)) // 2

        self.place_word(first_word, first_word_data['clue'], start_row, start_col, 'across', )

        #Place the rest
        placed_count = 1
        attempts_per_word = 100

        for word_data in selected[1:]:
            word = word_data['word'].upper()
            clue = word_data['clue']
            placed = False

            #Try to intersect first
            positions = self.find_intersections(word)
            random.shuffle(positions)

            for row, col, direction in positions[:attempts_per_word]:
                if self.can_place_word(word, row, col, direction):
                    self.place_word(word, clue, row, col, direction)
                    placed = True
                    placed_count += 1
                    break
            
            if not placed and placed_count < 5:
                #Try random positions
                for _ in range(attempts_per_word):
                    row = random.randint(0, self.grid_size - 1)
                    col = random.randint(o, self.grid - 1)
                    direction = random.choice(['across', 'down'])

                    if self.can_place_word(word, row, col, direction):
                        self.place_word(word, clue, row, col, direction)
                        placed = True
                        placed_count += 1
                        break

        self.fill_blocked_cells()

        return placed_count >= 5 #Want at least 5 words for a puzzle
    
    def fill_blocked_cells(self):
        #Fill the empty cells on the grid with blocked markers
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] == ' ':
                    self.grid[row][col] = '#'

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, screen, colours):
        colour = colours['button_hover'] if self.hovered else colours['button']
        pygame.draw.rect(screen, colour, self.rect, border_radius = 5)
        pygame.draw.rect(screen, colours['text'], self.rect, 2, border_radius = 5)
        
        font = pygame.font.Font(None, 28)
        text_surface = font.render(self.text, True, colours['button_text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.pygame.Rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.action()

class Checkbox:
    def __init__(self, x: int, y: int, text: str, checked: bool = False):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.text = text
        self.checked - checked
        self.hovered = False

    def draw(self, screen, colours):
        #Draw box
        pygame.draw.rect(screen, colours['grid_bg'], self.rect)
        pygame.draw.rect(screen, colours['text'], self.rect, 2)

        #Draw checkmarks if checked
        if self.checked:
            pygame.draw.line(screen, colours['text'],
                             (self.rect.x + 4, self.rect.y + 10),
                             (self.rect.x + 8, self.rect.y + 16), 3)
            pygame.draw.line(screen, colours['text'],
                             (self.rect.x + 4, self.rect.y + 16),
                             (self.rect.x + 16, self.rect.y + 4), 3)
            
        #Draw text
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, colours['text'])
        screen.blit(text_surface, (self.rect.x + 30, self.rect.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.pygame.Rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.pygame.Rect.collidepoint(event.pos):
                self.checked = not self.checked