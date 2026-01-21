import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from collections import deque
from typing import Optional, Tuple, List
import time


class HandTracker:
    """
    Advanced AI-based hand tracking with gesture recognition capabilities.
    Optimized for accuracy, smoothness, and performance.
    """
    
    def __init__(self, model_path: str = "hand_landmarker.task"):
        # --- MediaPipe model configuration ---
        base_options = python.BaseOptions(model_asset_path=model_path)
        
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.65,  # Slightly higher for stability
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.65,
            running_mode=vision.RunningMode.IMAGE
        )
        
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # --- Multi-stage smoothing system ---
        self.prev_landmarks = None
        self.smooth_factor = 0.65  # Primary smoothing (0.6-0.7 optimal)
        
        # Exponential moving average for critical landmarks
        self.ema_alpha = 0.3  # For fingertips (more responsive)
        self.ema_landmarks = {}
        
        # Kalman-like prediction buffer for ultra-smooth tracking
        self.landmark_history = deque(maxlen=5)
        
        # --- Performance tracking ---
        self.last_detection_time = 0
        self.fps_counter = deque(maxlen=30)
        
        # --- Gesture detection state ---
        self.gesture_cooldown = 0
        self.last_gesture = None
        self.gesture_threshold_frames = 3
        self.gesture_confirmation_buffer = deque(maxlen=self.gesture_threshold_frames)
        
        # --- Frame preprocessing optimization ---
        self.target_width = 640  # Resize for faster processing
        self.use_gpu = self._check_gpu_available()
        
    def _check_gpu_available(self) -> bool:
        """Check if GPU acceleration is available"""
        try:
            return cv2.cuda.getCudaEnabledDeviceCount() > 0
        except:
            return False
    
    def _preprocess_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Optimize frame for faster processing while maintaining quality
        Returns: (processed_frame, scale_factor)
        """
        h, w = frame.shape[:2]
        
        # Resize if frame is too large (maintains aspect ratio)
        if w > self.target_width:
            scale = self.target_width / w
            new_w = self.target_width
            new_h = int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        else:
            scale = 1.0
        
        return frame, scale
    
    def _apply_exponential_smoothing(self, landmarks: List[Tuple[float, float]], 
                                    indices: List[int]) -> List[Tuple[float, float]]:
        """Apply EMA to specific landmark indices (e.g., fingertips)"""
        smoothed = landmarks.copy()
        
        for idx in indices:
            if idx < len(landmarks):
                x, y = landmarks[idx]
                
                if idx in self.ema_landmarks:
                    prev_x, prev_y = self.ema_landmarks[idx]
                    x = prev_x + self.ema_alpha * (x - prev_x)
                    y = prev_y + self.ema_alpha * (y - prev_y)
                
                self.ema_landmarks[idx] = (x, y)
                smoothed[idx] = (x, y)
        
        return smoothed
    
    def _adaptive_smoothing(self, raw: List[Tuple[float, float]], 
                           prev: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Adaptive smoothing based on motion speed
        Fast motion = less smoothing (responsive)
        Slow motion = more smoothing (stable)
        """
        smoothed = []
        
        for (x, y), (px, py) in zip(raw, prev):
            # Calculate motion magnitude
            motion = np.sqrt((x - px)**2 + (y - py)**2)
            
            # Adaptive factor: more smoothing when motion is small
            adaptive_factor = self.smooth_factor
            if motion < 5:  # Small motion - increase smoothing
                adaptive_factor = min(0.8, self.smooth_factor + 0.15)
            elif motion > 30:  # Large motion - reduce smoothing
                adaptive_factor = max(0.4, self.smooth_factor - 0.2)
            
            sx = px + (x - px) * adaptive_factor
            sy = py + (y - py) * adaptive_factor
            smoothed.append((sx, sy))
        
        return smoothed
    
    def _predict_next_position(self, current: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Predict next landmark positions using velocity estimation
        Reduces perceived latency
        """
        if len(self.landmark_history) < 2:
            return current
        
        predicted = []
        prev_frame = self.landmark_history[-1]
        
        for (x, y), (px, py) in zip(current, prev_frame):
            # Simple velocity-based prediction
            vx = x - px
            vy = y - py
            
            # Predict next position (with dampening)
            pred_x = x + vx * 0.3
            pred_y = y + vy * 0.3
            
            predicted.append((pred_x, pred_y))
        
        return predicted
    
    def find_hand_landmarks(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
        """
        Detect and return smoothed hand landmarks with maximum optimization
        
        Returns:
            frame: Original frame (unmodified)
            landmarks: List of (x, y) tuples for 21 hand landmarks
        """
        start_time = time.time()
        
        # Preprocess frame for optimal performance
        processed_frame, scale_factor = self._preprocess_frame(frame)
        
        # Convert to RGB for MediaPipe
        rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        # Detect hand landmarks
        result = self.detector.detect(mp_image)
        
        landmarks = []
        
        if result.hand_landmarks:
            h, w = processed_frame.shape[:2]
            original_h, original_w = frame.shape[:2]
            
            # Extract raw landmarks (scale back to original resolution)
            raw_landmarks = [
                (lm.x * original_w, lm.y * original_h)
                for lm in result.hand_landmarks[0]
            ]
            
            # Multi-stage smoothing pipeline
            if self.prev_landmarks is None:
                # First detection - no smoothing
                smoothed = raw_landmarks
            else:
                # Stage 1: Adaptive temporal smoothing
                smoothed = self._adaptive_smoothing(raw_landmarks, self.prev_landmarks)
                
                # Stage 2: Apply EMA to fingertips (indices 4, 8, 12, 16, 20)
                smoothed = self._apply_exponential_smoothing(
                    smoothed, 
                    [4, 8, 12, 16, 20]  # Thumb tip, index tip, etc.
                )
                
                # Stage 3: Predictive smoothing for reduced latency
                if len(self.landmark_history) >= 2:
                    smoothed = self._predict_next_position(smoothed)
            
            # Update history
            self.prev_landmarks = smoothed
            self.landmark_history.append(smoothed)
            
            # Convert to integers for output
            landmarks = [(int(x), int(y)) for x, y in smoothed]
            
        else:
            # No hand detected - reset state
            self.prev_landmarks = None
            self.ema_landmarks.clear()
            self.landmark_history.clear()
        
        # Performance tracking
        processing_time = time.time() - start_time
        self.fps_counter.append(1.0 / processing_time if processing_time > 0 else 0)
        
        return frame, landmarks
    
    def detect_gesture(self, landmarks: List[Tuple[int, int]]) -> Optional[str]:
        """
        Detect specific hand gestures from landmarks
        Returns gesture name or None with temporal filtering for stability
        """
        if not landmarks or len(landmarks) < 21:
            self.gesture_confirmation_buffer.clear()
            return None
        
        # Cooldown management
        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= 1
            return self.last_gesture
        
        gesture = self._identify_gesture(landmarks)
        
        # Temporal filtering: require consistent detection
        self.gesture_confirmation_buffer.append(gesture)
        
        if len(self.gesture_confirmation_buffer) == self.gesture_threshold_frames:
            # Check if gesture is consistent across buffer
            if all(g == gesture for g in self.gesture_confirmation_buffer):
                self.last_gesture = gesture
                self.gesture_cooldown = 10  # Prevent rapid re-triggering
                return gesture
        
        return None
    
    def _identify_gesture(self, landmarks: List[Tuple[int, int]]) -> Optional[str]:
        """Identify specific gestures from landmark positions"""
        
        # Extract key landmarks
        thumb_tip = np.array(landmarks[4])
        index_tip = np.array(landmarks[8])
        middle_tip = np.array(landmarks[12])
        ring_tip = np.array(landmarks[16])
        pinky_tip = np.array(landmarks[20])
        
        wrist = np.array(landmarks[0])
        index_mcp = np.array(landmarks[5])  # Index finger base
        
        # Calculate distances
        thumb_index_dist = np.linalg.norm(thumb_tip - index_tip)
        palm_size = np.linalg.norm(index_mcp - wrist)
        
        # Gesture 1: PINCH (thumb and index close)
        if thumb_index_dist < palm_size * 0.3:
            return "PINCH"
        
        # Gesture 2: OPEN_PALM (all fingers extended)
        finger_tips = [index_tip, middle_tip, ring_tip, pinky_tip]
        all_extended = all(tip[1] < wrist[1] - palm_size * 0.3 for tip in finger_tips)
        
        if all_extended and thumb_tip[0] > wrist[0]:
            return "OPEN_PALM"
        
        # Gesture 3: POINTING (only index extended)
        index_extended = index_tip[1] < index_mcp[1] - palm_size * 0.4
        others_folded = all(
            tip[1] > wrist[1] - palm_size * 0.1 
            for tip in [middle_tip, ring_tip, pinky_tip]
        )
        
        if index_extended and others_folded:
            return "POINTING"
        
        # Gesture 4: FIST (all fingers closed)
        all_folded = all(
            tip[1] > wrist[1] - palm_size * 0.1 
            for tip in finger_tips
        )
        
        if all_folded:
            return "FIST"
        
        return None
    
    def get_fingertip_position(self, landmarks: List[Tuple[int, int]], 
                               finger: str = "index") -> Optional[Tuple[int, int]]:
        """
        Get position of specific fingertip
        finger: "thumb"=4, "index"=8, "middle"=12, "ring"=16, "pinky"=20
        """
        if not landmarks:
            return None
        
        finger_map = {
            "thumb": 4, "index": 8, "middle": 12, 
            "ring": 16, "pinky": 20
        }
        
        idx = finger_map.get(finger.lower(), 8)
        return landmarks[idx] if idx < len(landmarks) else None
    
    def get_fps(self) -> float:
        """Get current processing FPS"""
        return np.mean(self.fps_counter) if self.fps_counter else 0.0
    
    def draw_landmarks(self, frame: np.ndarray, 
                      landmarks: List[Tuple[int, int]],
                      show_connections: bool = True) -> np.ndarray:
        """
        Draw hand landmarks and connections on frame for visualization
        """
        if not landmarks:
            return frame
        
        # Draw connections first (underneath)
        if show_connections:
            connections = [
                # Thumb
                (0, 1), (1, 2), (2, 3), (3, 4),
                # Index
                (0, 5), (5, 6), (6, 7), (7, 8),
                # Middle
                (0, 9), (9, 10), (10, 11), (11, 12),
                # Ring
                (0, 13), (13, 14), (14, 15), (15, 16),
                # Pinky
                (0, 17), (17, 18), (18, 19), (19, 20),
                # Palm
                (5, 9), (9, 13), (13, 17)
            ]
            
            for start, end in connections:
                if start < len(landmarks) and end < len(landmarks):
                    cv2.line(frame, landmarks[start], landmarks[end], 
                            (0, 255, 0), 2, cv2.LINE_AA)
        
        # Draw landmarks on top
        for i, (x, y) in enumerate(landmarks):
            # Fingertips in red, others in blue
            color = (0, 0, 255) if i in [4, 8, 12, 16, 20] else (255, 0, 0)
            cv2.circle(frame, (x, y), 5, color, -1, cv2.LINE_AA)
            cv2.circle(frame, (x, y), 6, (255, 255, 255), 1, cv2.LINE_AA)
        
        return frame
    
    def reset(self):
        """Reset all tracking state"""
        self.prev_landmarks = None
        self.ema_landmarks.clear()
        self.landmark_history.clear()
        self.gesture_confirmation_buffer.clear()
        self.gesture_cooldown = 0
        self.last_gesture = None
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'detector'):
            self.detector.close()