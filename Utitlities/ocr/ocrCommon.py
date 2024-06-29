from Utitlities.ocr.ocr import do_processing, initOcr
import multiprocessing
def ocr_thread_func(ocrQueue, ui_queue):
    print("OCR Thread begin")
    initOcr()
    print("OCR init done")
    while True:
        event = ocrQueue.get_event()
        eventType, arg = event
        print(event)
        if eventType == "QUIT":
            break
        elif eventType == "POS":
            word ,center = do_processing(arg)
            if word:
                text, prob, bbox = word
                print(f"got word {word} in thread")
                ui_queue.put(("OCR_RES",("Camera is the best sensor in the world is it not ..heheheheheheheh",center)))
# initOcr()