import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from transformers import pipeline
from PIL import Image

print("Loading Deep Learning Model (SegFormer)...")
segmenter = pipeline("image-segmentation", model="nvidia/segformer-b0-finetuned-cityscapes-1024-1024")
print("AI Model Successfully Loaded!")

def process_frame_ai(frame):
    height, width = frame.shape[:2]
    
    small_frame = cv2.resize(frame, (512, 256))
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_frame)
    
    results = segmenter(pil_image)
    
    road_mask = None
    for result in results:
        if result['label'] == 'road':
            road_mask = np.array(result['mask'])
            break
            
    if road_mask is None:
        return frame 
        
    road_mask = cv2.resize(road_mask, (width, height), interpolation=cv2.INTER_NEAREST)
    
    color_overlay = np.zeros_like(frame)
    color_overlay[road_mask == 255] = [0, 255, 0] 
    
    final_output = cv2.addWeighted(frame, 1, color_overlay, 0.4, 0)
    return final_output

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    video_path = filedialog.askopenfilename(
        title="Select your dashcam video",
        filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All Files", "*.*")]
    )
    
    if not video_path:
        exit()
        
    cap = cv2.VideoCapture(video_path)

    print("Processing video with Deep Learning... (Press 'q' to quit)")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        result = process_frame_ai(frame)
        
        cv2.namedWindow("AI Lane Detection", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("AI Lane Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        cv2.imshow("AI Lane Detection", result)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()