import abc
from functools import wraps
from random import choice, randint
from typing import TypeVar, Optional

import pygame

T = TypeVar('T')
GridCoordinates = tuple[int, int]

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

DIRECTIONAL_KEYS = (
    pygame.K_UP,
    pygame.K_DOWN,
    pygame.K_LEFT,
    pygame.K_RIGHT,
)

BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Cell border color
BORDER_COLOR = (93, 216, 228)

APPLE_COLOR = (255, 0, 0)
BAD_APPLE_COLOR = (120, 0, 120)
STONE_COLOR = (160, 160, 160)

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


def singleton(cls: T) -> T:
    """Singleton pattern decorator."""
    instance = None

    @wraps(cls)
    def inner(*args, **kwargs) -> None:
        nonlocal instance

        if instance is None:
            instance = cls(*args, **kwargs)

        return instance

    return inner


def draw_cell(
    surface: pygame.Surface,
    position: tuple[int, int],
    color: tuple[int, int, int] = BOARD_BACKGROUND_COLOR,
) -> None:
    """Fills one rectangle cell on the grid."""
    rect = pygame.Rect(position, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def generate_random_coordinates(
    occupied_coordinates: Optional[list[GridCoordinates]] = None,
) -> GridCoordinates:
    """Generate random unoccupied coordinates in the grid."""
    if occupied_coordinates is None:
        occupied_coordinates = []

    while True:
        coordinates = (
            randint(0, GRID_WIDTH - 1),
            randint(0, GRID_HEIGHT - 1),
        )

        # If generated coordinates do not collide
        #  with any of occupied coordinates, exit loop
        if coordinates not in occupied_coordinates:
            break

    return coordinates


# FIXME: A big singleton problem, needs refactoring!
@singleton
class GameController:
    """Contains links to global objects, such as snake and apple.
    Also provides convenient methods to manipulate game flow.
    """

    def __init__(self) -> None:
        self.snake = Snake()
        self.apple = Apple()
        self.bad_apple = BadApple()
        self.stone = Stone()

    def handle_events(self) -> None:
        """Reads and handles all events from pygame."""
        for event in pygame.event.get():
            # Handle quit event, e.g. window closing.
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN and event.key in DIRECTIONAL_KEYS:
                self.snake.handle_key_press(event.key)

    # Probably better as a separate function, but needs some way to get positions on the grid
    @property
    def occupied_coordinates(self) -> list[GridCoordinates]:
        """Get a list of all occupied positions inside the grid."""
        return self.snake.positions + [
            self.apple.position,
            self.bad_apple.position,
            self.stone.position,
        ]

    def reset(self) -> None:
        """Resets the game."""
        self.snake.reset()
        self.apple.randomize_position(self.occupied_coordinates)
        self.bad_apple.randomize_position(self.occupied_coordinates)
        self.stone.randomize_position(self.occupied_coordinates)

    def check_snake_collision(self) -> None:
        """Checks if snake collides with anything and if it does,
        handles this event.
        """
        snake = self.snake

        # FIXME: A lot of duplicate code, probably there's a way to refactor.
        # If snake eats apple, increase its length by 1
        if snake.get_head_position() == self.apple.position:
            snake.eat(self.apple, self.occupied_coordinates)
            return

        # If snake eats bad apple, decrease its length by 1.
        if snake.get_head_position() == self.bad_apple.position:
            snake.eat(self.bad_apple, self.occupied_coordinates)
            return

        # If snake eats a stone, it dies from indigestion. Game is reset.
        if snake.get_head_position() == self.stone.position:
            snake.eat(self.stone, self.occupied_coordinates)
            return

        # If snake eats its own body, it dies. Game is reset.
        if snake.get_head_position() in snake.positions[1:]:
            self.reset()
            return


class GameObject:
    """Base game object."""

    def __init__(self) -> None:
        self.position = GRID_CENTER
        self.body_color = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw game object on the game screen."""
        pass

    @property
    def screen_position(self) -> tuple[int, int]:
        """Object's true position on screen."""
        col, row = self.position
        return (col * GRID_SIZE, row * GRID_SIZE)


class EatableObject(GameObject, abc.ABC):
    """An object that the Snake can eat."""

    def __init__(self) -> None:
        super().__init__()

        self.position = None

        # Randomize object's starting position
        self.randomize_position()

    @abc.abstractmethod
    def apply_effect(self, snake: 'Snake') -> None:
        """Apply some effect to the snake."""
        pass

    def randomize_position(
        self, occupied_coordinates: Optional[list[GridCoordinates]] = None
    ) -> None:
        """Set object position to a random cell inside the grid."""
        # Object can not be spawned in occupied coordinates.
        if occupied_coordinates is None:
            occupied_coordinates = []  # Probably better to block some coordinates in this case

        # Get random available coordinates and set it to self position
        self.position = generate_random_coordinates(occupied_coordinates)

    def draw(self, surface: pygame.Surface) -> None:
        """Draws an object on game screen."""
        draw_cell(surface, self.screen_position, self.body_color)


class Apple(EatableObject):
    """An apple. Used as food for the snake."""

    def __init__(self) -> None:
        super().__init__()
        self.body_color = APPLE_COLOR

    def apply_effect(self, snake: 'Snake') -> None:
        """Increase snake's length by 1."""
        snake.length += 1


class BadApple(EatableObject):
    """Rotten apple, which isn't good for your health.
    Eating it will cause snake to lose its length.
    """

    def __init__(self) -> None:
        super().__init__()
        self.body_color = BAD_APPLE_COLOR

    def apply_effect(self, snake: 'Snake') -> None:
        """Decrease snake's length by 1."""
        snake.length -= 1


class Stone(EatableObject):
    """Some stone, lying in the field. Snake can't digest it."""

    def __init__(self) -> None:
        super().__init__()
        self.body_color = STONE_COLOR

    def apply_effect(self, snake: 'Snake') -> None:
        """Snake can't digest stones. Its length is set to 0."""
        snake.length = 0


class Snake(GameObject):
    """The Snake.

    The snake is here to eat apples.
    The snake can move in 4 direction as well as grow when eating.
    """

    def __init__(self) -> None:
        super().__init__()

        self.body_color = SNAKE_COLOR
        self.head_color = SNAKE_HEAD_COLOR

        self.direction = RIGHT
        self.next_direction = None

        self.length = 1
        # Snake starts at the grid center
        self.positions = [GRID_CENTER]

    def get_head_position(self) -> tuple[int, int]:
        """Snake's head position (First square in snake positions)."""
        return self.positions[0]

    def eat(
        self,
        eatable_object: EatableObject,
        occupied_coordinates: Optional[list[GridCoordinates]],
    ) -> None:
        """Eats something."""
        eatable_object.apply_effect(self)
        eatable_object.randomize_position(occupied_coordinates)

    def move(self) -> None:
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
        while len(self.positions) > self.length:
            self.positions.pop()

    def handle_key_press(self, key_id: int) -> None:
        """Chooses snake's next direction based on pressed
        directional key.
        """
        if key_id == pygame.K_UP and self.direction != DOWN:
            self.next_direction = UP
        elif key_id == pygame.K_DOWN and self.direction != UP:
            self.next_direction = DOWN
        elif key_id == pygame.K_LEFT and self.direction != RIGHT:
            self.next_direction = LEFT
        elif key_id == pygame.K_RIGHT and self.direction != LEFT:
            self.next_direction = RIGHT

        self.update_direction()

    def update_direction(self) -> None:
        """Updates snake direction with a new value."""
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

    def reset(self) -> None:
        """Resets snake on collision with self."""
        self.positions = [GRID_CENTER]
        self.length = 1
        self.direction = choice((UP, DOWN, LEFT, RIGHT))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw snake on the game screen."""
        positions = self.screen_positions

        draw_cell(surface, positions[0], self.head_color)

        for position in positions[1:]:
            draw_cell(surface, position, self.body_color)


def main() -> None:
    """Game main loop."""
    # Initialize game controller
    controller = GameController()

    # Get all game object instances from controller
    snake = controller.snake
    apple = controller.apple
    bad_apple = controller.bad_apple
    stone = controller.stone

    while True:
        # Read and handle events
        controller.handle_events()

        # Clear screen
        screen.fill(BOARD_BACKGROUND_COLOR)

        # Check if snake collides with anything.
        #  If it does, handle this event.
        controller.check_snake_collision()

        # If snake length reaches 0, then it dies.
        #  The game must be reset.
        if snake.length == 0:
            controller.reset()

        snake.move()

        # Draw all game objects
        apple.draw(screen)
        bad_apple.draw(screen)
        stone.draw(screen)

        snake.draw(screen)

        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
