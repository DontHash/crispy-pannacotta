"""
Utility module for helper functions
Provides common utilities for the simulation
"""

import time
from typing import List


class Timer:
    """High-resolution timer for frame rate control and profiling"""

    def __init__(self):
        """Initialize the timer"""
        self.start_time = time.perf_counter()
        self.last_time = self.start_time
        self.current_time = self.start_time
        self.delta_time = 0.0
        self.total_elapsed = 0.0

    def update(self) -> float:
        """
        Update timer and return delta time since last call.

        Returns:
            Delta time in seconds since last update call
        """
        self.current_time = time.perf_counter()
        self.delta_time = self.current_time - self.last_time
        self.total_elapsed = self.current_time - self.start_time
        self.last_time = self.current_time
        return self.delta_time

    def reset(self) -> None:
        """Reset the timer"""
        self.start_time = time.perf_counter()
        self.last_time = self.start_time
        self.current_time = self.start_time
        self.delta_time = 0.0
        self.total_elapsed = 0.0

    def get_elapsed(self) -> float:
        """Get total elapsed time since initialization"""
        return self.total_elapsed

    def get_delta_time(self) -> float:
        """Get delta time from last update"""
        return self.delta_time


class FrameRateLimiter:
    """Limits frame rate to a target FPS"""

    def __init__(self, target_fps: float):
        """
        Initialize frame rate limiter.

        Args:
            target_fps: Target frames per second
        """
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.timer = Timer()
        self.frame_count = 0
        self.actual_fps = 0.0
        self.fps_update_counter = 0

    def should_continue_frame(self) -> bool:
        """
        Check if frame time has been exceeded (for frame rate limiting).

        Returns:
            True if more time can be spent on this frame, False if frame should finish
        """
        self.timer.update()
        return self.timer.get_delta_time() < self.frame_time

    def frame_complete(self) -> float:
        """
        Mark frame as complete and wait if necessary to maintain target FPS.

        Returns:
            Actual delta time used for this frame
        """
        elapsed = self.timer.update()

        # Sleep if frame finished too early
        if elapsed < self.frame_time:
            sleep_time = self.frame_time - elapsed
            time.sleep(sleep_time)

        self.frame_count += 1
        self.fps_update_counter += 1

        # Update FPS calculation every 60 frames
        if self.fps_update_counter >= 60:
            self.actual_fps = self.frame_count / self.timer.get_elapsed()
            self.fps_update_counter = 0

        return self.frame_time

    def get_fps(self) -> float:
        """Get current frames per second"""
        return self.actual_fps

    def get_frame_count(self) -> int:
        """Get total frame count since initialization"""
        return self.frame_count


class DataRecorder:
    """Records simulation data for analysis and logging"""

    def __init__(self, max_records: int = 10000):
        """
        Initialize data recorder.

        Args:
            max_records: Maximum number of records to keep
        """
        self.max_records = max_records
        self.data: List[dict] = []

    def record(
        self,
        time: float,
        angle: float,
        angular_velocity: float,
        angular_acceleration: float,
        total_energy: float,
        kinetic_energy: float,
        potential_energy: float,
    ) -> None:
        """
        Record simulation data point.

        Args:
            time: Simulation time
            angle: Angular position
            angular_velocity: Angular velocity
            angular_acceleration: Angular acceleration
            total_energy: Total energy
            kinetic_energy: Kinetic energy
            potential_energy: Potential energy
        """
        record = {
            "time": time,
            "angle": angle,
            "angular_velocity": angular_velocity,
            "angular_acceleration": angular_acceleration,
            "total_energy": total_energy,
            "kinetic_energy": kinetic_energy,
            "potential_energy": potential_energy,
        }
        self.data.append(record)

        # Maintain maximum record limit
        if len(self.data) > self.max_records:
            self.data.pop(0)

    def clear(self) -> None:
        """Clear all recorded data"""
        self.data.clear()

    def get_data(self) -> List[dict]:
        """Get all recorded data"""
        return self.data.copy()

    def export_csv(self, filename: str) -> None:
        """
        Export recorded data to CSV file.

        Args:
            filename: Output CSV filename
        """
        if not self.data:
            print("No data to export")
            return

        try:
            import csv

            with open(filename, "w", newline="") as csvfile:
                fieldnames = self.data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)
            print(f"Data exported to {filename}")
        except Exception as e:
            print(f"Error exporting data: {e}")


class PhysicsValidator:
    """Validates physics calculations and energy conservation"""

    @staticmethod
    def check_energy_conservation(
        energy: float, reference_energy: float, tolerance: float = 0.01
    ) -> bool:
        """
        Check if energy is conserved within tolerance.

        Args:
            energy: Current total energy
            reference_energy: Initial total energy
            tolerance: Acceptable energy change percentage (default 1%)

        Returns:
            True if energy is conserved within tolerance
        """
        if reference_energy == 0:
            return True

        relative_change = abs(energy - reference_energy) / abs(reference_energy)
        return relative_change <= tolerance

    @staticmethod
    def validate_angle(angle: float, max_angle: float = 3.14159) -> bool:
        """
        Validate that angle is within physical limits.

        Args:
            angle: Angle to validate in radians
            max_angle: Maximum allowed angle (default π)

        Returns:
            True if angle is valid
        """
        return -max_angle <= angle <= max_angle
