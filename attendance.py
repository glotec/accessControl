import numpy as np
import cv2
import face_recognition

video_capture = cv2.VideoCapture(0)

Glo_image = face_recognition.load_image_file('static/upload/Glo.jpg');
Esty_image = face_recognition.load_image_file('static/upload/IMG_20201107_142830_067.jpg');

glo_face_encoding = face_recognition.face_encodings(Glo_image)[0];
esty_face_encoding = face_recognition.face_encodings(Esty_image)[0];

known_face_encodings = [glo_face_encoding, esty_face_encoding];
known_face_names = ['Glo', 'Esty'];

while True:

    ret, frame = video_capture.read();

    # Converting the frame from OpenCV's BGR format to the RGB format
    rgb_frame = frame[:, :, ::-1];

    # Finding the face locations and encodings in each frame
    face_locations = face_recognition.face_locations(rgb_frame);
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations);

    # Now to loop through each face in this frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

        # Checking if the face is a match for known faces
        matches = face_recognition.compare_faces([known_face_encodings], face_encoding);

        name = 'Unknown';

        # Use the known face with the smallest vector distance to the new face
        face_distances = face_recognition.face_distance([known_face_encodings], face_encoding);
        best_match_index = np.argmin(face_distances);

        if matches[best_match_index]:
            name = known_face_names[best_match_index];


        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2);

        # Draw a label with the name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 0), cv2.FILLED);
        font = cv2.FONT_HERSHEY_DUPLEX;
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1);

    # Display the image
    cv2.imshow('Video', frame);

    # Hit 'q' on the keyboard to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break;

        video_capture.release();
        cv2.destroyAllWindows();