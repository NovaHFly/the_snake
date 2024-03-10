from random import choice, randint

import pygame

pygame.init()

# Screen aspect ratio
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480

# Grid constants
GRID_SIZE = 20
CELL_SIZE = (GRID_SIZE, GRID_SIZE)
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
GRID_CENTER = (GRID_WIDTH // 2, GRID_HEIGHT // 2)

# Move directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Cell border color
BORDER_COLOR = (93, 216, 228)

APPLE_COLOR = (255, 0, 0)

SNAKE_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (255, 255, 0)

# Game speed (in fps)
SPEED = 10

# Game screen setting
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Game window caption
pygame.display.set_caption('Змейка')

# Game clock
clock = pygame.time.Clock()


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


class GameObject:
    """Base game object."""

    def __init__(self):
        self.position = GRID_CENTER
        self.body_color = None

    def draw(self, surface: pygame.Surface):
        """Draw game object on the game screen."""
        pass

    @property
    def screen_position(self) -> tuple[int, int]:
        """Object's true position on screen."""
        col, row = self.position
        return (col * GRID_SIZE, row * GRID_SIZE)


class Apple(GameObject):
    """An apple. Used as food for the snake."""

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(
        self, snake_positions: list[tuple[int, int]] = None
    ):
        """Set apple position to a random cell inside the grid."""
        if snake_positions is None:
            snake_positions = [GRID_CENTER]

        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1),
                randint(0, GRID_HEIGHT - 1),
            )
            if self.position in snake_positions:
                continue
            break

    def draw(self, surface):
        """Draws an apple on game screen."""
        rect = pygame.Rect(self.screen_position, CELL_SIZE)
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
        self.head_color = SNAKE_HEAD_COLOR

        self.direction = RIGHT
        self.next_direction = None

        self.length = 1
        self.positions = [GRID_CENTER]

    def get_head_position(self) -> tuple[int, int]:
        """Snake's head position (First square in snake positions)."""
        return self.positions[0]

    def move(self):
        """Moves the snake's head in current direction.

        Inserts new head position in positions list.
        If snake does not grow on this move, deletes last position.
        """
        col, row = self.get_head_position()
        add_col, add_row = self.direction

        # Mod division is used to fix values which go
        #  over limit of the grid
        new_position = (
            (col + add_col) % GRID_WIDTH,
            (row + add_row) % GRID_HEIGHT,
        )

        # Insert new position as snake's head
        self.positions.insert(0, new_position)

        # If snake's not growing, remove last position
        if len(self.positions) > self.length:
            self.positions.pop()

    def update_direction(self):
        """Updates snake direction with a new value on direction key press."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    @property
    def screen_positions(self) -> list[tuple[int, int]]:
        """Snake segments true position on screen."""
        return list(
            map(
                lambda pos: (pos[0] * GRID_SIZE, pos[1] * GRID_SIZE),
                self.positions,
            )
        )

    def reset(self):
        """Resets snake on collision with self."""
        self.positions = [GRID_CENTER]
        self.length = 1
        self.direction = choice((UP, DOWN, LEFT, RIGHT))

    def draw(self, surface):
        """Draw snake on the game screen."""
        positions = self.screen_positions

        rect = pygame.Rect(positions[0], CELL_SIZE)
        pygame.draw.rect(surface, self.head_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        for position in positions[1:]:
            rect = pygame.Rect(position, CELL_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def main():
    """Game main loop."""
    snake = Snake()
    apple = Apple()

    while True:
        # Read and handle events
        handle_keys(snake)
        snake.update_direction()

        # Clear screen
        screen.fill(BOARD_BACKGROUND_COLOR)

        # If snake eats an apple, allow it to grow by one
        snake_ate_apple = snake.get_head_position() == apple.position
        if snake_ate_apple:
            snake.length += 1
            apple.randomize_position(snake.positions)

        # If snake collides with its body, reset its length to 1
        snake_collide_self = snake.get_head_position() in snake.positions[1:]
        if snake_collide_self:
            snake.reset()

        snake.move()

        # Draw all game objects
        apple.draw(screen)
        snake.draw(screen)

        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
