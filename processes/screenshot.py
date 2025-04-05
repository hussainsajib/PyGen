import cv2

def extract_frame(video_path: str):
    # Open the video file
    frame_time = 1
    screenshot_name = f'screenshot_{video_path.split("/")[-1].split(".")[0]}.png'
    output_image_path = f'exported_data/screenshots/{screenshot_name}'
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}.")
        return

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = total_frames / fps

    if frame_time > video_duration:
        print(f'Error: Specified time {frame_time} exceeds video duration {video_duration:.2f} seconds.')
        return

    # Calculate the frame number
    frame_number = int(frame_time * fps)
    
    # Set the video position to the desired frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    # Read the frame
    ret, frame = cap.read()
    if ret:
        # Save the frame as an image
        cv2.imwrite(output_image_path, frame)
        print(f"Thumbnail at {frame_time}s saved as {output_image_path}.")
    else:
        print(f"Error: Could not read frame at {frame_time}s.")

    # Release the video capture
    cap.release()
