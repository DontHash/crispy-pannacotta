"""
Pendulum Simulation Application
Main entry point for the interactive pendulum physics simulation
"""

import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import config
from physics import Pendulum
from graphics import Renderer, RealtimeGraph
from utils import Timer, FrameRateLimiter, DataRecorder, PhysicsValidator
from ui import ParameterInputUI, ControlPanel


class PendulumSimulation:
    """
    Main simulation class that manages the pendulum physics,
    rendering, and user interactions.
    """

    def __init__(self, parameters=None):
        """
        Initialize the pendulum simulation.
        
        Args:
            parameters: Dictionary with custom parameters, or None to use defaults
        """
        # Use provided parameters or defaults from config
        if parameters:
            length = parameters.get("length", config.PENDULUM_LENGTH)
            mass = parameters.get("mass", config.BOB_MASS)
            gravity = parameters.get("gravity", config.GRAVITY)
            initial_angle = parameters.get("initial_angle", config.INITIAL_ANGLE)
            damping = parameters.get("damping", config.DAMPING_COEFFICIENT)
            window_width = parameters.get("window_width", config.WINDOW_WIDTH)
            window_height = parameters.get("window_height", config.WINDOW_HEIGHT)
            show_trace = parameters.get("show_trace", config.SHOW_TRACE)
            show_grid = parameters.get("show_grid", config.SHOW_GRID)
            simulation_speed = parameters.get("simulation_speed", config.SIMULATION_SPEED)
            show_graph = parameters.get("show_graph", config.SHOW_REALTIME_GRAPH)
        else:
            length = config.PENDULUM_LENGTH
            mass = config.BOB_MASS
            gravity = config.GRAVITY
            initial_angle = config.INITIAL_ANGLE
            damping = config.DAMPING_COEFFICIENT
            window_width = config.WINDOW_WIDTH
            window_height = config.WINDOW_HEIGHT
            show_trace = config.SHOW_TRACE
            show_grid = config.SHOW_GRID
            simulation_speed = config.SIMULATION_SPEED
            show_graph = config.SHOW_REALTIME_GRAPH

        # Physics
        self.pendulum = Pendulum(
            length=length,
            mass=mass,
            gravity=gravity,
            initial_angle=initial_angle,
            damping=damping,
        )

        # Graphics
        self.renderer = Renderer(window_width, window_height)

        # Timing and performance
        self.timer = Timer()
        self.frame_limiter = FrameRateLimiter(config.TARGET_FPS)

        # Data recording
        self.recorder = DataRecorder()
        self.initial_energy = 0.0

        # Real-time graph
        self.graph = None
        if show_graph:
            try:
                self.graph = RealtimeGraph(update_interval=int(config.GRAPH_UPDATE_INTERVAL * 1000))
                print("✓ Real-time graph window opened")
            except Exception as e:
                print(f"⚠ Could not create graph window: {e}")
                self.graph = None

        # Control panel
        self.control_panel = None
        try:
            self.control_panel = ControlPanel(
                on_export=self.export_data,
                on_pause=self.toggle_pause,
                on_reset=self.reset_simulation,
                on_toggle_trace=self.toggle_trace
            )
            print("✓ Control panel window opened")
        except Exception as e:
            print(f"⚠ Could not create control panel: {e}")
            self.control_panel = None

        # Simulation state
        self.simulation_running = True
        self.simulation_paused = False
        self.show_trace = show_trace
        self.show_grid = show_grid
        self.accumulated_time = 0.0
        
        # Store parameters for reference
        self.params = {
            "length": length,
            "mass": mass,
            "gravity": gravity,
            "initial_angle": initial_angle,
            "damping": damping,
            "window_width": window_width,
            "window_height": window_height,
            "simulation_speed": simulation_speed,
        }

    def initialize_glut(self):
        """Initialize GLUT and OpenGL"""
        # Initialize GLUT
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(self.params["window_width"], self.params["window_height"])
        glutCreateWindow(config.WINDOW_TITLE.encode("utf-8"))

        # OpenGL settings
        glClearColor(*config.BACKGROUND_COLOR)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        # Setup projection
        self.renderer.setup_projection()
        self.renderer.setup_viewport()

        # Register callbacks
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.keyboard)
        glutTimerFunc(int(1000.0 / config.TARGET_FPS), self.timer_callback, 0)

        # Calculate initial energy
        total_energy, ke, pe = self.pendulum.get_energy()
        self.initial_energy = total_energy

        print("=" * 60)
        print("PENDULUM SIMULATION STARTED")
        print("=" * 60)
        print(f"Window Size: {self.params['window_width']}x{self.params['window_height']}")
        print(f"Target FPS: {config.TARGET_FPS}")
        print(f"Pendulum Length: {self.params['length']:.4f} units")
        print(f"Bob Mass: {self.params['mass']:.4f} kg")
        print(f"Gravity: {self.params['gravity']:.4f} m/s²")
        print(f"Initial Angle: {self.params['initial_angle']:.4f} radians ({self.params['initial_angle'] * 180 / 3.14159:.2f}°)")
        print(f"Damping Factor: {self.params['damping']:.4f}")
        if self.params['damping'] > 0:
            print("  ✓ Pendulum will DECAY over time (damping is active)")
        else:
            print("  ✗ Pendulum will NOT decay (damping = 0)")
        print(f"Simulation Speed: {self.params['simulation_speed']}x")
        print(f"Initial Energy: {self.initial_energy:.6f} J")
        print("\nKEYBOARD CONTROLS:")
        print("  SPACE: Pause/Resume simulation")
        print("  R: Reset simulation")
        print("  T: Toggle trace")
        print("  E: Export data to CSV")
        print("  ESC/Q: Quit simulation")
        print("=" * 60)

    def display(self):
        """OpenGL display callback"""
        if not self.simulation_running:
            return

        # Update control panel
        if self.control_panel and self.control_panel.is_alive():
            self.control_panel.update()
        elif self.control_panel and not self.control_panel.is_alive():
            # Control panel was closed, exit simulation
            print("Control panel closed, exiting...")
            sys.exit(0)

        # Update physics if not paused
        if not self.simulation_paused:
            self.update_physics()

        # Render scene
        self.render_scene()

        # Swap buffers
        glutSwapBuffers()

    def render_scene(self):
        """Render the complete simulation scene"""
        # Clear screen
        self.renderer.clear_screen()

        # Get pendulum positions
        bob_x, bob_y = self.pendulum.get_bob_position(config.PIVOT_X, config.PIVOT_Y)

        # Draw grid
        if self.show_grid:
            self.renderer.draw_grid(config.GRID_SIZE)

        # Draw pendulum components
        self.renderer.draw_rod(config.PIVOT_X, config.PIVOT_Y, bob_x, bob_y)
        self.renderer.draw_pivot_point(config.PIVOT_X, config.PIVOT_Y)
        self.renderer.draw_bob(bob_x, bob_y)

        # Draw trace
        if self.show_trace:
            self.renderer.draw_trace()

        # Render text information if enabled
        if config.SHOW_INFO:
            total_energy, ke, pe = self.pendulum.get_energy()
            fps = self.frame_limiter.get_fps()

            # Print info to console (since OpenGL text rendering requires additional setup)
            if self.frame_limiter.get_frame_count() % 60 == 0 and config.PRINT_FPS:
                angle_deg = self.pendulum.angle * 180 / 3.14159
                damping_status = "DECAYING" if self.params["damping"] > 0 else "CONSTANT"
                print(
                    f"Angle: {angle_deg:7.2f}° | "
                    f"Vel: {self.pendulum.angular_velocity:7.4f} rad/s | "
                    f"E_total: {total_energy:.6f} J | "
                    f"Status: {damping_status} | "
                    f"FPS: {fps:.1f}"
                )

    def update_physics(self):
        """Update physics simulation"""
        delta_time = self.frame_limiter.frame_complete()

        # Apply time scaling
        scaled_dt = delta_time * self.params["simulation_speed"]

        # Update pendulum
        self.pendulum.update(scaled_dt)

        # Add trace point
        if self.show_trace:
            bob_x, bob_y = self.pendulum.get_bob_position(config.PIVOT_X, config.PIVOT_Y)
            self.renderer.add_trace_point(bob_x, bob_y)

        # Record data
        self.accumulated_time += scaled_dt
        total_energy, ke, pe = self.pendulum.get_energy()

        if config.LOG_PHYSICS_DATA:
            self.recorder.record(
                time=self.accumulated_time,
                angle=self.pendulum.angle,
                angular_velocity=self.pendulum.angular_velocity,
                angular_acceleration=self.pendulum.angular_acceleration,
                total_energy=total_energy,
                kinetic_energy=ke,
                potential_energy=pe,
            )

        # Update real-time graph
        if self.graph:
            self.graph.add_data_point(
                time=self.accumulated_time,
                angle=self.pendulum.angle,
                velocity=self.pendulum.angular_velocity,
                ke=ke,
                pe=pe,
                total_energy=total_energy
            )
            if self.graph.should_update(self.accumulated_time, config.GRAPH_UPDATE_INTERVAL):
                self.graph.update(self.accumulated_time, config.GRAPH_HISTORY_LENGTH)

        # Validate physics
        if config.DEBUG_MODE:
            PhysicsValidator.validate_angle(self.pendulum.angle)
            PhysicsValidator.check_energy_conservation(total_energy, self.initial_energy)

    def reshape(self, width: int, height: int):
        """Handle window resize"""
        self.renderer.width = width
        self.renderer.height = height
        self.renderer.setup_projection()
        self.renderer.setup_viewport()

    def keyboard(self, key: bytes, x: int, y: int):
        """Handle keyboard input"""
        key_char = key.decode("utf-8") if isinstance(key, bytes) else key

        if key_char == " ":  # Space - Pause/Resume
            self.simulation_paused = not self.simulation_paused
            status = "PAUSED" if self.simulation_paused else "RUNNING"
            print(f"Simulation {status}")

        elif key_char.upper() == "R":  # Reset
            self.pendulum.reset(config.INITIAL_ANGLE)
            self.renderer.clear_trace()
            self.accumulated_time = 0.0
            total_energy, _, _ = self.pendulum.get_energy()
            self.initial_energy = total_energy
            if self.graph:
                self.graph.clear()
            print("Simulation RESET")

        elif key_char.upper() == "T":  # Toggle trace
            self.show_trace = not self.show_trace
            if not self.show_trace:
                self.renderer.clear_trace()
            status = "ON" if self.show_trace else "OFF"
            print(f"Trace {status}")

        elif key_char.upper() == "E":  # Export data
            self.recorder.export_csv("pendulum_data.csv")
            if self.graph:
                self.graph.save_plot("pendulum_graph.png")

        elif key_char == "\x1b" or key_char.upper() == "Q":  # ESC or Q - Quit
            print("Exiting simulation...")
            sys.exit(0)

    def toggle_pause(self):
        """Toggle pause state (called by control panel)"""
        self.simulation_paused = not self.simulation_paused
        status = "PAUSED" if self.simulation_paused else "RUNNING"
        print(f"Simulation {status}")

    def reset_simulation(self):
        """Reset simulation (called by control panel)"""
        self.pendulum.reset(config.INITIAL_ANGLE)
        self.renderer.clear_trace()
        self.accumulated_time = 0.0
        total_energy, _, _ = self.pendulum.get_energy()
        self.initial_energy = total_energy
        if self.graph:
            self.graph.clear()
        print("Simulation RESET")

    def toggle_trace(self):
        """Toggle trace visibility (called by control panel)"""
        self.show_trace = not self.show_trace
        if not self.show_trace:
            self.renderer.clear_trace()
        status = "ON" if self.show_trace else "OFF"
        print(f"Trace {status}")

    def export_data(self):
        """Export data and graph (called by control panel)"""
        self.recorder.export_csv("pendulum_data.csv")
        if self.graph:
            self.graph.save_plot("pendulum_graph.png")
        print("✓ Data exported to pendulum_data.csv")
        if self.graph:
            print("✓ Graph saved to pendulum_graph.png")

    def timer_callback(self, value):
        """Timer callback for continuous redrawing"""
        if self.simulation_running:
            glutPostRedisplay()
            glutTimerFunc(int(1000.0 / config.TARGET_FPS), self.timer_callback, 0)

    def run(self):
        """Start the simulation"""
        self.initialize_glut()
        glutMainLoop()


def main():
    """Main entry point"""
    # Show parameter input UI
    ui = ParameterInputUI()
    parameters = ui.run()
    
    if parameters is None:
        print("Simulation cancelled.")
        return
    
    # Create and run simulation with parameters
    simulation = PendulumSimulation(parameters)
    simulation.run()


if __name__ == "__main__":
    main()
