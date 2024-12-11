import time
import serial  # For serial communication
from dynamixel_sdk import *  # Dynamixel SDK
from pynput import keyboard
import threading  # For running the keyboard listener in a separate thread

# Constants for Dynamixel MX-28 motor
DXL_ID = 1
BAUDRATE = 57600
DEVICENAME = '/dev/ttyUSB0'  # Change to the correct port
PROTOCOL_VERSION = 2.0

# Serial communication setup fosr Arbotix-M
ser = serial.Serial(DEVICENAME, BAUDRATE)

# Create a PortHandler instance and PacketHandler instance
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

if not portHandler.openPort():
    print("Failed to open port!")
    exit()
print("Port opened successfully.")
if not portHandler.setBaudRate(BAUDRATE):
    print("Failed to set baudrate!")
    exit()
print(f"Baudrate set to {BAUDRATE}.")

# Flag to control program exit
exit_program = False

def on_press(key):
    """Detect the key press."""
    global exit_program
    try:
        if key.char == 's':  # If 's' key is pressed
            print("Key 's' pressed. Exiting the program.")
            exit_program = True  # Set the flag to exit the loop
            return False  # Stop listener
    except AttributeError:
        pass  # Handle special keys (e.g., function keys)

def set_motor_position(position, speed):
    """Moves the motor to a specified position with the given speed."""
    print(f"Setting motor speed to {speed}.")
    # Set motor speed (Goal Velocity)
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, 104, speed)  # Address 104 is Goal Velocity
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set speed: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Error: {packetHandler.getRxPacketError(dxl_error)}")
    else:
        print(f"Motor speed set to {speed}.")

    print(f"Setting motor position to {position}.")
    # Set the target position (Goal Position)
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, 116, position)  # Address 116 is Goal Position
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set position: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Error: {packetHandler.getRxPacketError(dxl_error)}")
    else:
        print(f"Motor moving to position {position} with speed {speed}.")

def read_button_state():
    """ Read button state from serial data sent by Arbotix-M """
    if ser.in_waiting > 0:
        button_state = ser.readline().decode('utf-8').strip()
        print(f"Button state: {button_state}")
        return button_state
    return None

def listen_for_keys():
    """Run the keyboard listener in a separate thread."""
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Start the key press listener in a separate threads
key_listener_thread = threading.Thread(target=listen_for_keys)
key_listener_thread.daemon = True  # Ensures the thread exits when the main program exits
key_listener_thread.start()

try:
    while not exit_program:
        print("Reading button state...")
        button_state = read_button_state()
        time.sleep(1)

        if button_state == 'BUTTON_1_PRESSED':
            print("Button 1 pressed. Motor moving clockwise.")
            set_motor_position(1023, 100)  # Move clockwise at very slow speed (speed 10)
            time.sleep(1)  # Simulate motor move duration
            print("Motor has moved clockwise.")

        elif button_state == 'BUTTON_2_PRESSED':
            print("Button 2 pressed. Motor moving counterclockwise.")
            set_motor_position(0, 100)  # Move counterclockwise at very slow speed (speed 10)
            time.sleep(1)  # Simulate motor move duration
            print("Motor has moved counterclockwise.")
        
        time.sleep(0.1)  # Add a small delay to avoid excessive CPU usage

except KeyboardInterrupt:
    print("Program interrupted.")
finally:
    ser.close()  # Close the serial port
    portHandler.closePort()  # Close the Dynamixel port
    print("Program exited cleanly.")
