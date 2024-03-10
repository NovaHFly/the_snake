from random import choice, randint

import pygame

# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

CELL_SIZE = (GRID_SIZE, GRID_SIZE)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Функция обработки действий пользователя
def handle_keys(game_object):
    """Reads all events from game.

    Handles window close event and key press events.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


# Тут опишите все классы игры.
class GameObject:
    """Base game object."""

    body_color: tuple[int, int, int]

    def __init__(self):
        self.position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]

    def draw(self, surface: pygame.Surface):
        """Draw game object on the game screen."""
        pass


class Apple(GameObject):
    """An apple. Used as food for the snake."""

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self):
        """Set apple position to a random cell inside the grid."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

    def draw(self, surface):
        """Draws an apple on game screen."""
        rect = pygame.Rect(self.position, CELL_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """The snake.

    The snake is here to eat apples.
    The snake can move in 4 direction as well as grow when eating.
    """

    def __init__(self):
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.direction = RIGHT
        self.next_direction = None
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]

    @property
    def head_position(self):
        """Snake's head position (First square in snake positions)."""
        return self.positions[0]

    def move(self, grow: bool = False):
        """Moves the snake's head in current direction.

        Inserts new head position in positions list.
        If snake does not grow on this move, deletes last position.
        """
        col, row = self.head_position
        add_col, add_row = map(lambda x: x * GRID_SIZE, self.direction)

        new_position = (
            (col + add_col) % SCREEN_WIDTH,
            (row + add_row) % SCREEN_HEIGHT,
        )

        # Insert new position as snake's head
        self.positions.insert(0, new_position)

        # If snake's not growing, delete last position
        if not grow:
            self.positions.pop()

    def update_direction(self):
        """Updates snake direction with a new value on direction key press."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    # # Метод draw класса Snake
    def draw(self, surface):
        """Draw snake on the game screen."""
        for position in self.positions:
            rect = pygame.Rect(position, CELL_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

def main():
    """Game main loop."""
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple()

    while True:
        # Read and handle events
        handle_keys(snake)
        snake.update_direction()

        # Clear screen
        screen.fill(BOARD_BACKGROUND_COLOR)

        snake_ate_apple = snake.head_position == apple.position
        if snake_ate_apple:
            apple.randomize_position()
        snake.move(grow=snake_ate_apple)

        # Draw all game objects
        apple.draw(screen)
        snake.draw(screen)

        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
