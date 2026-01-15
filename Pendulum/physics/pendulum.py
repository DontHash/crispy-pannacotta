"""
Physics module for Pendulum Simulation
Implements the mathematical model of a simple pendulum using numerical integration
"""

import math
from typing import Tuple


class Pendulum:
    """
    Represents a simple pendulum with physics calculations.
    Uses Runge-Kutta 4th order integration for accurate motion simulation.
    """

    def __init__(
        self,
        length: float,
        mass: float,
        gravity: float,
        initial_angle: float,
        damping: float = 0.0,
    ):
        """
        Initialize the pendulum with physical parameters.

        Args:
            length: Length of the pendulum rod in units
            mass: Mass of the bob in kg
            gravity: Gravitational acceleration in m/s^2
            initial_angle: Initial angular displacement in radians
            damping: Damping coefficient (0 = no damping)
        """
        self.length = length
        self.mass = mass
        self.gravity = gravity
        self.damping = damping

        # State variables
        self.angle = initial_angle  # Angular position (theta)
        self.angular_velocity = 0.0  # dtheta/dt
        self.angular_acceleration = 0.0  # d²theta/dt²

    def _calculate_acceleration(
        self, angle: float, angular_velocity: float
    ) -> float:
        """
        Calculate angular acceleration using the pendulum equation.
        ω'' = -(g/L) * sin(θ) - (c * ω)
        where c is the damping coefficient

        Args:
            angle: Current angular position in radians
            angular_velocity: Current angular velocity

        Returns:
            Angular acceleration in rad/s²
        """
        # Gravitational torque component
        gravitational_component = -(self.gravity / self.length) * math.sin(angle)

        # Damping component (proportional to velocity)
        damping_component = -self.damping * angular_velocity

        return gravitational_component + damping_component

    def update(self, dt: float) -> None:
        """
        Update pendulum state using Runge-Kutta 4th order integration.
        This provides high accuracy while maintaining computational efficiency.

        Args:
            dt: Time step in seconds
        """
        # Current state
        theta = self.angle
        omega = self.angular_velocity

        # RK4 Step 1
        k1_omega = self._calculate_acceleration(theta, omega)
        k1_theta = omega

        # RK4 Step 2
        k2_omega = self._calculate_acceleration(theta + 0.5 * dt * k1_theta, omega + 0.5 * dt * k1_omega)
        k2_theta = omega + 0.5 * dt * k1_omega

        # RK4 Step 3
        k3_omega = self._calculate_acceleration(theta + 0.5 * dt * k2_theta, omega + 0.5 * dt * k2_omega)
        k3_theta = omega + 0.5 * dt * k2_omega

        # RK4 Step 4
        k4_omega = self._calculate_acceleration(theta + dt * k3_theta, omega + dt * k3_omega)
        k4_theta = omega + dt * k3_omega

        # Update state
        self.angle += (dt / 6.0) * (k1_theta + 2 * k2_theta + 2 * k3_theta + k4_theta)
        self.angular_velocity += (dt / 6.0) * (k1_omega + 2 * k2_omega + 2 * k3_omega + k4_omega)

        # Update acceleration
        self.angular_acceleration = self._calculate_acceleration(self.angle, self.angular_velocity)

    def get_bob_position(self, pivot_x: float, pivot_y: float) -> Tuple[float, float]:
        """
        Calculate the position of the pendulum bob in 2D space.

        Args:
            pivot_x: X-coordinate of the pivot point
            pivot_y: Y-coordinate of the pivot point

        Returns:
            Tuple of (bob_x, bob_y) coordinates
        """
        # Calculate bob position using trigonometry
        # The pendulum rotates around the pivot point
        bob_x = pivot_x + self.length * math.sin(self.angle)
        bob_y = pivot_y - self.length * math.cos(self.angle)
        return (bob_x, bob_y)

    def get_bob_velocity(self) -> Tuple[float, float]:
        """
        Calculate the velocity components of the bob.

        Returns:
            Tuple of (velocity_x, velocity_y)
        """
        # Velocity is perpendicular to the rod
        velocity_magnitude = self.length * self.angular_velocity
        velocity_x = velocity_magnitude * math.cos(self.angle)
        velocity_y = velocity_magnitude * math.sin(self.angle)
        return (velocity_x, velocity_y)

    def get_energy(self) -> Tuple[float, float, float]:
        """
        Calculate the total, kinetic, and potential energy of the pendulum.

        Returns:
            Tuple of (total_energy, kinetic_energy, potential_energy)
        """
        # Reference: potential energy is zero at the lowest point
        # Height of bob relative to lowest point: h = L - L*cos(θ) = L(1 - cos(θ))
        height = self.length * (1.0 - math.cos(self.angle))

        # Kinetic energy: KE = 0.5 * m * v²
        # where v = L * ω (linear velocity at distance L from pivot)
        kinetic_energy = 0.5 * self.mass * (self.length * self.angular_velocity) ** 2

        # Potential energy: PE = m * g * h
        potential_energy = self.mass * self.gravity * height

        # Total energy
        total_energy = kinetic_energy + potential_energy

        return (total_energy, kinetic_energy, potential_energy)

    def reset(self, initial_angle: float) -> None:
        """
        Reset the pendulum to initial conditions.

        Args:
            initial_angle: New initial angle in radians
        """
        self.angle = initial_angle
        self.angular_velocity = 0.0
        self.angular_acceleration = 0.0
