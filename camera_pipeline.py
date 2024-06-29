# import time
# import functools
# def timeit(func):
#     @functools.wraps(func)
#     def wrapper(*arg, **kwargs):
#         start_time = time.time()
#         res = func()
#         end_time = time.time()
#         print(f"total time taken is {end_time - start_time}")
#         return res
#     return wrapper
#
# @timeit
# def gent():
#     gen = (x**2 for x in range(1,100000000000))
#     s = 0
#     for i in range(1,10):
#         # s = s + next(gen)
#         print(next(gen))
#     print(s)
#
# @timeit
# def li():
#     lit = [x**2 for x in range(1,10000000)]
#     s = 0;
#     for i in range(0,10):
#         # s = s + lit[i]
#         print(i)
#     print(s)
#
# gent()
# li()
#
import cv2
import mediapipe as mp
import threading
import queue
import logging
import time
import numpy as np
import tkinter as tk
from pynput import keyboard


# Initialize MediaPipe Hands.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

mp_drawing = mp.solutions.drawing_utils

# Initialize the webcam.
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    logging.error("Error: Could not open webcam.")
    exit()


class GestureController:
    def __init__(self):
        self.gesture_queue = queue.Queue()
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # Cooldown period in seconds

    def set_gesture(self, gesture):
        current_time = time.time()
        if current_time - self.last_gesture_time > self.gesture_cooldown:
            self.gesture_queue.put(gesture)
            self.last_gesture_time = current_time

    def get_gesture(self):
        return self.gesture_queue.get()


def keyboard_thread(controller):
    logging.info("Keyboard thread started.")
    while True:
        gesture = controller.get_gesture()
        if gesture == "NEXT":
            logging.info("Gesture detected: NEXT")
            keyboard.Controller().press(keyboard.Key.right)
            keyboard.Controller().release(keyboard.Key.right)
        elif gesture == "PREVIOUS":
            logging.info("Gesture detected: PREVIOUS")
            keyboard.Controller().press(keyboard.Key.left)
            keyboard.Controller().release(keyboard.Key.left)
        elif gesture == "QUIT":
            logging.info("Received QUIT gesture. Exiting Keyboard thread.")
            break


controller = GestureController()
thread = threading.Thread(target=keyboard_thread, args=(controller,))
thread.start()

# History to store hand positions
hand_position_history = []
fps = 0
start_time = time.time()


def detect_flick_gesture(hand_position_history, threshold=20, frames=60):
    if len(hand_position_history) < frames:
        return None

    # Calculate the difference between the start and end points
    start_pos = np.array(hand_position_history[0])
    end_pos = np.array(hand_position_history[-1])
    movement_vector = end_pos - start_pos

    # Calculate the speed of movement
    speed = np.linalg.norm(movement_vector) / frames

    # Determine if it is a flick gesture
    if speed > threshold:
        if movement_vector[0] > 0:
            return "NEXT"
        elif movement_vector[0] < 0:
            return "PREVIOUS"

    return None


def check_for_quit(controller):
    def on_press(key):
        try:
            if key == keyboard.Key.esc:
                controller.set_gesture("QUIT")
                return False
        except AttributeError:
            pass

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


quit_thread = threading.Thread(target=check_for_quit, args=(controller,))
quit_thread.start()


def update_fps():
    global fps, start_time
    end_time = time.time()
    fps = 1 / (end_time - start_time)
    start_time = end_time


def create_transparent_window():
    window = tk.Tk()
    window.attributes("-topmost", True)
    window.attributes("-alpha", 0.3)  # Set window transparency
    window.overrideredirect(1)
    window.geometry("400x200+100+100")
    return window


def update_transparent_window(label, window):
    hand_history_length = len(hand_position_history)
    label.config(text=f"FPS: {fps:.2f}\nHand History Length: {hand_history_length}")
    window.after(100, update_transparent_window, label, window)


# Create a transparent window using tkinter
transparent_window = create_transparent_window()
transparent_label = tk.Label(transparent_window, text="", font=("Helvetica", 16), bg="white")
transparent_label.pack(padx=10, pady=10)

# Start updating the transparent window
transparent_window.after(100, update_transparent_window, transparent_label, transparent_window)

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            logging.error("Error: Failed to capture frame.")
            break

        update_fps()
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_pos = (hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x,
                            hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y)
                hand_position_history.append(hand_pos)

                # Keep the history to the last 60 frames
                if len(hand_position_history) > 60:
                    hand_position_history.pop(0)

                detected_gesture = detect_flick_gesture(hand_position_history)
                if detected_gesture:
                    controller.set_gesture(detected_gesture)

        cv2.imshow('MediaPipe Hands', frame)
        if cv2.waitKey(5) & 0xFF == 27:
            controller.set_gesture("QUIT")
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    thread.join()
    quit_thread.join()
    logging.info("Application exited cleanly.")
    transparent_window.destroy()