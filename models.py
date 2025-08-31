import cv2
import face_recognition
import numpy as np

def encode_face(image_bgr):
    """Return a 128-d embedding or None."""
    if image_bgr is None:
        return None
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb, model='hog')  # fast; 'cnn' for GPU
    if not boxes:
        return None
    encs = face_recognition.face_encodings(rgb, boxes)
    return encs[0] if encs else None

def compare_faces(known_encodings, unknown_encoding, tolerance=0.5):
    if not known_encodings:
        return None
    matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance)
    dists = face_recognition.face_distance(known_encodings, unknown_encoding)
    if len(dists) == 0:
        return None
    best_i = int(np.argmin(dists))
    if matches[best_i]:
        return best_i
    return None
