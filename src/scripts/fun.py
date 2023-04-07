import cv2
import numpy as np

def main():
    udp_ip = "35.0.26.70"
    udp_port = 5200

    # Define the UDP video stream URL
    video_stream_url = f"udp://{udp_ip}:{udp_port}"

    # Open the video stream
    cap = cv2.VideoCapture(video_stream_url)

    if not cap.isOpened():
        print(f"Error: Unable to open video stream at {video_stream_url}")
        return

    while True:
        # Read a frame from the video stream
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read a frame from the video stream")
            break

        # Apply the Gaussian filter to the frame
        gaussian_filtered_frame = cv2.GaussianBlur(frame, (15, 15), 0)

        # Display the original and filtered frames side by side
        combined_frame = np.hstack((frame, gaussian_filtered_frame))
        cv2.imshow("Original (Left) vs Gaussian Filtered (Right)", combined_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the video capture and close all windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
