import cv2
import numpy as np
import math
import time

class CyberneticHUD:
    def __init__(self):
        self.frame_count = 0
        self.pulse_time = 0
        self.scan_angle = 0
        self.circuit_alpha = 0.7
        
        # Colors (BGR format)
        self.cyan = (255, 255, 0)
        self.green = (0, 255, 0)
        self.red = (0, 0, 255)
        self.orange = (0, 165, 255)
        self.white = (255, 255, 255)
        self.blue = (255, 0, 0)
        
    def draw_skeleton_arm(self, frame, pose_landmarks=None):
        """Draw the skeleton arm wireframe that tracks real arm movement"""
        height, width = frame.shape[:2]
        
        pulse = abs(math.sin(time.time() * 2)) * 0.3 + 0.7
        arm_color = (int(255 * pulse), int(255 * pulse), int(255 * pulse))  # White pulsing
        
        if pose_landmarks:
            # Use real pose landmarks to draw skeleton arm
            landmarks = pose_landmarks.landmark
            
            # Get arm joint positions (left arm - matching reference images)
            left_shoulder = landmarks[11]  # Left shoulder
            left_elbow = landmarks[13]     # Left elbow  
            left_wrist = landmarks[15]     # Left wrist
            left_pinky = landmarks[17]     # Left pinky
            left_index = landmarks[19]     # Left index
            left_thumb = landmarks[21]     # Left thumb
            
            # Convert normalized coordinates to pixel coordinates
            shoulder_pos = (int(left_shoulder.x * width), int(left_shoulder.y * height))
            elbow_pos = (int(left_elbow.x * width), int(left_elbow.y * height))
            wrist_pos = (int(left_wrist.x * width), int(left_wrist.y * height))
            pinky_pos = (int(left_pinky.x * width), int(left_pinky.y * height))
            index_pos = (int(left_index.x * width), int(left_index.y * height))
            thumb_pos = (int(left_thumb.x * width), int(left_thumb.y * height))
            
            # Draw main arm bones following your real arm
            cv2.line(frame, shoulder_pos, elbow_pos, arm_color, 4)
            cv2.line(frame, elbow_pos, wrist_pos, arm_color, 4)
            
            # Draw hand connections
            cv2.line(frame, wrist_pos, thumb_pos, arm_color, 3)
            cv2.line(frame, wrist_pos, index_pos, arm_color, 3)
            cv2.line(frame, wrist_pos, pinky_pos, arm_color, 3)
            
            # Draw joints as pulsing circles
            joints = [shoulder_pos, elbow_pos, wrist_pos, thumb_pos, index_pos, pinky_pos]
            
            for joint in joints:
                if 0 <= joint[0] < width and 0 <= joint[1] < height:  # Check bounds
                    cv2.circle(frame, joint, int(8 + pulse * 4), arm_color, -1)
                    cv2.circle(frame, joint, int(10 + pulse * 4), self.cyan, 2)
            
            # Add skeleton wireframe extensions for more detail
            # Calculate additional joint positions based on arm direction
            if all(0 <= pos[0] < width and 0 <= pos[1] < height for pos in [shoulder_pos, elbow_pos, wrist_pos]):
                # Add forearm detail lines
                forearm_dir_x = (wrist_pos[0] - elbow_pos[0]) // 3
                forearm_dir_y = (wrist_pos[1] - elbow_pos[1]) // 3
                
                mid_forearm = (elbow_pos[0] + forearm_dir_x, elbow_pos[1] + forearm_dir_y)
                cv2.line(frame, elbow_pos, mid_forearm, arm_color, 2)
                cv2.circle(frame, mid_forearm, 6, arm_color, -1)
                cv2.circle(frame, mid_forearm, 8, self.cyan, 1)
        
        else:
            # Fallback static skeleton arm when no pose detected
            x_offset, y_offset = 50, 150
            shoulder = (x_offset + 50, y_offset)
            elbow = (x_offset + 120, y_offset + 80)
            wrist = (x_offset + 180, y_offset + 120)
            
            # Draw static arm
            cv2.line(frame, shoulder, elbow, arm_color, 3)
            cv2.line(frame, elbow, wrist, arm_color, 3)
            
            joints = [shoulder, elbow, wrist]
            for joint in joints:
                cv2.circle(frame, joint, 6, arm_color, -1)
                cv2.circle(frame, joint, 8, self.cyan, 1)

    def draw_neural_network(self, frame, x_offset=50, y_offset=100):
        """Draw the neural network wireframe like in reference images"""
        height, width = frame.shape[:2]
        
        # Neural network nodes and connections
        nodes = [
            (x_offset, y_offset),
            (x_offset, y_offset + 60),
            (x_offset, y_offset + 120),
            (x_offset, y_offset + 180),
            (x_offset + 100, y_offset + 30),
            (x_offset + 100, y_offset + 90),
            (x_offset + 100, y_offset + 150),
            (x_offset + 200, y_offset + 60),
            (x_offset + 200, y_offset + 120)
        ]
        
        # Draw connections
        connections = [
            (0, 4), (0, 5), (1, 4), (1, 5), (1, 6),
            (2, 5), (2, 6), (3, 6), (4, 7), (4, 8),
            (5, 7), (5, 8), (6, 7), (6, 8)
        ]
        
        pulse = abs(math.sin(time.time() * 2)) * 0.5 + 0.5
        
        for start_idx, end_idx in connections:
            start = nodes[start_idx]
            end = nodes[end_idx]
            alpha = int(255 * pulse)
            color = (alpha, 255, alpha)
            cv2.line(frame, start, end, color, 2)
        
        # Draw nodes
        for i, node in enumerate(nodes):
            size = 8 + int(pulse * 4)
            cv2.circle(frame, node, size, self.cyan, -1)
            cv2.circle(frame, node, size + 2, self.white, 1)
        
        # Add data flow animation - rectangular modules like in reference
        flow_positions = [
            (x_offset - 30, y_offset - 15),
            (x_offset - 30, y_offset + 45),
            (x_offset - 30, y_offset + 105),
            (x_offset - 30, y_offset + 165)
        ]
        
        for i, pos in enumerate(flow_positions):
            # Draw rectangular data modules
            cv2.rectangle(frame, pos, (pos[0] + 20, pos[1] + 12), self.cyan, 2)
            cv2.rectangle(frame, (pos[0] + 2, pos[1] + 2), (pos[0] + 18, pos[1] + 10), self.cyan, -1)
            # Add connection dots
            cv2.circle(frame, (pos[0] + 25, pos[1] + 6), 3, self.white, -1)
    
    def draw_progress_bar(self, frame, x, y, width, height, progress, label, color):
        """Draw animated progress bar"""
        # Background
        cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
        cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
        
        # Fill
        fill_width = int((progress / 100.0) * width)
        if fill_width > 0:
            cv2.rectangle(frame, (x + 2, y + 2), (x + fill_width - 2, y + height - 2), color, -1)
        
        # Animated scan line
        scan_pos = int((time.time() * 100) % width)
        cv2.line(frame, (x + scan_pos, y), (x + scan_pos, y + height), self.white, 1)
        
        # Label
        cv2.putText(frame, f"{label}: {progress:.1f}% complete", 
                   (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def draw_crosshair(self, frame, center, size=50):
        """Draw targeting crosshair"""
        x, y = center
        pulse = abs(math.sin(time.time() * 3)) * 0.3 + 0.7
        color = (int(255 * pulse), 255, int(255 * pulse))
        
        # Main cross
        cv2.line(frame, (x - size, y), (x + size, y), color, 2)
        cv2.line(frame, (x, y - size), (x, y + size), color, 2)
        
        # Corner brackets
        bracket_size = size // 3
        cv2.line(frame, (x - size, y - size), (x - size + bracket_size, y - size), color, 2)
        cv2.line(frame, (x - size, y - size), (x - size, y - size + bracket_size), color, 2)
        
        cv2.line(frame, (x + size, y - size), (x + size - bracket_size, y - size), color, 2)
        cv2.line(frame, (x + size, y - size), (x + size, y - size + bracket_size), color, 2)
        
        cv2.line(frame, (x - size, y + size), (x - size + bracket_size, y + size), color, 2)
        cv2.line(frame, (x - size, y + size), (x - size, y + size - bracket_size), color, 2)
        
        cv2.line(frame, (x + size, y + size), (x + size - bracket_size, y + size), color, 2)
        cv2.line(frame, (x + size, y + size), (x + size, y + size - bracket_size), color, 2)
        
        # Center dot
        cv2.circle(frame, (x, y), 3, color, -1)
    
    def draw_face_ar_overlay(self, frame, face_landmarks):
        """Draw face AR overlay exactly like reference images"""
        if not face_landmarks:
            return
        
        height, width = frame.shape[:2]
        
        # Get face bounding box
        face_points = []
        for landmark in face_landmarks[0].landmark:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            face_points.append((x, y))
        
        if not face_points:
            return
        
        # Calculate face center and bounds
        min_x = min([p[0] for p in face_points])
        max_x = max([p[0] for p in face_points])
        min_y = min([p[1] for p in face_points])
        max_y = max([p[1] for p in face_points])
        
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        
        # Main face rectangle frames (cyan like in reference)
        padding = 20
        cv2.rectangle(frame, (min_x - padding, min_y - padding), 
                     (max_x + padding, max_y + padding), self.cyan, 2)
        
        # Inner frame
        inner_padding = 10
        cv2.rectangle(frame, (min_x - inner_padding, min_y - inner_padding), 
                     (max_x + inner_padding, max_y + inner_padding), self.cyan, 1)
        
        # Side rectangles (like in reference images)
        side_width = 80
        side_height = 40
        
        # Left side rectangles
        left_x = min_x - padding - side_width - 10
        cv2.rectangle(frame, (left_x, center_y - side_height), 
                     (left_x + side_width, center_y), self.cyan, 2)
        cv2.rectangle(frame, (left_x, center_y + 10), 
                     (left_x + side_width, center_y + side_height + 10), self.cyan, 2)
        
        # Right side rectangles  
        right_x = max_x + padding + 10
        cv2.rectangle(frame, (right_x, center_y - side_height), 
                     (right_x + side_width, center_y), self.cyan, 2)
        cv2.rectangle(frame, (right_x, center_y + 10), 
                     (right_x + side_width, center_y + side_height + 10), self.cyan, 2)
        
        # Circular elements (like the reference)
        cv2.circle(frame, (right_x + side_width//2, center_y - side_height//2), 15, self.cyan, 2)
        cv2.circle(frame, (right_x + side_width//2, center_y + side_height//2 + 10), 15, self.cyan, 2)
        
        # Add some inner details
        cv2.line(frame, (left_x + 10, center_y - 15), (left_x + side_width - 10, center_y - 15), self.cyan, 1)
        cv2.line(frame, (left_x + 10, center_y + 25), (left_x + side_width - 10, center_y + 25), self.cyan, 1)
        
        # Scanning lines effect
        scan_y = int(min_y + (time.time() * 80) % (max_y - min_y))
        cv2.line(frame, (min_x - padding, scan_y), (max_x + padding, scan_y), self.green, 1)
        
    def draw_scanning_effect(self, frame, face_landmarks):
        """Draw face scanning animation"""
        if not face_landmarks:
            return
        
        height, width = frame.shape[:2]
        
        # Get face bounding box
        face_points = []
        for landmark in face_landmarks[0].landmark:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            face_points.append((x, y))
        
        if not face_points:
            return
        
        # Calculate face center and bounds
        min_x = min([p[0] for p in face_points])
        max_x = max([p[0] for p in face_points])
        min_y = min([p[1] for p in face_points])
        max_y = max([p[1] for p in face_points])
        
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        
        # Animated scan lines
        scan_y = int(min_y + (time.time() * 100) % (max_y - min_y))
        cv2.line(frame, (min_x - 20, scan_y), (max_x + 20, scan_y), self.red, 2)
        
        # Face outline
        face_width = max_x - min_x
        face_height = max_y - min_y
        cv2.rectangle(frame, (min_x - 10, min_y - 10), (max_x + 10, max_y + 10), self.red, 2)
        
        # Crosshair on face center
        self.draw_crosshair(frame, (center_x, center_y), 30)
        
        # Scanning text
        cv2.putText(frame, "FACIAL RECOGNITION ACTIVE", 
                   (center_x - 100, min_y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.red, 2)
    
    def draw_circuit_overlay(self, frame, hand_landmarks):
        """Draw glowing circuit patterns around hands"""
        if not hand_landmarks:
            return
        
        height, width = frame.shape[:2]
        
        for hand in hand_landmarks:
            # Get hand center
            landmarks = []
            for landmark in hand.landmark:
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                landmarks.append((x, y))
            
            if len(landmarks) < 21:
                continue
            
            center_x = sum([p[0] for p in landmarks]) // len(landmarks)
            center_y = sum([p[1] for p in landmarks]) // len(landmarks)
            
            # Draw circuit patterns
            pulse = abs(math.sin(time.time() * 4)) * 0.5 + 0.5
            color = (int(255 * pulse), 255, int(255 * pulse))
            
            # Radiating lines
            for i in range(8):
                angle = i * (2 * math.pi / 8)
                end_x = int(center_x + 80 * math.cos(angle))
                end_y = int(center_y + 80 * math.sin(angle))
                cv2.line(frame, (center_x, center_y), (end_x, end_y), color, 2)
                
                # Circuit nodes
                node_x = int(center_x + 60 * math.cos(angle))
                node_y = int(center_y + 60 * math.sin(angle))
                cv2.circle(frame, (node_x, node_y), 5, color, -1)
            
            # Central hub
            cv2.circle(frame, (center_x, center_y), 15, color, 3)
            cv2.circle(frame, (center_x, center_y), 8, self.white, -1)
    
    def draw_system_info(self, frame):
        """Draw system information panel"""
        height, width = frame.shape[:2]
        
        # System panel background
        panel_x = width - 300
        panel_y = 50
        panel_width = 250
        panel_height = 200
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Panel border
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), self.cyan, 2)
        
        # Title
        cv2.putText(frame, "SYSTEM STATUS", (panel_x + 10, panel_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.cyan, 2)
        
        # Status lines
        status_lines = [
            "NEURAL LINK: ACTIVE",
            "BIOMETRIC SCAN: OK",
            f"TIMESTAMP: {int(time.time())}",
            "PROTOCOL: BORG-VII",
            "STATUS: OPERATIONAL"
        ]
        
        for i, line in enumerate(status_lines):
            y_pos = panel_y + 50 + (i * 25)
            cv2.putText(frame, line, (panel_x + 10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.green, 1)
    
    def draw_complete_hud(self, frame, face_landmarks, hand_landmarks, pose_landmarks, cyborg_evolution, borg_level, gesture, face_detected, scanning_active):
        """Draw the complete HUD overlay"""
        height, width = frame.shape[:2]
        
        # Skeleton arm wireframe that follows your real arm movement
        self.draw_skeleton_arm(frame, pose_landmarks)
        
        # Neural network (left side, below skeleton arm)
        self.draw_neural_network(frame, x_offset=50, y_offset=350)
        
        # Face AR overlay (always show when face detected)
        if face_landmarks:
            self.draw_face_ar_overlay(frame, face_landmarks)
        
        # Progress bars (right side, matching reference images)
        self.draw_progress_bar(frame, width - 350, height - 150, 300, 20, cyborg_evolution, "cyborg evolution", self.orange)
        self.draw_progress_bar(frame, width - 350, height - 100, 300, 20, borg_level * 10, "borg evolution level", self.orange)
        
        # System info panel
        self.draw_system_info(frame)
        
        # Face scanning effects (only when pinching)
        if scanning_active and face_landmarks:
            self.draw_scanning_effect(frame, face_landmarks)
        
        # Circuit overlays for open palm gesture
        if gesture == "open_palm":
            self.draw_circuit_overlay(frame, hand_landmarks)
        
        # Corner crosshairs (like in reference)
        corner_size = 20
        corners = [
            (corner_size, corner_size),
            (width - corner_size, corner_size),
            (corner_size, height - corner_size),
            (width - corner_size, height - corner_size)
        ]
        
        for corner in corners:
            # Draw + style crosshairs
            cv2.line(frame, (corner[0] - 15, corner[1]), (corner[0] + 15, corner[1]), self.cyan, 2)
            cv2.line(frame, (corner[0], corner[1] - 15), (corner[0], corner[1] + 15), self.cyan, 2)
        
        # Current gesture display
        cv2.putText(frame, f"GESTURE: {gesture.upper()}", (50, height - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.cyan, 2)
        
        # Face detection status
        status_color = self.green if face_detected else self.red
        status_text = "FACE DETECTED" if face_detected else "NO FACE"
        cv2.putText(frame, f"BIOMETRIC: {status_text}", (50, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # Show pose tracking status
        pose_status = "POSE TRACKED" if pose_landmarks else "NO POSE"
        pose_color = self.green if pose_landmarks else self.red
        cv2.putText(frame, f"ARM TRACKING: {pose_status}", (width - 250, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, pose_color, 2)
        
        self.frame_count += 1
        return frame