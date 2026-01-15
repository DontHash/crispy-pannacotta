"""
Graphics module for Pendulum Simulation
Handles all OpenGL rendering and visualization
"""

import math
from typing import List, Tuple
from OpenGL.GL import *
from OpenGL.GLU import *
import config


class Color:
    """Helper class for color management"""

    @staticmethod
    def set_color(color: Tuple[float, float, float, float]) -> None:
        """Set OpenGL color"""
        glColor4f(*color)


class Renderer:
    """
    Handles all rendering operations for the pendulum simulation.
    Manages OpenGL state, drawing primitives, and visualization.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize the renderer with window dimensions.

        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        self.width = width
        self.height = height
        self.trace_points: List[Tuple[float, float]] = []
        self.frame_count = 0
        self.fps = 0.0
        self.last_time = 0.0

    def setup_projection(self) -> None:
        """Configure OpenGL projection matrix for 2D rendering"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(
            config.ORTHO_LEFT,
            config.ORTHO_RIGHT,
            config.ORTHO_BOTTOM,
            config.ORTHO_TOP,
            config.ORTHO_NEAR,
            config.ORTHO_FAR,
        )
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def setup_viewport(self) -> None:
        """Configure OpenGL viewport"""
        glViewport(0, 0, self.width, self.height)

    def clear_screen(self) -> None:
        """Clear the screen with background color"""
        Color.set_color(config.BACKGROUND_COLOR)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def draw_grid(self, grid_size: float) -> None:
        """
        Draw a reference grid for better spatial understanding.

        Args:
            grid_size: Size of each grid cell
        """
        if not config.SHOW_GRID:
            return

        Color.set_color(config.GRID_COLOR)
        glBegin(GL_LINES)

        # Vertical lines
        x = config.ORTHO_LEFT
        while x <= config.ORTHO_RIGHT:
            glVertex2f(x, config.ORTHO_BOTTOM)
            glVertex2f(x, config.ORTHO_TOP)
            x += grid_size

        # Horizontal lines
        y = config.ORTHO_BOTTOM
        while y <= config.ORTHO_TOP:
            glVertex2f(config.ORTHO_LEFT, y)
            glVertex2f(config.ORTHO_RIGHT, y)
            y += grid_size

        glEnd()

    def draw_pivot_point(self, pivot_x: float, pivot_y: float) -> None:
        """
        Draw the fixed pivot point as a circle.

        Args:
            pivot_x: X-coordinate of pivot
            pivot_y: Y-coordinate of pivot
        """
        Color.set_color(config.PIVOT_POINT_COLOR)
        self._draw_circle(pivot_x, pivot_y, config.PIVOT_RADIUS, segments=32)

    def draw_rod(
        self, pivot_x: float, pivot_y: float, bob_x: float, bob_y: float
    ) -> None:
        """
        Draw the pendulum rod as a line.

        Args:
            pivot_x: X-coordinate of pivot
            pivot_y: Y-coordinate of pivot
            bob_x: X-coordinate of bob
            bob_y: Y-coordinate of bob
        """
        Color.set_color(config.ROD_COLOR)
        glLineWidth(config.ROD_WIDTH)
        glBegin(GL_LINES)
        glVertex2f(pivot_x, pivot_y)
        glVertex2f(bob_x, bob_y)
        glEnd()
        glLineWidth(1.0)  # Reset line width

    def draw_bob(self, bob_x: float, bob_y: float) -> None:
        """
        Draw the pendulum bob as a circle.

        Args:
            bob_x: X-coordinate of bob
            bob_y: Y-coordinate of bob
        """
        Color.set_color(config.BOB_COLOR)
        self._draw_circle(bob_x, bob_y, config.BOB_RADIUS, segments=32)

    def draw_trace(self) -> None:
        """
        Draw the trajectory trace of the pendulum bob with vertical scrolling.
        Creates a strip chart effect where oscillations stack vertically over time.
        """
        if not config.SHOW_TRACE or len(self.trace_points) < 2:
            return

        Color.set_color(config.TRACE_COLOR)
        glLineWidth(1.5)
        glBegin(GL_LINE_STRIP)
        
        for idx, point in enumerate(self.trace_points):
            x = point[0]
            y = point[1]
            glVertex2f(x, y)
        
        glEnd()
        glLineWidth(1.0)

    def add_trace_point(self, x: float, y: float) -> None:
        """
        Add a point to the trace history.
        When enough time has passed for a complete oscillation, automatically scroll down.

        Args:
            x: X-coordinate
            y: Y-coordinate
        """
        self.trace_points.append((x, y))

        # Limit trace length to maintain performance
        if len(self.trace_points) > config.TRACE_LENGTH:
            self.trace_points.pop(0)
    
    def clear_trace(self) -> None:
        """Clear the trace history"""
        self.trace_points.clear()

    def _draw_circle(
        self, center_x: float, center_y: float, radius: float, segments: int = 32
    ) -> None:
        """
        Draw a filled circle using triangle fan.

        Args:
            center_x: X-coordinate of center
            center_y: Y-coordinate of center
            radius: Radius of circle
            segments: Number of segments for smooth circle (higher = smoother, slower)
        """
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(center_x, center_y)

        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            glVertex2f(x, y)

        glEnd()

    def draw_text_info(
        self,
        angle: float,
        angular_velocity: float,
        angular_acceleration: float,
        total_energy: float,
        kinetic_energy: float,
        potential_energy: float,
        fps: float,
    ) -> None:
        """
        Render text information about the simulation.
        Note: Text rendering requires external library (not implemented in basic OpenGL)
        This is a placeholder for integration with text rendering libraries.

        Args:
            angle: Current angle in radians
            angular_velocity: Angular velocity in rad/s
            angular_acceleration: Angular acceleration in rad/s²
            total_energy: Total energy
            kinetic_energy: Kinetic energy
            potential_energy: Potential energy
            fps: Frames per second
        """
        # This function is a placeholder for text rendering
        # You can integrate PyOpenGL text libraries here
        # For now, this data can be printed to console
        pass

    def update_fps(self, delta_time: float) -> None:
        """
        Update FPS counter.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        self.frame_count += 1
        if self.frame_count % 60 == 0:  # Update every 60 frames
            if delta_time > 0:
                self.fps = 1.0 / delta_time
