try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

import pygame
import random
import json
import sys
from typing import List, Dict, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
CELL_SIZE = 35
GRID_SIZE = 15
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 150
POINTS_PER_WORD = 100
POINTS_PER_LETTER = 10

# Colors - Light Mode
LIGHT_COLORS = {
    'background': (250, 250, 250),
    'grid_bg': (255, 255, 255),
    'grid_lines': (200, 200, 200),
    'text': (30, 30, 30),
    'cell_filled': (240, 240, 240),
    'cell_blocked': (50, 50, 50),
    'cell_selected': (100, 150, 255),
    'cell_correct': (144, 238, 144),
    'cell_incorrect': (255, 160, 160),
    'cell_hint': (255, 223, 128),
    'number_text': (100, 100, 100),
    'button': (70, 130, 180),
    'button_hover': (100, 160, 210),
    'button_disabled': (150, 150, 150),
    'button_text': (255, 255, 255),
    'score_text': (0, 100, 0),
}

# Colors - Dark Mode
DARK_COLORS = {
    'background': (30, 30, 35),
    'grid_bg': (45, 45, 50),
    'grid_lines': (70, 70, 75),
    'text': (230, 230, 230),
    'cell_filled': (55, 55, 60),
    'cell_blocked': (20, 20, 25),
    'cell_selected': (80, 120, 200),
    'cell_correct': (60, 140, 60),
    'cell_incorrect': (180, 60, 60),
    'cell_hint': (180, 140, 50),
    'number_text': (150, 150, 150),
    'button': (60, 100, 150),
    'button_hover': (80, 120, 170),
    'button_disabled': (80, 80, 90),
    'button_text': (240, 240, 240),
    'score_text': (100, 200, 100),
}


class CrosswordWord:
    def __init__(self, word: str, clue: str, row: int, col: int, direction: str, number: int):
        self.word = word.upper()
        self.clue = clue
        self.row = row
        self.col = col
        self.direction = direction  # 'across' or 'down'
        self.number = number


class CrosswordGenerator:
    def __init__(self, words_data: List[Dict], grid_size: int = 15):
        self.words_data = words_data
        self.grid_size = grid_size
        self.grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        self.placed_words: List[CrosswordWord] = []
        self.word_number = 1
        
    def can_place_word(self, word: str, row: int, col: int, direction: str) -> bool:
        if direction == 'across':
            if col + len(word) > self.grid_size:
                return False
            # Check if there's a blocked cell before or after
            if col > 0 and self.grid[row][col - 1] != ' ' and self.grid[row][col - 1] != '#':
                return False
            if col + len(word) < self.grid_size and self.grid[row][col + len(word)] != ' ' and self.grid[row][col + len(word)] != '#':
                return False
            
            for i, letter in enumerate(word):
                current_col = col + i
                cell = self.grid[row][current_col]
                
                if cell != ' ' and cell != letter and cell != '#':
                    return False
                
                # Check perpendicular conflicts
                if cell == ' ' or cell == '#':
                    if row > 0 and self.grid[row - 1][current_col] not in [' ', '#']:
                        return False
                    if row < self.grid_size - 1 and self.grid[row + 1][current_col] not in [' ', '#']:
                        return False
        
        else:  # down
            if row + len(word) > self.grid_size:
                return False
            # Check if there's a blocked cell before or after
            if row > 0 and self.grid[row - 1][col] != ' ' and self.grid[row - 1][col] != '#':
                return False
            if row + len(word) < self.grid_size and self.grid[row + len(word)][col] != ' ' and self.grid[row + len(word)][col] != '#':
                return False
            
            for i, letter in enumerate(word):
                current_row = row + i
                cell = self.grid[current_row][col]
                
                if cell != ' ' and cell != letter and cell != '#':
                    return False
                
                # Check perpendicular conflicts
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
        
        for placed_word in self.placed_words:
            for i, letter1 in enumerate(word):
                for j, letter2 in enumerate(placed_word.word):
                    if letter1 == letter2:
                        if placed_word.direction == 'across':
                            # Try placing down
                            new_row = placed_word.row - i
                            new_col = placed_word.col + j
                            if 0 <= new_row < self.grid_size and 0 <= new_row + len(word) <= self.grid_size:
                                positions.append((new_row, new_col, 'down'))
                        else:
                            # Try placing across
                            new_row = placed_word.row + j
                            new_col = placed_word.col - i
                            if 0 <= new_col < self.grid_size and 0 <= new_col + len(word) <= self.grid_size:
                                positions.append((new_row, new_col, 'across'))
        
        return positions
    
    def generate(self, num_words: int = 15) -> bool:
        if not self.words_data or num_words == 0:
            return False
        
        # Select random words
        available_count = min(num_words, len(self.words_data))
        selected = random.sample(self.words_data, available_count)
        # Sort by length (longer words first for better placement)
        selected.sort(key=lambda x: len(x['word']), reverse=True)
        
        # Place first word in the center
        first_word_data = selected[0]
        first_word = first_word_data['word'].upper()
        start_row = self.grid_size // 2
        start_col = (self.grid_size - len(first_word)) // 2
        
        self.place_word(first_word, first_word_data['clue'], start_row, start_col, 'across')
        
        # Try to place remaining words - ONLY THROUGH INTERSECTIONS
        placed_count = 1
        attempts_per_word = 200
        
        for word_data in selected[1:]:
            word = word_data['word'].upper()
            clue = word_data['clue']
            placed = False
            
            # ONLY try intersections - no random placement
            positions = self.find_intersections(word)
            random.shuffle(positions)
            
            for row, col, direction in positions[:attempts_per_word]:
                if self.can_place_word(word, row, col, direction):
                    self.place_word(word, clue, row, col, direction)
                    placed = True
                    placed_count += 1
                    break
            
            # If we can't place it, skip this word (don't place randomly)
            if not placed:
                print(f"Skipped word '{word}' - no valid intersections")
        
        # Fill empty cells with blocked cells
        self.fill_blocked_cells()
        
        return placed_count >= 6  # Minimum 6 words for a valid puzzle
    
    def fill_blocked_cells(self):
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
        self.enabled = True
    
    def draw(self, screen, colors):
        if not self.enabled:
            color = colors['button_disabled']
        else:
            color = colors['button_hover'] if self.hovered else colors['button']
        
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, colors['text'], self.rect, 2, border_radius=5)
        
        font = pygame.font.Font(None, 28)
        text_surface = font.render(self.text, True, colors['button_text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.action()
                return True
        return False


class Checkbox:
    def __init__(self, x: int, y: int, text: str, checked: bool = False):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.text = text
        self.checked = checked
        self.hovered = False
    
    def draw(self, screen, colors):
        # Draw box
        pygame.draw.rect(screen, colors['grid_bg'], self.rect)
        pygame.draw.rect(screen, colors['text'], self.rect, 2)
        
        # Draw checkmark if checked
        if self.checked:
            pygame.draw.line(screen, colors['text'], 
                           (self.rect.x + 4, self.rect.y + 10),
                           (self.rect.x + 8, self.rect.y + 16), 3)
            pygame.draw.line(screen, colors['text'],
                           (self.rect.x + 8, self.rect.y + 16),
                           (self.rect.x + 16, self.rect.y + 4), 3)
        
        # Draw text
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, colors['text'])
        screen.blit(text_surface, (self.rect.x + 30, self.rect.y))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and event.button == 1:
                self.checked = not self.checked
                return True
        return False


class CrosswordGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Crossword Puzzle")
        self.clock = pygame.time.Clock()
        
        # Theme
        self.dark_mode = False
        self.colors = LIGHT_COLORS.copy()
        
        # Load words
        self.all_words = self.load_words()
        self.categories = sorted(list(set(word['category'] for word in self.all_words)))
        
        # Score system
        self.current_score = 0
        self.high_score = self.load_high_score()
        self.streak = 0
        
        # Game state
        self.state = 'menu'  # 'menu', 'playing', 'complete'
        self.generator = None
        self.user_grid = None
        self.selected_cell = None
        self.selected_word = None
        self.hints_remaining = 3
        self.hint_cells = []  # Track which cells were filled by hints
        
        # UI Elements
        self.create_menu_ui()
        self.hint_button = None
    
    def load_words(self) -> List[Dict]:
        try:
            with open('crossword_words.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("ERROR: crossword_words.json not found!")
            # Return default words if file doesn't exist
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
    
    def load_high_score(self) -> int:
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read())
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            print("Could not save high score")
    
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
        self.colors = DARK_COLORS.copy() if self.dark_mode else LIGHT_COLORS.copy()
    
    def use_hint(self):
        if self.hints_remaining <= 0:
            return
        
        # Find all empty cells that need to be filled
        empty_cells = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.generator.grid[row][col] != '#':
                    if self.user_grid[row][col] == '':
                        empty_cells.append((row, col))
        
        if empty_cells:
            # Pick a random empty cell
            row, col = random.choice(empty_cells)
            self.user_grid[row][col] = self.generator.grid[row][col]
            self.hint_cells.append((row, col))
            self.hints_remaining -= 1
            
            # Update hint button
            if self.hint_button:
                self.hint_button.text = f"Hint ({self.hints_remaining})"
                if self.hints_remaining == 0:
                    self.hint_button.enabled = False
    
    def start_game(self):
        print("Starting game...")
        
        # Get selected categories
        selected_categories = [cb.text for cb in self.category_checkboxes if cb.checked]
        
        # Filter words by categories
        if selected_categories:
            available_words = [w for w in self.all_words if w['category'] in selected_categories]
        else:
            available_words = self.all_words
        
        if not available_words:
            print("No words available for selected categories")
            return
        
        print(f"Available words: {len(available_words)}")
        
        # Generate puzzle - try multiple times if needed
        max_attempts = 10
        for attempt in range(max_attempts):
            self.generator = CrosswordGenerator(available_words, GRID_SIZE)
            success = self.generator.generate(num_words=12)
            
            if success:
                print(f"Puzzle generated successfully on attempt {attempt + 1}")
                print(f"Placed {len(self.generator.placed_words)} words")
                
                # Initialize user grid
                self.user_grid = [['' if self.generator.grid[r][c] != '#' else '#' 
                                  for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
                self.selected_cell = None
                self.selected_word = None
                self.hints_remaining = 3
                self.hint_cells = []
                
                # Create hint button
                self.hint_button = Button(GRID_OFFSET_X + GRID_SIZE * CELL_SIZE + 50, 50, 150, 40, f"Hint ({self.hints_remaining})", self.use_hint)
                
                self.state = 'playing'
                return
            else:
                print(f"Failed attempt {attempt + 1}")
        
        print("Could not generate valid puzzle after multiple attempts")
    
    def calculate_score(self):
        base_score = len(self.generator.placed_words) * POINTS_PER_WORD
        
        # Count letters (excluding hints)
        letter_count = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.generator.grid[row][col] != '#':
                    if (row, col) not in self.hint_cells:
                        letter_count += 1
        
        letter_bonus = letter_count * POINTS_PER_LETTER
        streak_bonus = self.streak * 50
        
        return base_score + letter_bonus + streak_bonus
    
    def next_puzzle(self):
        self.streak += 1
        self.start_game()
    
    def draw_score_bar(self):
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 28)
        
        # Current Score
        score_text = font_large.render(f"Score: {self.current_score}", True, self.colors['score_text'])
        self.screen.blit(score_text, (50, 20))
        
        # High Score
        high_score_text = font_medium.render(f"High Score: {self.high_score}", True, self.colors['text'])
        self.screen.blit(high_score_text, (50, 60))
        
        # Streak
        streak_text = font_large.render(f"Streak: {self.streak}", True, self.colors['button'])
        self.screen.blit(streak_text, (300, 20))
        
        # Hints remaining
        if self.state == 'playing':
            hints_text = font_medium.render(f"Hints: {self.hints_remaining}", True, self.colors['text'])
            self.screen.blit(hints_text, (300, 60))
    
    def draw_menu(self):
        self.screen.fill(self.colors['background'])
        
        # Title
        font_title = pygame.font.Font(None, 64)
        title = font_title.render("Crossword Puzzle", True, self.colors['text'])
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))
        
        # High Score Display
        font_score = pygame.font.Font(None, 36)
        hs_text = font_score.render(f"High Score: {self.high_score}", True, self.colors['score_text'])
        self.screen.blit(hs_text, (WINDOW_WIDTH // 2 - hs_text.get_width() // 2, 120))
        
        # Instructions
        font_small = pygame.font.Font(None, 28)
        instructions = font_small.render("Select categories (or none for all):", True, self.colors['text'])
        self.screen.blit(instructions, (100, 150))
        
        # Draw checkboxes
        for checkbox in self.category_checkboxes:
            checkbox.draw(self.screen, self.colors)
        
        # Draw buttons
        self.start_button.draw(self.screen, self.colors)
        self.theme_button.draw(self.screen, self.colors)
    
    def draw_grid(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE
                cell = self.generator.grid[row][col]
                
                if cell == '#':
                    # Blocked cell
                    pygame.draw.rect(self.screen, self.colors['cell_blocked'],
                                   (x, y, CELL_SIZE, CELL_SIZE))
                else:
                    # Empty cell
                    color = self.colors['grid_bg']
                    
                    # Highlight hint cells
                    if (row, col) in self.hint_cells:
                        color = self.colors['cell_hint']
                    # Highlight selected cell
                    elif self.selected_cell and self.selected_cell == (row, col):
                        color = self.colors['cell_selected']
                    # Highlight cells in selected word
                    elif self.selected_word:
                        word = self.selected_word
                        if word.direction == 'across':
                            if row == word.row and word.col <= col < word.col + len(word.word):
                                color = self.colors['cell_filled']
                        else:
                            if col == word.col and word.row <= row < word.row + len(word.word):
                                color = self.colors['cell_filled']
                    
                    pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, self.colors['grid_lines'],
                                   (x, y, CELL_SIZE, CELL_SIZE), 1)
                    
                    # Draw user's letter
                    user_letter = self.user_grid[row][col]
                    if user_letter and user_letter != '#':
                        font = pygame.font.Font(None, 32)
                        # Check if correct
                        if user_letter == cell:
                            text_color = self.colors['text']
                        else:
                            text_color = self.colors['cell_incorrect']
                        text = font.render(user_letter, True, text_color)
                        text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                        self.screen.blit(text, text_rect)
                    
                    # Draw word numbers
                    for word in self.generator.placed_words:
                        if word.row == row and word.col == col:
                            font_small = pygame.font.Font(None, 18)
                            number = font_small.render(str(word.number), True, self.colors['number_text'])
                            self.screen.blit(number, (x + 2, y + 2))
    
    def draw_clues(self):
        clue_x = GRID_OFFSET_X + GRID_SIZE * CELL_SIZE + 50
        clue_y = GRID_OFFSET_Y + 50
        max_width = WINDOW_WIDTH - clue_x - 20
        
        font_title = pygame.font.Font(None, 32)
        font_clue = pygame.font.Font(None, 20)
        
        # Separate across and down clues
        across_words = [w for w in self.generator.placed_words if w.direction == 'across']
        down_words = [w for w in self.generator.placed_words if w.direction == 'down']
        
        across_words.sort(key=lambda w: w.number)
        down_words.sort(key=lambda w: w.number)
        
        # Draw Across clues
        title = font_title.render("Across", True, self.colors['text'])
        self.screen.blit(title, (clue_x, clue_y))
        y = clue_y + 40
        
        for word in across_words:
            if y > WINDOW_HEIGHT - 40:
                break
            clue_color = self.colors['button'] if self.selected_word == word else self.colors['text']
            clue_text = f"{word.number}. {word.clue}"
            
            # Wrap text if too long
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
                text = font_clue.render(line, True, clue_color)
                self.screen.blit(text, (clue_x, y))
                y += 22
            y += 5
        
        # Draw Down clues
        y += 20
        if y < WINDOW_HEIGHT - 40:
            title = font_title.render("Down", True, self.colors['text'])
            self.screen.blit(title, (clue_x, y))
            y += 40
            
            for word in down_words:
                if y > WINDOW_HEIGHT - 40:
                    break
                clue_color = self.colors['button'] if self.selected_word == word else self.colors['text']
                clue_text = f"{word.number}. {word.clue}"
                
                # Wrap text
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
                    text = font_clue.render(line, True, clue_color)
                    self.screen.blit(text, (clue_x, y))
                    y += 22
                y += 5
    
    def draw_controls(self):
        font = pygame.font.Font(None, 20)
        controls = [
            "Click cell to select",
            "Type letters to fill",
            "Backspace to delete",
            "Arrow keys to move",
            "ESC for menu"
        ]
        
        y = GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE + 20
        for control in controls:
            text = font.render(control, True, self.colors['text'])
            self.screen.blit(text, (GRID_OFFSET_X, y))
            y += 22
    
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
        overlay.fill(self.colors['background'])
        self.screen.blit(overlay, (0, 0))
        
        font_title = pygame.font.Font(None, 72)
        font_sub = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 28)
        
        # Calculate and award score
        puzzle_score = self.calculate_score()
        self.current_score += puzzle_score
        
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self.save_high_score()
        
        title = font_title.render("Puzzle Complete!", True, self.colors['text'])
        score_text = font_sub.render(f"Points Earned: {puzzle_score}", True, self.colors['score_text'])
        total_text = font_sub.render(f"Total Score: {self.current_score}", True, self.colors['score_text'])
        subtitle = font_small.render("Press SPACE for next puzzle or ESC for menu", True, self.colors['text'])
        
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(total_text, (WINDOW_WIDTH // 2 - total_text.get_width() // 2, WINDOW_HEIGHT // 2 + 30))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, WINDOW_HEIGHT // 2 + 80))
    
    def handle_cell_click(self, pos):
        x, y = pos
        col = (x - GRID_OFFSET_X) // CELL_SIZE
        row = (y - GRID_OFFSET_Y) // CELL_SIZE
        
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            if self.generator.grid[row][col] != '#':
                self.selected_cell = (row, col)
                
                # Find which word this cell belongs to
                for word in self.generator.placed_words:
                    if word.direction == 'across':
                        if row == word.row and word.col <= col < word.col + len(word.word):
                            self.selected_word = word
                            return
                    else:
                        if col == word.col and word.row <= row < word.row + len(word.word):
                            self.selected_word = word
                            return
    
    def handle_key_input(self, event):
        if not self.selected_cell:
            return
        
        row, col = self.selected_cell
        
        # Don't allow editing hint cells
        if (row, col) in self.hint_cells:
            if event.unicode.isalpha():
                # Move to next cell if trying to type on hint
                if self.selected_word:
                    if self.selected_word.direction == 'across':
                        self.move_selection(0, 1)
                    else:
                        self.move_selection(1, 0)
            elif event.key == pygame.K_BACKSPACE:
                # Move backward when backspacing on hint
                if self.selected_word:
                    if self.selected_word.direction == 'across':
                        self.move_selection(0, -1)
                    else:
                        self.move_selection(-1, 0)
            return
        
        if event.key == pygame.K_BACKSPACE:
            # Delete current cell
            self.user_grid[row][col] = ''
            # Move backward in the word direction
            if self.selected_word:
                if self.selected_word.direction == 'across':
                    self.move_selection(0, -1)
                else:
                    self.move_selection(-1, 0)
        elif event.key == pygame.K_DELETE:
            self.user_grid[row][col] = ''
        elif event.unicode.isalpha():
            self.user_grid[row][col] = event.unicode.upper()
            # Auto-advance to next EMPTY cell (skip already filled cells and hints)
            if self.selected_word:
                if self.selected_word.direction == 'across':
                    self.move_to_next_empty_cell(0, 1)
                else:
                    self.move_to_next_empty_cell(1, 0)
        elif event.key == pygame.K_LEFT:
            self.move_selection(0, -1)
        elif event.key == pygame.K_RIGHT:
            self.move_selection(0, 1)
        elif event.key == pygame.K_UP:
            self.move_selection(-1, 0)
        elif event.key == pygame.K_DOWN:
            self.move_selection(1, 0)
    
    def move_selection(self, row_delta, col_delta):
        if not self.selected_cell or not self.selected_word:
            return
        
        row, col = self.selected_cell
        new_row = row + row_delta
        new_col = col + col_delta
        
        # Stay within the selected word boundaries
        word = self.selected_word
        if word.direction == 'across':
            word_start_col = word.col
            word_end_col = word.col + len(word.word) - 1
            
            # Move through cells in the word
            while word_start_col <= new_col <= word_end_col:
                if self.generator.grid[new_row][new_col] != '#':
                    # Check if this cell is empty (not filled and not a hint)
                    if (new_row, new_col) not in self.hint_cells and self.user_grid[new_row][new_col] == '':
                        self.selected_cell = (new_row, new_col)
                        return
                new_col += col_delta
        else:  # down
            word_start_row = word.row
            word_end_row = word.row + len(word.word) - 1
            
            # Move through cells in the word
            while word_start_row <= new_row <= word_end_row:
                if self.generator.grid[new_row][new_col] != '#':
                    # Check if this cell is empty (not filled and not a hint)
                    if (new_row, new_col) not in self.hint_cells and self.user_grid[new_row][new_col] == '':
                        self.selected_cell = (new_row, new_col)
                        return
                new_row += row_delta
    
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
                            self.current_score = 0
                            self.streak = 0
                            self.create_menu_ui()
                    elif event.key == pygame.K_SPACE and self.state == 'complete':
                        self.next_puzzle()
                    elif self.state == 'playing':
                        self.handle_key_input(event)
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.state == 'menu':
                        for checkbox in self.category_checkboxes:
                            checkbox.handle_event(event)
                        self.start_button.handle_event(event)
                        self.theme_button.handle_event(event)
                    elif self.state == 'playing' and self.hint_button:
                        self.hint_button.handle_event(event)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == 'menu':
                        for checkbox in self.category_checkboxes:
                            checkbox.handle_event(event)
                        self.start_button.handle_event(event)
                        self.theme_button.handle_event(event)
                    elif self.state == 'playing':
                        if self.hint_button:
                            self.hint_button.handle_event(event)
                        self.handle_cell_click(event.pos)
            
            # Drawing
            self.screen.fill(self.colors['background'])
            
            if self.state == 'menu':
                self.draw_menu()
            
            elif self.state == 'playing':
                self.draw_score_bar()
                if self.hint_button:
                    self.hint_button.draw(self.screen, self.colors)
                self.draw_grid()
                self.draw_clues()
                self.draw_controls()
                
                # Check if complete
                if self.check_completion():
                    self.state = 'complete'
            
            elif self.state == 'complete':
                self.draw_score_bar()
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