import cv2
import mediapipe as mp
import threading
import queue
import logging
import time
import numpy as np
from pynput import keyboard



mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

mp_drawing = mp.solutions.drawing_utils

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
import multiprocessing
from Utitlities.ThreadController.threadCommon import ThreadCommonQueue
from Utitlities.MouseHanlder.mouseCommon import mouse_thread_func
from Utitlities.ocr.ocrCommon import ocr_thread_func
from Utitlities.UIProcess.tooltip import ui_listener
if __name__ == "__main__":
    ui_queue = multiprocessing.Queue()
    ui_process = multiprocessing.Process(target=ui_listener,args=(ui_queue,))
    ui_process.start()

    MouseQueue = ThreadCommonQueue()
    mouse_thread = threading.Thread(target=mouse_thread_func, args=(MouseQueue,))
    mouse_thread.start()

    ocrQueue = ThreadCommonQueue()
    ocr_thread = threading.Thread(target=ocr_thread_func, args=(ocrQueue, ui_queue))
    ocr_thread.start()

    debug = 1
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
                    MouseQueue.set_event(("MOVE", (hand_pos[0]*1920,hand_pos[1]*1080)))
                    print(hand_pos[0]*1920,hand_pos[1]*1080)
                    if debug:
                        ocrQueue.set_event(("POS",(539, 75)))
                        debug = 0
                        print("ocr event sent")
                    # detected_gesture = detect_flick_gesture(hand_position_history)
                    # if detected_gesture:
                    #     controller.set_gesture(detected_gesture)

            cv2.imshow('MediaPipe Hands', frame)
            if cv2.waitKey(5) & 0xFF == 27:
                controller.set_gesture("QUIT")
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        MouseQueue.set_event(("QUIT",None))
        ocrQueue.set_event(("QUIT",None))
        ui_queue.put(("QUIT",None))
        thread.join()
        quit_thread.join()
        ocr_thread.join()
        mouse_thread.join()
        print("threads are done")
        ui_process.join()
        print("Application exited cleanly.")
        logging.info("Application exited cleanly.")