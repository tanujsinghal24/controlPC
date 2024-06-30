import cv2
import numpy as np
import easyocr
import pyautogui
from pynput import mouse
import time

global reader

def initOcr():
    global reader
    reader = easyocr.Reader(['en'], gpu=True)

def capture_screenshot_around_point(point, region_width=300, region_height=100):
    x, y = point
    region_top_left_x = x - region_width // 2
    region_top_left_y = y - region_height // 2
    region = (region_top_left_x, region_top_left_y, region_width, region_height)
    screenshot = pyautogui.screenshot(region=region)
    screenshot_np = np.array(screenshot)
    screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)
    return screenshot_rgb, (region_top_left_x, region_top_left_y)


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def get_mouse_click_position():
    print("Click on the screen to capture position...")

    click_position = []

    def on_click(x, y, button, pressed):
        if pressed:
            click_position.append((int(x), int(y)))
            return False

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    print(f"Mouse clicked at: {click_position[0]}")
    return click_position[0]


# def find_closest_word(results, click_point):
#     click_x, click_y = click_point
#     min_distance = float('inf')
#     closest_word = None
#
#     for bbox, text, prob in results:
#         words = text.split()
#         num_words = len(words)
#         top_left, _, bottom_right, _ = bbox
#
#         word_width = (bottom_right[0] - top_left[0]) / num_words
#         word_height = bottom_right[1] - top_left[1]
#         final_center = (0,0)
#         for i, word in enumerate(words):
#             word_x_center = top_left[0] + (i + 0.5) * word_width
#             word_y_center = top_left[1] + 0.5 * word_height
#             distance = np.sqrt((click_x - word_x_center) ** 2 + (click_y - word_y_center) ** 2)
#
#             if distance < min_distance:
#                 min_distance = distance
#                 word_top_left = (top_left[0] + i * word_width, top_left[1])
#                 word_bottom_right = (word_top_left[0] + word_width, word_top_left[1] + word_height)
#                 closest_word = (word, prob, (word_top_left, word_bottom_right))
#                 print()
#     return closest_word
def find_closest_word(results, click_point, region_top_left):
    click_x, click_y = click_point
    min_distance = float('inf')
    closest_word = None
    center_point = None

    for bbox, text, prob in results:
        words = text.split()
        num_words = len(words)
        top_left, _, bottom_right, _ = bbox

        word_width = (bottom_right[0] - top_left[0]) / num_words
        word_height = bottom_right[1] - top_left[1]

        for i, word in enumerate(words):
            word_x_center = top_left[0] + (i + 0.5) * word_width
            word_y_center = top_left[1] + 0.5 * word_height
            distance = np.sqrt((click_x - word_x_center) ** 2 + (click_y - word_y_center) ** 2)

            if distance < min_distance:
                min_distance = distance
                word_top_left = (top_left[0] + i * word_width, top_left[1])
                word_bottom_right = (word_top_left[0] + word_width, word_top_left[1] + word_height)
                # Adjust the center point relative to the whole screen
                center_point = ((word_top_left[0] + word_bottom_right[0]) / 2 + region_top_left[0],
                                (word_top_left[1] + word_bottom_right[1]) / 2 + region_top_left[1])
                closest_word = (word, prob, (word_top_left, word_bottom_right))

    return closest_word, center_point


def do_processing(arg):
    start_time = time.time()
    point=arg
    if not arg:
        initOcr()
        point = get_mouse_click_position()#individual testing
    print("do processing start")
    region_width = 300
    region_height = 100

    # Temporarily move the cursor out of the screenshot region
    #
    original_position = pyautogui.position()
    time.sleep(0.200)
    pyautogui.moveTo(1, 1)
    pyautogui.click()
    screenshot, region_top_left = capture_screenshot_around_point(point, region_width, region_height)

    pyautogui.moveTo(original_position)

    preprocessed_image = preprocess_image(screenshot)


    results = reader.readtext(preprocessed_image)

    for bbox, text, prob in results:
        print(f"Detected text: {text} with confidence: {prob}")

    relative_point = (region_width // 2, region_height // 2)
    closest_word, center = find_closest_word(results, relative_point, region_top_left )

    if closest_word:
        text, prob, bbox = closest_word
        print(f"Closest recognized text: {text} with confidence: {prob}")

        # Draw bounding box and text on the image
        (top_left, bottom_right) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))
        # cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
        # cv2.putText(screenshot, text, top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        # Display the image with OCR results (optional)
        # cv2.imshow('OCR Result', screenshot)
        print(f"prediction time = {time.time() - start_time}")

        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return closest_word, center
    else:
        print("No text found in the captured region.")
        return None, None

if __name__ == "__main__":
    import multiprocessing
    from Utitlities.UIProcess.tooltip import ui_listener
    ui_queue = multiprocessing.Queue()
    ui_process = multiprocessing.Process(target=ui_listener, args=(ui_queue,))
    ui_process.start()
    _,center = do_processing(None)
    ui_queue.put(("OCR_RES", ("Camera is the best sensor in the world is it not ..heheheheheheheh", center)))
    time.sleep(20)
    ui_queue.put(("QUIT", None))
    ui_process.join()