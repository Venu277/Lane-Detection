import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

def find_edges(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    return edges

def isolate_road(edges):
    """Hidden blinders aggressively shifted to the right to ignore the left guardrail."""
    height, width = edges.shape
    
    # We ignore the left 35% of the screen completely to block out the guardrail
    bottom_left = (int(width * 0.35), height)
    bottom_right = (width, height)
    top_left = (int(width * 0.45), int(height * 0.55))
    top_right = (width, int(height * 0.55))
    
    polygon = np.array([[bottom_left, bottom_right, top_right, top_left]], dtype=np.int32)
    mask = np.zeros_like(edges)
    cv2.fillPoly(mask, polygon, 255)
    
    return cv2.bitwise_and(edges, mask)

def make_coordinates(frame, line_parameters):
    try:
        slope, intercept = line_parameters
    except TypeError:
        return None
        
    y1 = frame.shape[0]           
    y2 = int(y1 * 0.55)           
    
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    
    return np.array([x1, y1, x2, y2])

def average_slope_intercept(frame, lines):
    left_fit = []
    right_fit = []
    
    if lines is None:
        return None, None
        
    for line in lines:
        # ROBUST UNPACKING: This automatically handles both OpenCV formats
        x1, y1, x2, y2 = line.reshape(4)
        
        if x1 == x2: continue 
        
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        intercept = parameters[1]
        
        if slope < -0.4: 
            left_fit.append((slope, intercept))
        elif slope > 0.4:
            right_fit.append((slope, intercept))
            
    left_line = make_coordinates(frame, np.average(left_fit, axis=0)) if left_fit else None
    right_line = make_coordinates(frame, np.average(right_fit, axis=0)) if right_fit else None
    
    return left_line, right_line

def draw_lane_overlay(frame, left_line, right_line):
    overlay = np.zeros_like(frame)
    
    if left_line is not None and right_line is not None:
        road_polygon = np.array([
            [left_line[0], left_line[1]],   
            [left_line[2], left_line[3]],   
            [right_line[2], right_line[3]], 
            [right_line[0], right_line[1]]  
        ], np.int32)
        
        cv2.fillPoly(overlay, [road_polygon], (0, 255, 0))
        cv2.line(overlay, (left_line[0], left_line[1]), (left_line[2], left_line[3]), (255, 0, 0), 8)
        cv2.line(overlay, (right_line[0], right_line[1]), (right_line[2], right_line[3]), (0, 0, 255), 8)
        
    return overlay

def process_frame(frame):
    edges = find_edges(frame)
    road_only = isolate_road(edges)
    
    lines = cv2.HoughLinesP(road_only, 2, np.pi/180, 50, np.array([]), minLineLength=30, maxLineGap=100)
    left_line, right_line = average_slope_intercept(frame, lines)
    lane_overlay = draw_lane_overlay(frame, left_line, right_line)
    
    final_output = cv2.addWeighted(frame, 1, lane_overlay, 0.35, 0)
    
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

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        result = process_frame(frame)
        
        cv2.namedWindow("Targeted Lane Detection", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Targeted Lane Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        cv2.imshow("Targeted Lane Detection", result)
        
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()