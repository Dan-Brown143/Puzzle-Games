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
LIGHT_COLOURS = {
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

DARK_COLOURS = {
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
                    col = random.randint(0, self.grid - 1)
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

class CrosswordGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Crossword Puzzle")
        self.clock = pygame.time.clock()

        #Theme

        self.dark_mode = False
        self.colours = LIGHT_COLOURS.copy()
        
        #Load words
        self.all_words = self.load_words()
        self.categories = list(set(word['category'] for word in self.all_words))

        #Game state
        self.state = 'menu'
        self.generator = None
        self.user_grid = None
        self.selected_cell = None
        self.selected_word = None
        
        #UI
        self.create_menu_ui()

    def load_words(self) -> List[Dict]:
        try:
            with open('crossword_words.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            #Defaults if the word file doesnt exist
            return [
                {"word": "python", "clue": "Popular programming language", "category": "Technology"},
                {"word": "game", "clue": "Something played for fun", "category": "Entertainment"},
                {"word": "puzzle", "clue": "Brain teaser", "category": "Entertainment"},
                {"word": "computer", "clue": "Electronic device for processing data", "category": "Technology"},
                {"word": "music", "clue": "Organized sound", "category": "Arts"},
                {"word": "science", "clue": "Study of the natural world", "category": "Education"},
                {"word": "history", "clue": "Study of past events", "category": "Education"},
                {"word": "guitar", "clue": "Six-stringed instrument", "category": "Arts"},
                {"word": "soccer", "clue": "Popular sport played with feet", "category": "Sports"},
                {"word": "basketball", "clue": "Sport with hoops and a ball", "category": "Sports"},
                {"word": "painting", "clue": "Art created with colors", "category": "Arts"},
                {"word": "novel", "clue": "Long fictional story", "category": "Entertainment"},
                {"word": "ocean", "clue": "Large body of salt water", "category": "Nature"},
                {"word": "mountain", "clue": "Large natural elevation", "category": "Nature"},
                {"word": "forest", "clue": "Large area covered with trees", "category": "Nature"},
            ]
        
    def create_menu_ui(self):
        self.category_checkboxes = []
        y_offset = 200
        for i, category in enumerate(self.categories):
            checkbox = Checkbox(100, y_offset + i * 40, category, checked=False)
            self.category_checkboxes.append(checkbox)

        self.start_button = Button(100, y_offset + len(self.categories) * 40 + 40, 200, 50, "Start Game", self.start_game)
        self.theme_button = Button(320, y_offset + len(self.categories) * 40 + 40, 200, 50, "Toggle Theme", self.toggle_theme)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.colours = DARK_COLOURS.copy() if self.dark_mode else LIGHT_COLOURS.copy()

    def start_game(self):
        selected_categories = [cb.text for cb in self.category_checkboxes if cb.checked]

        if selected_categories:
             available_words = [w for w in self.all_words if w['category'] in selected_categories]
        else:
            available_words = self.all_words

        if not available_words:
            print("No words are available for the selected categories")
            return
        
        self.generator = CrosswordGenerator(available_words, GRID_SIZE)
        success = self.generator.generate(num_words=12)

        if success:
            self.user_grid = [['' if self.generator.grid[r][c] != '#' else '#'
                               for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
            self.selected_cell = None
            self.selected_word = None
            self.state = 'playing'
        else:
            print("Failed to generate the puzzle, trying again")
            self.start_game()

    def draw_menu(self):
        self.screen.fill(self.colours['background'])

        #Title
        font_title = pygame.font.Font(None, 64)
        title = font_title.render("Crossword Puzzle", True, self.colours['text'])
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))

        #Instructions
        font_small = pygame.font.Font(None, 28)
        instructions = font_small.render("Select categories (or none for any word):", True, self.colours['text'])
        self.screen.blit(instructions, (100, 150))

        #Draw the checkboxes
        for checkbox in self.category_checkboxes:
            checkbox.draw(self.screen, self.colours)

        #Draw the buttons
        self.start_button.draw(self.screen, self.colours)
        self.theme_button.draw(self.screen, self.colours)

    def draw_grid(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE
                cell = self.generator.grid[row][col]

                if cell == '#':
                    pygame.draw.rect(self.screen, self.colours['cell_blocked'],
                                     (x, y, CELL_SIZE, CELL_SIZE))
                else:
                    colour = self.colours['grid_bg']

                    if self.selected_cell and self.selected_cell == (row, col):
                        colour = self.colours['cell_selected']
                    elif self.selected_word:
                        word = self.selected_word
                        if word.direction == 'across':
                            if row == word.row and word.col <= col < word.col + len(word.word):
                                colour = self.colours['cell_filled']
                        else:
                            if col == word.col and word.row <= row < word.row + len(word.word):
                                colour = self.colours['cell_filled']

                pygame.draw.rect(self.screen, colour, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, self.colours['grid_lines'],
                                 (x, y, CELL_SIZE, CELL_SIZE), 1)
                
                #Draw users letter
                user_letter = self.user_grid[row][col]
                if user_letter and user_letter != '#':
                    font = pygame.font.Font(None, 32)
                    if user_letter == cell:
                        text_colour = self.colours['text']
                    else:
                        text_colour = self.colours['cell_incorrect']
                    text = font.render(user_letter, True, text_colour)
                    text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                    self.screen.blit(text, text_rect)

                #Draw word numbers
                for word in self.generator.placed_words:
                    if word.row == row and word.col == col:
                        font_small = pygame.font.Font(None, 18)
                        number = font_small.render(str(word.number), True, self.colours['number_text'])
                        self.screen.blit(number, (x + 2, y + 2))

    def draw_clues(self):
        clue_x = GRID_OFFSET_X + GRID_SIZE * CELL_SIZE + 40
        clue_y = GRID_OFFSET_Y

        font_title = pygame.font.Font(None, 32)
        font_clue = pygame.font.Font(None, 22)

        #Separate the across clues from the down clues
        across_words = [w for w in self.generator.placed_words if w.direction == 'across']
        down_words = [w for w in self.generator.placed_words if w.direction == 'down']

        across_words.sort(key=lambda w: w.number)
        down_words.sort(key=lambda w: w.number)

        #Draw the across clues
        title = font_title.render("Across", True, self.colours['text'])
        self.screen.blit(title, (clue_x, clue_y))
        y = clue_y + 40

        for word in across_words:
            if y > WINDOW_HEIGHT - 40:
                break
            clue_colour = self.colours['button'] if self.selected_word == word else self.colours['text']
            clue_text = f"{word.number}. {word.clue}"

            max_width = WINDOW_WIDTH - clue_x - 20
            words_in_clue = clue_text.split()
            lines = []
            current_line = []

            for word_str in words_in_clue:
                test_line = ' '.join(current_line + [word_str])
                if font_clue.size(test_line)[0] <= max_width:
                    current_line.append(word_str)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word_str]
            if current_line:
                lines.append(' '.join(current_line))

            for line in lines:
                text = font_clue.render(line, True, clue_colour)
                self.screen.blit(text, (clue_x, y))
                y += 25
            y += 5

        #Draw the down clues
        y += 20
        if y < WINDOW_HEIGHT - 40:
            title = font_title.render("Down", True, self.colours['text'])
            self.screen.blit(title, (clue_x, y))
            y += 40

            for word in down_words:
                if y > WINDOW_HEIGHT - 40:
                    break
                clue_colour = self.colours['button'] if self.selected_word == word else self.colours['text']
                clue_text = f"{word.number}. {word.clue}"

                max_width = WINDOW_WIDTH - clue_x - 20
                words_in_clue = clue_text.split()
                lines = []
                current_line = []

                for word_str in words_in_clue:
                    test_line = ' '.join(current_line + [word_str])
                    if font_clue.size(test_line)[0] <= max_width:
                        current_line.append(word_str)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word_str]
                if current_line:
                    lines.append(' '.join(current_line))

                for line in lines:
                    text = font_clue.render(line, True, clue_colour)
                    self.screen.blit(text, (clue_x, y))
                    y += 25
                y += 5

    def draw_controls(self):
        font = pygame.font.Font(None, 24)
        controls = [
            "Click a cell to select",
            "Type a letter to fill",
            "Backspace to delete",
            "Arrow keys to navigate",
            "ESC for the menu"
        ]

        y = GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE + 20
        for control in controls:
            text = font.render(control, True, self.colours['text'])
            self.screen.blit(text, (GRID_OFFSET_X, y))
            y += 30

    def check_completion(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.generator.grid[row][col] != '#':
                    if self.user_grid[row][col] != self.generator.grid[row][col]:
                        return False
        return True
    
    def draw_complete_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(self.colours['background'])
        self.screen.blit(overlay, (0, 0))

        font_title = pygame.font.Font(None, 72)
        font_sub = pygame.font.Font(None, 36)

        title = font_title.render("Congratulations", True, self.colours['text'])
        subtitle = font_sub.render("Press ESC for the menu or SPACE for a new game", True, self.colours['text'])

        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, WINDOW_HEIGHT // 2 + 20))

    def handle_cell_click(self, pos):
        x, y = pos
        col = (x - GRID_OFFSET_X) // CELL_SIZE
        row = (y - GRID_OFFSET_Y) // CELL_SIZE

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            if self.generator.grid[row][col] != '#':
                self.selected_cell = (row, col)

                for word in self.generator.placed_words:
                    if word.direction == 'across':
                        if row == word.row and word.col <= col < word.col + len(word.word):
                            self.selected_word = word
                            return
                    else:
                        if col == word.col and word.row <= row < word.row + len(word.word):
                            self.selected_word = word
                            return
                        
    def handle_key_inputs(self, event):
        if not self.selected_cell:
            return
        
        row, col = self.selected_cell

        if event.key == pygame.K_BACKSPACE:
            self.user_grid[row][col] = ''
        elif event.key == pygame.K_DELETE:
            self.user_grid[row][col] = ''
        elif event.unicode.isalpha():
            self.user_grid[row][col] = event.unicode.upper()
            self.move_selection(1, 0)
        elif event.key == pygame.K_LEFT:
            self.move_selection(0, -1)
        elif event.key == pygame.K_RIGHT:
            self.move_selection(0, 1)
        elif event.key == pygame.K_UP:
            self.move_selection(-1, 0)
        elif event.key == pygame.K_DOWN:
            self.move_selection(1, 0)

    def move_selection(self, row_delta, col_delta):
        if not self.selected_cell:
            return
        
        row, col = self.selected_cell
        new_row = row + row_delta
        new_col = col + col_delta

        if self.selected_word:
            if self.selected_word.direction == 'across' and col_delta != 0:
                word_start_col = self.selected_word.col
                word_end_col = self.selected_word.col + len(self.selected_word.word) - 1
                if word_start_col <= new_col <= word_end_col:
                    self.selected_cell = (new_row, new_col)
                    return
            elif self.selected_word.direction == 'down' and row_delta != 0:
                word_start_row = self.selected_word.row
                word_end_row = self.selected_word.row + len(self.selected_word.word) - 1
                if word_start_row <= new_row <= word_end_row:
                    self.selected_cell = (new_row, new_col)
                    return
                
        while 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
            if self.generator.grid[new_row][new_col] != '#':
                self.selected_cell = (new_row, new_col)
                return
            new_row += row_delta
            new_col += col_delta

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == 'playing' or self.state == 'complete':
                            self.state = 'menu'
                            self.create_menu_ui()
                    elif event.key == pygame.K_SPACE and self.state == 'complete':
                        self.start_game()
                    elif self.state == 'playing':
                        self.handle_key_inputs(event)

                elif self.state == 'menu':
                    for checkbox in self.category_checkboxes:
                        checkbox.handle_event(event)
                    self.start_button.handle_event(event)
                    self.theme_button.handle_event(event)

                elif self.state == 'playing':
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_cell_click(event.pos)

            self.screen.fill(self.colours['background'])

            if self.state == 'menu':
                self.draw_menu()

            elif self.state == 'playing':
                self.draw_grid
                self.draw_clues
                self.draw_controls

                if self.check_completion():
                    self.state = 'complete'

            elif self.state == 'complete':
                self.draw_grid()
                self.draw_clues()
                self.draw_complete_screen()

            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CrosswordGame()
    game.run()