import mediapipe as mp
import numpy as np
import math

class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def is_finger_extended(self, landmarks, finger_tip_id, finger_pip_id, finger_mcp_id):
        """Check if a finger is extended based on landmark positions"""
        tip = landmarks[finger_tip_id]
        pip = landmarks[finger_pip_id] 
        mcp = landmarks[finger_mcp_id]
        
        # For thumb, use different logic
        if finger_tip_id == 4:  # Thumb
            return tip.x > pip.x if landmarks[0].x < landmarks[9].x else tip.x < pip.x
        
        # For other fingers, check if tip is above pip (extended)
        return tip.y < pip.y
    
    def recognize_gesture(self, hand_landmarks):
        """Recognize hand gesture from landmarks"""
        landmarks = hand_landmarks.landmark
        
        # Finger landmark IDs
        finger_tips = [4, 8, 12, 16, 20]   # Thumb, Index, Middle, Ring, Pinky tips
        finger_pips = [3, 6, 10, 14, 18]  # PIP joints
        finger_mcps = [2, 5, 9, 13, 17]   # MCP joints
        
        # Check which fingers are extended
        extended_fingers = []
        for i in range(5):
            if self.is_finger_extended(landmarks, finger_tips[i], finger_pips[i], finger_mcps[i]):
                extended_fingers.append(i)
        
        # Gesture recognition logic
        num_extended = len(extended_fingers)
        
        # FIST - no fingers extended or only thumb
        if num_extended == 0 or (num_extended == 1 and 0 in extended_fingers):
            return "fist"
        
        # OPEN PALM - all fingers extended
        elif num_extended >= 4:
            return "open_palm"
        
        # PINCH - thumb and index finger close together
        elif num_extended >= 2:
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            distance = self.calculate_distance(thumb_tip, index_tip)
            
            # If thumb and index are close (pinching)
            if distance < 0.05:  # Threshold for pinch detection
                return "pinch"
        
        # Default gesture
        return "unknown"
    
    def get_hand_center(self, hand_landmarks):
        """Get the center point of the hand"""
        landmarks = hand_landmarks.landmark
        
        x_coords = [lm.x for lm in landmarks]
        y_coords = [lm.y for lm in landmarks]
        
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        
        return (center_x, center_y)
    
    def get_gesture_confidence(self, hand_landmarks, gesture):
        """Calculate confidence score for detected gesture"""
        landmarks = hand_landmarks.landmark
        
        if gesture == "fist":
            # Check how closed the hand is
            finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
            palm_center = landmarks[9]  # Middle finger MCP as palm reference
            
            distances = []
            for tip_id in finger_tips:
                dist = self.calculate_distance(landmarks[tip_id], palm_center)
                distances.append(dist)
            
            # Lower distances mean more closed fist
            avg_distance = sum(distances) / len(distances)
            confidence = max(0, 1 - (avg_distance * 10))  # Scale confidence
            return confidence
        
        elif gesture == "open_palm":
            # Check how spread out the fingers are
            finger_tips = [4, 8, 12, 16, 20]
            palm_center = landmarks[9]
            
            distances = []
            for tip_id in finger_tips:
                dist = self.calculate_distance(landmarks[tip_id], palm_center)
                distances.append(dist)
            
            # Higher distances mean more open palm
            avg_distance = sum(distances) / len(distances)
            confidence = min(1, avg_distance * 5)  # Scale confidence
            return confidence
        
        elif gesture == "pinch":
            # Check how close thumb and index finger are
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            distance = self.calculate_distance(thumb_tip, index_tip)
            
            # Closer distance means higher pinch confidence
            confidence = max(0, 1 - (distance * 20))
            return confidence
        
        return 0.5  # Default confidence for unknown gestures