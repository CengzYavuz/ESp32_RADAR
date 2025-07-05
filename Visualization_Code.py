import threading
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial  # Make sure you have pyserial installed: pip install pyserial

# ================== CONFIGURATION ===================
SIMULATE = False  # Set to False to use hardware serial communication; True for simulation mode.
PORT = '/dev/ttyUSB0'  # Serial port where the ESP is connected.
BAUD_RATE = 115200  # Serial communication speed.

STEP_DEG = 4  # Motor (or simulated motor) moves 4° per step.
NUM_STEPS = 360 // STEP_DEG  # Total number of steps in one full 360° rotation.
MAX_RANGE = 400  # Maximum radar range (in centimeters).

# ================== SHARED STATE ===================
# These globals are used in both the serial/simulated reader and the visualization.
distances = [0.0] * NUM_STEPS  # Stores the distance measurement for each step (blue dot positions).
lock = threading.Lock()  # Ensures thread-safe updates for shared variables.
current_step = 0  # Current angular step (0 to NUM_STEPS-1).
direction = 1  # Sweep direction: 1 for normal, -1 for reverse.
is_running = True  # Indicates whether the motor/sweep is active.
last_theta = 0.0  # Last beam angle (in radians) used by the visualization.


# ================== SERIAL READER ===================
def serial_reader():
    """
    Opens a serial connection, sends the "RDY" startup signal,
    and continuously listens for incoming messages from the ESP.

    Expected messages:
      - "Distance:<value>" : A measurement reading.
      - "CDR"              : Command to change (reverse) the sweep direction.
    """
    global current_step, direction
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    except Exception as e:
        print("Error: Could not open serial port:", e)
        return

    print("Waiting 2 seconds for ESP device reset...")
    time.sleep(2)
    ser.write(b'RDY\r\n')  # Send the ready/start signal to the ESP.
    print("Sent RDY signal to ESP.")

    while True:
        try:
            line = ser.readline().decode(errors="ignore").strip()
            if not line:
                continue  # Ignore empty lines

            if line.startswith("Distance:"):
                try:
                    distance_value = float(line.split("Distance:")[1])
                    distances[current_step] = distance_value
                    print(f"Received distance: {distance_value} cm")
                except Exception as e:
                    print("Error parsing distance value:", e)
                    continue
            elif line == "FWR":
                with lock:
                    # Always advance the beam one step per distance reading
                    current_step = (current_step + direction) % NUM_STEPS
                print(f"Step {current_step})")

            elif line == "CDR":
                with lock:
                    direction *= -1  # Reverse the direction.
                print("Received DIRECTION CHANGE command.")
            else:
                print("Received unknown command:", line)

        except Exception as e:
            print("Error reading serial data:", e)


# ================== SIMULATED READER (optional) ===================
def simulated_reader():
    """
    If SIMULATE is True, this thread simulates incoming data.
    A random distance measurement is assigned to the current step,
    and the current_step is updated similarly to the hardware version.
    """
    global current_step, direction, is_running
    while True:
        with lock:
            if is_running:
                # Simulate a measured distance between 50 cm and MAX_RANGE.
                distances[current_step] = np.random.uniform(50, MAX_RANGE)
                current_step = (current_step + direction) % NUM_STEPS
        time.sleep(0.08)  # Simulate the combined 70 ms motor movement and 60 ms stabilization delay.


# ================== THREAD SELECTION ===================
if SIMULATE:
    threading.Thread(target=simulated_reader, daemon=True).start()
else:
    threading.Thread(target=serial_reader, daemon=True).start()

# ================== VISUALIZATION SETUP ===================
# Create the radar display.
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect("equal")
ax.set_xlim(-MAX_RANGE, MAX_RANGE)
ax.set_ylim(-MAX_RANGE, MAX_RANGE)
ax.axis("off")  # Hide the default axes for a cleaner radar look.

# Draw concentric circles (radar rings) for visual context.
for r in np.linspace(0, MAX_RANGE, 5)[1:]:
    theta = np.linspace(0, 2 * np.pi, 200)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    ax.plot(x, y, color="green", lw=0.5)

# Draw radial (spoke) lines every 45° and label them with their angle.
for angle in range(0, 360, 45):
    rad = np.deg2rad(angle)
    ax.plot([0, MAX_RANGE * np.cos(rad)], [0, MAX_RANGE * np.sin(rad)], color="green", lw=0.5)
    ax.text(1.05 * MAX_RANGE * np.cos(rad), 1.05 * MAX_RANGE * np.sin(rad),
            f"{angle}°", color="green", ha="center", va="center")

# Dynamic plot elements:
# 'beam_line' represents the current sweeping beam.
beam_line, = ax.plot([], [], color="lime", lw=2)
# 'dots' represents the distance measurement points (blue dots).
dots = ax.scatter([], [], c="blue", s=20)


# ================== ANIMATION UPDATE FUNCTION ===================
def update(frame):
    """
    Called periodically by FuncAnimation. It:
      - Copies the current distance measurements and current_step.
      - Computes the (x, y) positions for each measurement (blue dots) using polar-to-Cartesian conversion.
      - Updates the sweeping beam line based on the current step.
    """
    global last_theta
    with lock:
        current_distances = list(distances)  # Get a snapshot of distance measurements.
        idx = current_step
        running = is_running

    # Get all angle positions (in radians) for the measurement steps.
    angles = np.deg2rad(np.arange(0, 360, STEP_DEG))
    xs = np.array(current_distances) * np.cos(angles)
    ys = np.array(current_distances) * np.sin(angles)
    dots.set_offsets(np.column_stack([xs, ys]))

    # Update the beam's angle:
    # If the motor is running, use the current step's angle.
    if running:
        last_theta = angles[idx]
    # Draw the beam from the center to the edge of the radar.
    beam_line.set_data([0, MAX_RANGE * np.cos(last_theta)],
                       [0, MAX_RANGE * np.sin(last_theta)])
    return dots, beam_line


# ================== CREATE ANIMATION ===================
# The animation updates every 50ms.
ani = FuncAnimation(fig, update, interval=50, blit=True, cache_frame_data=False)

print("Radar visualization started.")
plt.show()

