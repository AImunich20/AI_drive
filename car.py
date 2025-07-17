import cv2
import collections

person_start_time = None
already_alerted = False

def car(cap, model, current_time, last_detection_time):
    global person_start_time, already_alerted

    success, frame = cap.read()
    if not success:
        return None, "no frame", last_detection_time, already_alerted

    results = model(frame)
    annotated_frame = results[0].plot()

    for r in results:
        boxes = r.boxes
        labels = [model.names.get(int(box.cls), "Unknown") for box in boxes]

        countclass = collections.Counter(labels)
        cperson = countclass.get('person', 0)

        cv2.imshow("people", annotated_frame)

        if cperson >= 1:
            if person_start_time is None:
                person_start_time = current_time
                already_alerted = False

            time_count = current_time - person_start_time

            if time_count >= 20 and not already_alerted:
                filename = "detected_sleep.jpg"
                cv2.imwrite(filename, annotated_frame)
                last_detection_time = current_time
                already_alerted = True

            return annotated_frame, "have people", last_detection_time, already_alerted
        else:
            person_start_time = None
            already_alerted = False

    return annotated_frame, "no people", last_detection_time, already_alerted
