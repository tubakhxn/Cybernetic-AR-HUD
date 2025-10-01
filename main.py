"""
Cybernetic AR HUD - Real-Time Face & Hand Tracking
Created by: Tuba Khan (@tubakhxn)
GitHub: https://github.com/tubakhxn

A futuristic cyberpunk-style AR/HUD overlay system that tracks 
face, hands, and body in real-time using MediaPipe and OpenCV.

Please give credit when using this code!
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from hud import CyberneticHUD
from gestures import GestureRecognizer
from utils import FPSCounter

class CyborgARSystem:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize face mesh and hands
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize pose tracking for skeleton arm
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize components
        self.hud = CyberneticHUD()
        self.gesture_recognizer = GestureRecognizer()
        self.fps_counter = FPSCounter()
        
        # System state
        self.cyborg_evolution = 58.2  # Starting percentage like in reference
        self.borg_level = 8.2
        self.current_gesture = "none"
        self.face_detected = False
        self.scanning_active = False
        self.evolution_progress = 0
        
    def process_frame(self, frame):
        """Process each frame for face, hand, and pose detection"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process face mesh
        face_results = self.face_mesh.process(frame_rgb)
        
        # Process hands
        hand_results = self.hands.process(frame_rgb)
        
        # Process pose for skeleton arm tracking
        pose_results = self.pose.process(frame_rgb)
        
        # Update face detection status
        self.face_detected = face_results.multi_face_landmarks is not None
        
        # Process gestures
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.current_gesture = self.gesture_recognizer.recognize_gesture(hand_landmarks)
        else:
            self.current_gesture = "none"
        
        # Update system state based on gestures
        self.update_system_state()
        
        # Draw HUD overlays
        frame = self.hud.draw_complete_hud(
            frame, 
            face_results.multi_face_landmarks if face_results.multi_face_landmarks else None,
            hand_results.multi_hand_landmarks if hand_results.multi_hand_landmarks else None,
            pose_results.pose_landmarks if pose_results.pose_landmarks else None,
            self.cyborg_evolution,
            self.borg_level,
            self.current_gesture,
            self.face_detected,
            self.scanning_active
        )
        
        # Draw FPS
        fps = self.fps_counter.get_fps()
        cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1] - 120, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return frame
    
    def update_system_state(self):
        """Update system state based on current gesture"""
        if self.current_gesture == "open_palm":
            # Slowly increase evolution
            self.cyborg_evolution = min(100.0, self.cyborg_evolution + 0.1)
            self.borg_level = min(10.0, self.borg_level + 0.05)
            
        elif self.current_gesture == "fist":
            # Activate evolution progress
            self.evolution_progress = min(100, self.evolution_progress + 2)
            if self.evolution_progress >= 100:
                self.cyborg_evolution = min(100.0, self.cyborg_evolution + 5)
                self.evolution_progress = 0
                
        elif self.current_gesture == "pinch":
            # Activate scanning
            self.scanning_active = True
        else:
            self.scanning_active = False
    
    def run(self):
        """Main application loop"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("🤖 CYBORG AR SYSTEM INITIALIZING...")
        print("👋 Show your hand gestures:")
        print("   • Open Palm → Circuit overlays")
        print("   • Fist → Evolution progress") 
        print("   • Pinch → Face scanning")
        print("   • Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process frame
            frame = self.process_frame(frame)
            
            # Update FPS counter
            self.fps_counter.update()
            
            # Display frame
            cv2.imshow('Cybernetic AR HUD', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    system = CyborgARSystem()
    system.run()