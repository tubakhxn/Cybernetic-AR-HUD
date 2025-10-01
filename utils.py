import time
import cv2
import numpy as np

class FPSCounter:
    def __init__(self, buffer_size=30):
        self.buffer_size = buffer_size
        self.frame_times = []
        self.last_time = time.time()
    
    def update(self):
        """Update the FPS counter with current time"""
        current_time = time.time()
        self.frame_times.append(current_time - self.last_time)
        self.last_time = current_time
        
        # Keep only recent frames
        if len(self.frame_times) > self.buffer_size:
            self.frame_times.pop(0)
    
    def get_fps(self):
        """Calculate and return current FPS"""
        if len(self.frame_times) < 2:
            return 0.0
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        if avg_frame_time == 0:
            return 0.0
        
        return 1.0 / avg_frame_time

class PerformanceMonitor:
    def __init__(self):
        self.process_times = {}
        self.start_times = {}
    
    def start_timer(self, process_name):
        """Start timing a process"""
        self.start_times[process_name] = time.time()
    
    def end_timer(self, process_name):
        """End timing a process and store the duration"""
        if process_name in self.start_times:
            duration = time.time() - self.start_times[process_name]
            if process_name not in self.process_times:
                self.process_times[process_name] = []
            
            self.process_times[process_name].append(duration)
            
            # Keep only recent measurements
            if len(self.process_times[process_name]) > 30:
                self.process_times[process_name].pop(0)
    
    def get_average_time(self, process_name):
        """Get average processing time for a process"""
        if process_name not in self.process_times or not self.process_times[process_name]:
            return 0.0
        
        return sum(self.process_times[process_name]) / len(self.process_times[process_name])
    
    def get_performance_info(self):
        """Get performance information for all tracked processes"""
        info = {}
        for process_name in self.process_times:
            info[process_name] = {
                'avg_time': self.get_average_time(process_name),
                'fps': 1.0 / self.get_average_time(process_name) if self.get_average_time(process_name) > 0 else 0
            }
        return info

def normalize_coordinates(landmarks, frame_width, frame_height):
    """Convert normalized coordinates to pixel coordinates"""
    pixel_coords = []
    for landmark in landmarks:
        x = int(landmark.x * frame_width)
        y = int(landmark.y * frame_height)
        pixel_coords.append((x, y))
    return pixel_coords

def calculate_angle(point1, point2, point3):
    """Calculate angle between three points"""
    # Vector from point2 to point1
    v1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
    # Vector from point2 to point3  
    v2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
    
    # Calculate angle using dot product
    cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    angle = np.arccos(np.clip(cosine, -1.0, 1.0))
    
    return np.degrees(angle)

def smooth_value(current_value, target_value, smoothing_factor=0.8):
    """Smooth transitions between values"""
    return current_value * smoothing_factor + target_value * (1 - smoothing_factor)

def interpolate_color(color1, color2, factor):
    """Interpolate between two colors"""
    return tuple(int(c1 * (1 - factor) + c2 * factor) for c1, c2 in zip(color1, color2))

def create_glow_effect(frame, points, color, radius=20):
    """Create a glowing effect around points"""
    overlay = frame.copy()
    
    for point in points:
        # Create multiple circles with decreasing opacity for glow effect
        for i in range(radius, 0, -2):
            alpha = (radius - i) / radius * 0.3
            glow_color = tuple(int(c * alpha) for c in color)
            cv2.circle(overlay, point, i, glow_color, -1)
    
    # Blend with original frame
    cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
    return frame

def draw_animated_text(frame, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, 
                      font_scale=1, color=(255, 255, 255), thickness=2, 
                      animation_type="pulse"):
    """Draw animated text with various effects"""
    if animation_type == "pulse":
        pulse = abs(np.sin(time.time() * 3)) * 0.3 + 0.7
        current_scale = font_scale * pulse
        cv2.putText(frame, text, position, font, current_scale, color, thickness)
    
    elif animation_type == "glow":
        # Create glow effect
        for offset in range(5, 0, -1):
            alpha = (5 - offset) / 5 * 0.5
            glow_color = tuple(int(c * alpha) for c in color)
            cv2.putText(frame, text, position, font, font_scale, glow_color, thickness + offset)
        
        # Main text
        cv2.putText(frame, text, position, font, font_scale, color, thickness)
    
    else:
        # Default static text
        cv2.putText(frame, text, position, font, font_scale, color, thickness)

def get_system_info():
    """Get basic system information"""
    return {
        'timestamp': int(time.time()),
        'uptime': time.time(),
        'frame_count': 0
    }

class ConfigManager:
    """Manage application configuration"""
    def __init__(self):
        self.config = {
            'detection_confidence': 0.5,
            'tracking_confidence': 0.5,
            'max_faces': 1,
            'max_hands': 2,
            'show_fps': True,
            'show_confidence': True,
            'animation_speed': 1.0,
            'colors': {
                'cyan': (255, 255, 0),
                'green': (0, 255, 0),
                'red': (0, 0, 255),
                'orange': (0, 165, 255),
                'white': (255, 255, 255)
            }
        }
    
    def get(self, key, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value