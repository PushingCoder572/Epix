import pygame
import sys

# Initialization method for Pygame
pygame.init()

# RGB constants
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


# Class holding the dimensions of the game and window
class GDimensions:
    def __init__(self, w, h, x, y, window_w, window_h):
        self.width = w
        self.height = h
        self.margin_x = x
        self.margin_y = y

        self.window_w = window_w
        self.window_h = window_h

        self.right_border = self.margin_x + self.width
        self.left_border = self.margin_x
        self.top_border = self.margin_y
        self.bottom_border = self.margin_y + self.height


def create_text(game_dimensions):
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render('Pausat, Tryck på \'Enter\' för att starta', False, BLACK)
    text_rect = text.get_rect()
    text_rect.center = (game_dimensions.window_w//2, game_dimensions.window_h//2)

    return text, text_rect


def generate_cell_size(window):
    width, height = window.get_size()

    cell_size = width//100

    return cell_size


# Function that calculates all the dimensions of the game window
def generate_game_size(window, cell_size):
    # Retrieves the specific width and height for the fullscreen window
    width, height = window.get_size()

    game_width = (width//cell_size) * cell_size
    game_height = (height//cell_size) * cell_size

    margin_x = int((width - game_width)/2)
    margin_y = int((height - game_height)/2)

    return GDimensions(game_width, game_height, margin_x, margin_y, width, height)


def generate_grid(grid_dimensions):
    lst = []

    size_x, size_y = grid_dimensions
    for i in range(size_y):
        lst.append([0] * size_x)

    return lst


# Function that returns the numbers of cells in the grid
def fetch_dimensions(game_dimensions, cell_size):
    return game_dimensions.width//cell_size, game_dimensions.height//cell_size


# The main game class
class GameOfLife:
    def __init__(self):
        self.is_running = False

        # Creating the window to display the game
        self.window = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        self.cell_size = generate_cell_size(self.window)
        self.game_dimensions = generate_game_size(self.window, self.cell_size)
        self.grid = generate_grid(fetch_dimensions(self.game_dimensions, self.cell_size))
        self.text = create_text(self.game_dimensions)

    # Method to draw one row
    def fill_row(self, y, index_y):
        x = self.game_dimensions.margin_x

        for index_x in range(len(self.grid[0])):
            if self.grid[index_y][index_x] == 0:
                # Drawing a cell using Pygame
                pygame.draw.rect(self.window, WHITE, ((x, y), (self.cell_size, self.cell_size)))
            else:
                # Drawing a cell using Pygame
                pygame.draw.rect(self.window, GREEN, ((x, y), (self.cell_size, self.cell_size)))

            # Drawing vertical borders using Pygame lines
            pygame.draw.line(self.window, BLACK,
                             (x, self.game_dimensions.margin_y),
                             (x, self.game_dimensions.window_h), 1)
            x += self.cell_size

        # Drawing horizontal borders using Pygame lines
        pygame.draw.line(self.window, BLACK, (0, y), (self.game_dimensions.window_w, y), 1)

    # Main draw method, fills in one row at a time
    def draw(self):
        y = self.game_dimensions.margin_y

        for i in range(len(self.grid)):
            self.fill_row(y, i)
            y += self.cell_size

    # Method to turn the pixel coordinates into grid-square coordinates
    def click_to_coordinate(self, p):
        x, y = p

        x -= self.game_dimensions.margin_x
        y -= self.game_dimensions.margin_y

        return int(x / self.cell_size), int(y / self.cell_size)

    # Method to check if the click was inside the grid
    def inbounds(self, p):
        x, y = p

        if self.game_dimensions.left_border < x < self.game_dimensions.right_border:
            if self.game_dimensions.top_border < y < self.game_dimensions.bottom_border:
                return True
            else:
                return False
        else:
            return False

    # Method to make clicked upon squares change
    def select(self, p, button):
        x, y = self.click_to_coordinate(p)

        # Using the Pygame button codes. 1 = Left click. 3 = Right click.
        if button == 1:
            self.grid[y][x] = 1
        elif button == 3:
            self.grid[y][x] = 0

    # Method to check living neighbors of a given cell
    def check_neighbors(self, p):
        neighbors = 0

        y, x = p
        w, h = fetch_dimensions(game.game_dimensions, game.cell_size)

        potentials = [(x - 1, y - 1),
                      (x - 1, y),
                      (x - 1, y + 1),
                      (x, y - 1),
                      (x, y + 1),
                      (x + 1, y - 1),
                      (x + 1, y),
                      (x + 1, y + 1)]

        for a, b in potentials:
            if 0 <= a < w and 0 <= b < h:
                if self.grid[b][a] == 1:
                    neighbors += 1

        return neighbors

    # Method to simulate one iteration of the Game of Life
    def run_sim(self):
        w, h = fetch_dimensions(self.game_dimensions, self.cell_size)

        to_create = []
        to_kill = []
        for i in range(h):
            for j in range(w):
                neighbors = self.check_neighbors((i, j))
                cell = self.grid[i][j]

                if cell == 0:
                    if neighbors == 3:
                        to_create.append((i, j))
                elif cell == 1:
                    if neighbors < 2 or neighbors > 3:
                        to_kill.append((i, j))

        self.update_grid(to_create, to_kill)

    # Method to update the grid according to the simulation
    def update_grid(self, create, kill):
        for i in create:
            y, x = i
            self.grid[y][x] = 1

        for i in kill:
            y, x = i
            self.grid[y][x] = 0


game = GameOfLife()

while 1:
    # Pygame event-system handling
    for event in pygame.event.get():
        # Checking for keyboard interaction
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_RETURN:
                game.is_running = not game.is_running
        # Checking for mouse interaction
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if game.inbounds(pos):
                game.select(pos, event.button)

    game.draw()

    if game.is_running:
        game.run_sim()
    else:
        txt, rect = game.text
        game.window.blit(txt, rect)

    # Refreshing the window
    pygame.display.flip()
