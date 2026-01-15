"""
Configuration module for Pendulum Simulation
Contains all adjustable parameters for physics and graphics
"""

# ==================== WINDOW SETTINGS ====================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Pendulum Simulation - Physics Visualization"

# ==================== PHYSICS PARAMETERS ====================
# Pendulum properties
INITIAL_ANGLE = 0.5  # Initial angle in radians (approximately 28.6 degrees)
PENDULUM_LENGTH = 3.0  # Length of pendulum in units
ROD_MASS = 0.1  # Mass of the rod (negligible)
BOB_MASS = 1.0  # Mass of the bob in kg
GRAVITY = 9.81  # Gravitational acceleration in m/s^2

# Damping (air resistance and friction)
DAMPING_COEFFICIENT = 0.0  # 0 = no damping, increase for more resistance

# Time step for physics simulation
TIME_STEP = 0.001  # Time step in seconds (1 millisecond)
SIMULATION_SPEED = 1.0  # Speed multiplier for animation (1.0 = real-time)

# ==================== GRAPHICS SETTINGS ====================
# Rendering parameters
BACKGROUND_COLOR = (0.1, 0.1, 0.15, 1.0)  # RGBA - Dark blue background
PIVOT_POINT_COLOR = (1.0, 0.2, 0.2, 1.0)  # Red
ROD_COLOR = (0.8, 0.8, 0.8, 1.0)  # Light gray
BOB_COLOR = (0.2, 0.8, 1.0, 1.0)  # Cyan
TRACE_COLOR = (0.4, 0.6, 1.0, 0.3)  # Semi-transparent blue

# Visual parameters
ROD_WIDTH = 3.0  # Line width for rod
PIVOT_RADIUS = 0.1  # Radius of pivot point circle
BOB_RADIUS = 0.2  # Radius of pendulum bob
TRACE_LENGTH = 500  # Maximum number of points in trace

# Grid and text rendering
SHOW_GRID = True
SHOW_INFO = True
SHOW_TRACE = True
GRID_SIZE = 0.5
GRID_COLOR = (0.3, 0.3, 0.3, 0.2)

# ==================== ANIMATION SETTINGS ====================
# FPS and timing
TARGET_FPS = 60  # Target frames per second
FRAME_TIME_LIMIT = 1.0 / TARGET_FPS  # Maximum time per frame

# ==================== CAMERA/VIEWPORT SETTINGS ====================
# Orthographic projection bounds
ORTHO_LEFT = -6.0
ORTHO_RIGHT = 6.0
ORTHO_BOTTOM = -4.0
ORTHO_TOP = 4.0
ORTHO_NEAR = -1.0
ORTHO_FAR = 1.0

# Pivot point position (center of screen)
PIVOT_X = 0.0
PIVOT_Y = 2.0

# ==================== DEBUG SETTINGS ====================
DEBUG_MODE = False  # Print debug information
LOG_PHYSICS_DATA = True  # Log physics values to file
PRINT_FPS = True  # Print FPS to console

# ==================== GRAPH SETTINGS ====================
SHOW_REALTIME_GRAPH = True  # Show real-time graph window
GRAPH_UPDATE_INTERVAL = 0.1  # Update graph every N seconds
GRAPH_HISTORY_LENGTH = 500  # Number of data points to show in graph
