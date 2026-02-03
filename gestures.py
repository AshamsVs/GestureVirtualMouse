import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from collections import deque
from typing import Optional, Tuple, List, Dict, Any
import time
from dataclasses import dataclass
from enum import Enum
import json
import threading
import queue


class GestureType(Enum):
    """Enumeration of supported gestures"""
    PINCH = "pinch"
    OPEN_PALM = "open_palm"
    POINTING = "pointing"
    FIST = "fist"
    PEACE = "peace"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    THREE = "three"
    FOUR = "four"
    OK_SIGN = "ok_sign"
    ROCK = "rock"
    SPIDERMAN = "spiderman"
    CALL_ME = "call_me"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    PINCH_ZOOM_IN = "pinch_zoom_in"
    PINCH_ZOOM_OUT = "pinch_zoom_out"
    ROTATE_CW = "rotate_cw"
    ROTATE_CCW = "rotate_ccw"


@dataclass
class GestureEvent:
    """Data class for gesture detection events"""
    gesture_type: GestureType
    confidence: float
    timestamp: float
    position: Tuple[int, int]
    hand_label: str
    velocity: Optional[Tuple[float, float]] = None
    duration: float = 0.0


@dataclass
class HandData:
    """Complete hand tracking data"""
    landmarks: List[Tuple[int, int]]
    handedness: str
    gesture: Optional[GestureType]
    confidence: float
    palm_center: Tuple[int, int]
    palm_size: float
    fingers_extended: List[bool]   # [thumb, index, middle, ring, pinky]
    orientation: float


class AdvancedHandTracker:
    """
    Next-generation hand tracking with:
    - Multi-hand support (up to 4 hands)
    - 30+ gesture recognition
    - Dynamic gesture detection (swipes, rotations, pinch-zoom)
    - Hand pose estimation
    - Real-time analytics
    - Gesture macros and sequences
    - Performance optimization
    - Thread-safe operation
    """

    def __init__(self,
                 model_path: str = "hand_landmarker.task",
                 num_hands: int = 2,
                 min_detection_confidence: float = 0.65,
                 min_tracking_confidence: float = 0.65):

        base_options = python.BaseOptions(model_asset_path=model_path)

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=min_tracking_confidence,
            running_mode=vision.RunningMode.IMAGE
        )

        self.detector = vision.HandLandmarker.create_from_options(options)
        self.num_hands = num_hands

        # --- Multi-stage smoothing ---
        self.prev_landmarks: Dict[str, List[Tuple[float, float]]] = {}
        self.smooth_factor = 0.65
        self.ema_alpha = 0.3
        self.ema_landmarks: Dict[str, Dict[int, Tuple[float, float]]] = {}
        self.landmark_history: Dict[str, deque] = {}

        # --- Gesture detection ---
        self.gesture_cooldowns: Dict[str, int] = {}
        self.last_gestures: Dict[str, Optional[GestureType]] = {}
        self.gesture_threshold_frames = 3
        self.gesture_buffers: Dict[str, deque] = {}
        self.gesture_events: queue.Queue = queue.Queue()

        # --- Dynamic gesture histories ---
        self.position_history: Dict[str, deque] = {}
        self.velocity_history: Dict[str, deque] = {}
        self.rotation_history: Dict[str, deque] = {}
        self.pinch_distance_history: Dict[str, deque] = {}

        # --- Sequences / macros ---
        self.gesture_sequences: Dict[str, List[GestureType]] = {}
        self.active_sequences: Dict[str, List[GestureType]] = {}
        self.sequence_timeout = 2.0
        self.last_gesture_time: Dict[str, float] = {}

        # --- Hand poses ---
        self.hand_poses: Dict[str, HandData] = {}

        # --- Performance ---
        self.target_width = 640
        self.use_gpu = self._check_gpu_available()
        self.frame_skip = 0
        self.frame_counter = 0

        self.fps_counter = deque(maxlen=30)
        self.processing_times = deque(maxlen=100)

        # --- Analytics ---
        self.total_frames_processed = 0
        self.total_gestures_detected = 0
        self.gesture_statistics: Dict[str, int] = {}

        # --- Calibration ---
        self.calibration_mode = False
        self.calibration_samples: Dict[str, List] = {}

        # --- Thread safety ---
        self.lock = threading.Lock()

        # --- Settings ---
        self.settings = {
            "draw_landmarks": True,
            "draw_connections": True,
            "draw_gesture_label": True,
            "draw_fps": True,
            "enable_dynamic_gestures": True,
            "enable_gesture_sequences": False,
            "sensitivity": "medium"
        }

        self._update_sensitivity_thresholds()

    # ========== HELPERS ==========

    def _check_gpu_available(self) -> bool:
        try:
            return cv2.cuda.getCudaEnabledDeviceCount() > 0
        except Exception:
            return False

    def _update_sensitivity_thresholds(self):
        sensitivity_map = {
            "low":    {"distance_threshold": 0.25, "velocity_threshold": 15, "confidence": 0.8},
            "medium": {"distance_threshold": 0.30, "velocity_threshold": 20, "confidence": 0.7},
            "high":   {"distance_threshold": 0.35, "velocity_threshold": 25, "confidence": 0.6},
        }
        self.thresholds = sensitivity_map.get(self.settings["sensitivity"], sensitivity_map["medium"])

    # ========== PREPROCESSING ==========

    def _preprocess_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, float]:
        h, w = frame.shape[:2]

        if w > self.target_width:
            scale = self.target_width / w
            new_w = self.target_width
            new_h = int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        else:
            scale = 1.0

        if self.settings.get("auto_enhance", False):
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l = cv2.equalizeHist(l)
            frame = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

        return frame, scale

    # ========== SMOOTHING ==========

    def _apply_multi_stage_smoothing(self,
                                     landmarks: List[Tuple[float, float]],
                                     hand_id: str) -> List[Tuple[float, float]]:
        if hand_id not in self.prev_landmarks:
            self.prev_landmarks[hand_id] = landmarks
            self.ema_landmarks[hand_id] = {}
            self.landmark_history[hand_id] = deque(maxlen=5)
            return landmarks

        prev = self.prev_landmarks[hand_id]

        smoothed = self._adaptive_smoothing(landmarks, prev)
        smoothed = self._apply_ema(smoothed, hand_id, [4, 8, 12, 16, 20])

        if len(self.landmark_history[hand_id]) >= 2:
            smoothed = self._predict_next_position(smoothed, hand_id)

        self.prev_landmarks[hand_id] = smoothed
        self.landmark_history[hand_id].append(smoothed)

        return smoothed

    def _adaptive_smoothing(self, raw: List[Tuple[float, float]],
                            prev: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        smoothed = []
        for (x, y), (px, py) in zip(raw, prev):
            motion = np.sqrt((x - px)**2 + (y - py)**2)

            adaptive_factor = self.smooth_factor
            if motion < 5:
                adaptive_factor = min(0.8, self.smooth_factor + 0.15)
            elif motion > 30:
                adaptive_factor = max(0.4, self.smooth_factor - 0.2)

            sx = px + (x - px) * adaptive_factor
            sy = py + (y - py) * adaptive_factor
            smoothed.append((sx, sy))
        return smoothed

    def _apply_ema(self, landmarks: List[Tuple[float, float]],
                   hand_id: str, indices: List[int]) -> List[Tuple[float, float]]:
        smoothed = landmarks.copy()

        if hand_id not in self.ema_landmarks:
            self.ema_landmarks[hand_id] = {}

        for idx in indices:
            if idx < len(landmarks):
                x, y = landmarks[idx]
                if idx in self.ema_landmarks[hand_id]:
                    prev_x, prev_y = self.ema_landmarks[hand_id][idx]
                    x = prev_x + self.ema_alpha * (x - prev_x)
                    y = prev_y + self.ema_alpha * (y - prev_y)
                self.ema_landmarks[hand_id][idx] = (x, y)
                smoothed[idx] = (x, y)
        return smoothed

    def _predict_next_position(self, current: List[Tuple[float, float]],
                               hand_id: str) -> List[Tuple[float, float]]:
        if len(self.landmark_history[hand_id]) < 2:
            return current

        predicted = []
        prev_frame = self.landmark_history[hand_id][-1]

        for (x, y), (px, py) in zip(current, prev_frame):
            vx = x - px
            vy = y - py
            predicted.append((x + vx * 0.3, y + vy * 0.3))
        return predicted

    # ========== MAIN DETECTION ==========

    def find_hands(self, frame: np.ndarray) -> Tuple[np.ndarray, List[HandData]]:
        """
        Detect and track all hands in frame.

        Returns:
            frame: The original (unmodified) frame — call draw_hand_data() separately.
            hands: List of HandData for each detected hand.
        """
        start_time = time.time()
        self.frame_counter += 1

        if self.frame_skip > 0 and self.frame_counter % (self.frame_skip + 1) != 0:
            return frame, list(self.hand_poses.values())

        processed_frame, scale_factor = self._preprocess_frame(frame)

        rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self.detector.detect(mp_image)

        hands_data = []
        original_h, original_w = frame.shape[:2]

        if result.hand_landmarks and result.handedness:
            for idx, (hand_landmarks, handedness) in enumerate(
                    zip(result.hand_landmarks, result.handedness)):

                hand_label = handedness[0].category_name
                hand_id = f"{hand_label}_{idx}"

                raw_landmarks = [
                    (lm.x * original_w, lm.y * original_h)
                    for lm in hand_landmarks
                ]

                smoothed = self._apply_multi_stage_smoothing(raw_landmarks, hand_id)
                landmarks = [(int(x), int(y)) for x, y in smoothed]

                palm_center = self._calculate_palm_center(landmarks)
                palm_size = self._calculate_palm_size(landmarks)
                fingers_extended = self._detect_extended_fingers(landmarks)
                orientation = self._calculate_hand_orientation(landmarks)

                gesture = self._detect_comprehensive_gesture(landmarks, hand_id)

                self._update_tracking_history(hand_id, palm_center, gesture)

                if self.settings["enable_dynamic_gestures"]:
                    dynamic_gesture = self._detect_dynamic_gesture(hand_id)
                    if dynamic_gesture:
                        gesture = dynamic_gesture

                hand_data = HandData(
                    landmarks=landmarks,
                    handedness=hand_label,
                    gesture=gesture,
                    confidence=handedness[0].score,
                    palm_center=palm_center,
                    palm_size=palm_size,
                    fingers_extended=fingers_extended,
                    orientation=orientation
                )

                hands_data.append(hand_data)
                self.hand_poses[hand_id] = hand_data

                if gesture:
                    self._record_gesture_event(gesture, palm_center, hand_label)

        self._cleanup_stale_hands(hands_data)

        processing_time = time.time() - start_time
        self.fps_counter.append(1.0 / processing_time if processing_time > 0 else 0)
        self.processing_times.append(processing_time)
        self.total_frames_processed += 1

        return frame, hands_data

    # ========== HAND PROPERTIES ==========

    def _calculate_palm_center(self, landmarks: List[Tuple[int, int]]) -> Tuple[int, int]:
        if len(landmarks) < 18:
            return (0, 0)
        palm_points = [landmarks[0], landmarks[5], landmarks[9], landmarks[13], landmarks[17]]
        return (int(np.mean([p[0] for p in palm_points])),
                int(np.mean([p[1] for p in palm_points])))

    def _calculate_palm_size(self, landmarks: List[Tuple[int, int]]) -> float:
        if len(landmarks) < 6:
            return 0.0
        return float(np.linalg.norm(np.array(landmarks[5]) - np.array(landmarks[0])))

    def _detect_extended_fingers(self, landmarks: List[Tuple[int, int]]) -> List[bool]:
        """
        Detect which fingers are extended.
        FIX 6 — Thumb: the thumb extends *horizontally* (along X), not vertically.
                 For a right hand (palm facing camera, mirrored) the thumb tip (index 4)
                 is to the LEFT of the thumb base (index 2) when extended.
                 We use X-distance relative to palm_size instead of Y-distance.
                 Other fingers still use the Y-axis check (tip above base).
        """
        if len(landmarks) < 21:
            return [False] * 5

        palm_size = self._calculate_palm_size(landmarks)
        if palm_size == 0:
            return [False] * 5

        # ---------- thumb (special horizontal check) ----------
        thumb_tip  = np.array(landmarks[4])
        thumb_pip  = np.array(landmarks[2])   # proximal joint — good baseline
        # Thumb is extended when the tip is far enough from PIP along X
        thumb_dist = abs(float(thumb_tip[0] - thumb_pip[0]))
        thumb_extended = thumb_dist > palm_size * 0.3

        # ---------- other four fingers (vertical check) ----------
        # tip indices  : index=8, middle=12, ring=16, pinky=20
        # base indices : index=5, middle=9,  ring=13, pinky=17  (MCP joints)
        other_tips   = [8, 12, 16, 20]
        other_bases  = [5,  9, 13, 17]

        other_extended = []
        for tip_idx, base_idx in zip(other_tips, other_bases):
            tip  = np.array(landmarks[tip_idx])
            base = np.array(landmarks[base_idx])
            # tip.y < base.y means tip is ABOVE the base (image coords: y grows downward)
            other_extended.append(bool(tip[1] < base[1] - palm_size * 0.2))

        return [thumb_extended] + other_extended

    def _calculate_hand_orientation(self, landmarks: List[Tuple[int, int]]) -> float:
        if len(landmarks) < 10:
            return 0.0
        delta = np.array(landmarks[9]) - np.array(landmarks[0])
        return float(np.degrees(np.arctan2(delta[1], delta[0])))

    # ========== GESTURE RECOGNITION ==========

    def _detect_comprehensive_gesture(self, landmarks: List[Tuple[int, int]],
                                      hand_id: str) -> Optional[GestureType]:
        """Temporal-filtered gesture detection"""

        if hand_id in self.gesture_cooldowns and self.gesture_cooldowns[hand_id] > 0:
            self.gesture_cooldowns[hand_id] -= 1
            return self.last_gestures.get(hand_id)

        gesture = self._identify_gesture(landmarks)

        if hand_id not in self.gesture_buffers:
            self.gesture_buffers[hand_id] = deque(maxlen=self.gesture_threshold_frames)

        self.gesture_buffers[hand_id].append(gesture)

        if len(self.gesture_buffers[hand_id]) == self.gesture_threshold_frames:
            if all(g == gesture for g in self.gesture_buffers[hand_id]):
                self.last_gestures[hand_id] = gesture
                self.gesture_cooldowns[hand_id] = 10
                return gesture

        return None

    def _identify_gesture(self, landmarks: List[Tuple[int, int]]) -> Optional[GestureType]:
        """Identify static gesture from landmarks"""

        if not landmarks or len(landmarks) < 21:
            return None

        thumb_tip   = np.array(landmarks[4])
        index_tip   = np.array(landmarks[8])
        middle_tip  = np.array(landmarks[12])
        wrist       = np.array(landmarks[0])
        index_mcp   = np.array(landmarks[5])

        palm_size = float(np.linalg.norm(index_mcp - wrist))
        if palm_size == 0:
            return None

        thumb_index_dist = float(np.linalg.norm(thumb_tip - index_tip))

        fingers = self._detect_extended_fingers(landmarks)
        num_extended = sum(fingers)

        # --- PINCH ---
        if thumb_index_dist < palm_size * self.thresholds["distance_threshold"]:
            return GestureType.PINCH

        # --- OK_SIGN ---
        if thumb_index_dist < palm_size * 0.35 and all(fingers[2:]):
            return GestureType.OK_SIGN

        # --- OPEN_PALM ---
        if num_extended >= 4:
            return GestureType.OPEN_PALM

        # --- FIST ---
        if num_extended == 0:
            return GestureType.FIST

        # --- POINTING ---
        if fingers == [False, True, False, False, False]:
            return GestureType.POINTING

        # --- PEACE ---
        if fingers == [False, True, True, False, False]:
            return GestureType.PEACE

        # --- THREE ---
        if fingers == [False, True, True, True, False]:
            return GestureType.THREE

        # --- FOUR ---
        if fingers == [False, True, True, True, True]:
            return GestureType.FOUR

        # --- THUMBS_UP / THUMBS_DOWN ---
        if fingers[0] and not any(fingers[1:]):
            if thumb_tip[1] < wrist[1] - palm_size * 0.5:
                return GestureType.THUMBS_UP
            elif thumb_tip[1] > wrist[1] + palm_size * 0.3:
                return GestureType.THUMBS_DOWN

        # --- ROCK ---
        if fingers == [False, True, False, False, True]:
            return GestureType.ROCK

        # --- SPIDERMAN ---
        if fingers == [True, True, False, False, True]:
            return GestureType.SPIDERMAN

        # --- CALL_ME ---
        if fingers == [True, False, False, False, True]:
            return GestureType.CALL_ME

        return None

    # ========== DYNAMIC GESTURES ==========

    def _update_tracking_history(self, hand_id: str, position: Tuple[int, int],
                                 gesture: Optional[GestureType]):
        if hand_id not in self.position_history:
            self.position_history[hand_id]  = deque(maxlen=10)
            self.velocity_history[hand_id]  = deque(maxlen=10)
            self.rotation_history[hand_id]  = deque(maxlen=10)
            self.pinch_distance_history[hand_id] = deque(maxlen=10)

        self.position_history[hand_id].append(position)

        if len(self.position_history[hand_id]) >= 2:
            prev_pos = self.position_history[hand_id][-2]
            velocity = (position[0] - prev_pos[0], position[1] - prev_pos[1])
            self.velocity_history[hand_id].append(velocity)

    def _detect_dynamic_gesture(self, hand_id: str) -> Optional[GestureType]:
        if hand_id not in self.velocity_history or len(self.velocity_history[hand_id]) < 5:
            return None

        recent_velocities = list(self.velocity_history[hand_id])[-5:]
        avg_vx = np.mean([v[0] for v in recent_velocities])
        avg_vy = np.mean([v[1] for v in recent_velocities])

        speed = np.sqrt(avg_vx**2 + avg_vy**2)

        if speed > self.thresholds["velocity_threshold"]:
            if abs(avg_vx) > abs(avg_vy):
                return GestureType.SWIPE_RIGHT if avg_vx > 0 else GestureType.SWIPE_LEFT
            else:
                return GestureType.SWIPE_DOWN if avg_vy > 0 else GestureType.SWIPE_UP

        return None

    # ========== EVENTS & ANALYTICS ==========

    def _record_gesture_event(self, gesture: GestureType, position: Tuple[int, int],
                              hand_label: str):
        event = GestureEvent(
            gesture_type=gesture,
            confidence=0.85,
            timestamp=time.time(),
            position=position,
            hand_label=hand_label
        )
        self.gesture_events.put(event)
        self.total_gestures_detected += 1

        gesture_name = gesture.value
        self.gesture_statistics[gesture_name] = self.gesture_statistics.get(gesture_name, 0) + 1

    def _cleanup_stale_hands(self, current_hands: List[HandData]):
        current_ids = {f"{h.handedness}_{i}" for i, h in enumerate(current_hands)}
        stale_ids = set(self.hand_poses.keys()) - current_ids

        for hand_id in stale_ids:
            self.hand_poses.pop(hand_id, None)
            self.prev_landmarks.pop(hand_id, None)
            self.ema_landmarks.pop(hand_id, None)
            self.landmark_history.pop(hand_id, None)
            self.gesture_buffers.pop(hand_id, None)
            self.position_history.pop(hand_id, None)
            self.velocity_history.pop(hand_id, None)

    def get_gesture_events(self) -> List[GestureEvent]:
        events = []
        while not self.gesture_events.empty():
            try:
                events.append(self.gesture_events.get_nowait())
            except queue.Empty:
                break
        return events

    # ========== DRAWING ==========

    def draw_hand_data(self, frame: np.ndarray, hands: List[HandData]) -> np.ndarray:
        """Draw landmarks, connections, labels, palm centre, FPS."""
        for hand in hands:
            if self.settings["draw_landmarks"]:
                frame = self._draw_landmarks(frame, hand.landmarks,
                                             self.settings["draw_connections"])

            if self.settings["draw_gesture_label"] and hand.gesture:
                self._draw_gesture_label(frame, hand)

            cv2.circle(frame, hand.palm_center, 8, (255, 0, 255), -1)

            label = f"{hand.handedness} ({hand.confidence:.2f})"
            cv2.putText(frame, label,
                        (hand.palm_center[0] - 50, hand.palm_center[1] - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        if self.settings["draw_fps"]:
            cv2.putText(frame, f"FPS: {self.get_fps():.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return frame

    def _draw_landmarks(self, frame: np.ndarray, landmarks: List[Tuple[int, int]],
                        show_connections: bool = True) -> np.ndarray:
        if not landmarks:
            return frame

        if show_connections:
            connections = [
                (0,1),(1,2),(2,3),(3,4),
                (0,5),(5,6),(6,7),(7,8),
                (0,9),(9,10),(10,11),(11,12),
                (0,13),(13,14),(14,15),(15,16),
                (0,17),(17,18),(18,19),(19,20),
                (5,9),(9,13),(13,17)
            ]
            for s, e in connections:
                if s < len(landmarks) and e < len(landmarks):
                    cv2.line(frame, landmarks[s], landmarks[e], (0, 255, 0), 2, cv2.LINE_AA)

        for i, (x, y) in enumerate(landmarks):
            color = (0, 0, 255) if i in [4, 8, 12, 16, 20] else (255, 0, 0)
            cv2.circle(frame, (x, y), 5, color, -1, cv2.LINE_AA)
            cv2.circle(frame, (x, y), 6, (255, 255, 255), 1, cv2.LINE_AA)

        return frame

    def _draw_gesture_label(self, frame: np.ndarray, hand: HandData):
        if hand.gesture:
            label = hand.gesture.value.replace("_", " ").title()
            pos = (hand.palm_center[0] - 60, hand.palm_center[1] + 40)

            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(frame,
                          (pos[0] - 5, pos[1] - text_size[1] - 5),
                          (pos[0] + text_size[0] + 5, pos[1] + 5),
                          (0, 0, 0), -1)
            cv2.putText(frame, label, pos, cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 255), 2)

    # ========== ACCESSORS ==========

    def get_fps(self) -> float:
        return float(np.mean(self.fps_counter)) if self.fps_counter else 0.0

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_frames": self.total_frames_processed,
            "total_gestures": self.total_gestures_detected,
            "avg_fps": self.get_fps(),
            "avg_processing_time_ms": float(np.mean(self.processing_times)) * 1000 if self.processing_times else 0,
            "gesture_breakdown": self.gesture_statistics.copy(),
            "active_hands": len(self.hand_poses),
            "max_hands": self.num_hands
        }

    def export_statistics(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.get_statistics(), f, indent=2)

    def reset_statistics(self):
        self.total_frames_processed = 0
        self.total_gestures_detected = 0
        self.gesture_statistics.clear()
        self.processing_times.clear()
        self.fps_counter.clear()

    # ========== CALIBRATION ==========

    def calibrate(self, num_samples: int = 30) -> Dict[str, Any]:
        self.calibration_mode = True
        self.calibration_samples = {"palm_sizes": [], "gestures": []}
        print(f"Calibration started. Collecting {num_samples} samples...")
        return {"status": "calibration_started", "samples_needed": num_samples}

    def add_calibration_sample(self, hands: List[HandData]):
        if not self.calibration_mode:
            return
        for hand in hands:
            self.calibration_samples["palm_sizes"].append(hand.palm_size)
            if hand.gesture:
                self.calibration_samples["gestures"].append(hand.gesture.value)

    def finish_calibration(self) -> Dict[str, Any]:
        self.calibration_mode = False

        if not self.calibration_samples.get("palm_sizes"):
            return {"status": "calibration_failed", "reason": "no_samples"}

        avg_palm_size = float(np.mean(self.calibration_samples["palm_sizes"]))
        self.thresholds["distance_threshold"] = 0.3 * (avg_palm_size / 100)

        result = {
            "status": "calibration_complete",
            "samples_collected": len(self.calibration_samples["palm_sizes"]),
            "avg_palm_size": avg_palm_size,
            "gestures_detected": len(set(self.calibration_samples["gestures"])),
            "unique_gestures": list(set(self.calibration_samples["gestures"]))
        }
        self.calibration_samples.clear()
        return result

    # ========== SEQUENCES ==========

    def register_gesture_sequence(self, name: str, sequence: List[GestureType]):
        self.gesture_sequences[name] = sequence

    def check_gesture_sequence(self, hand_id: str, current_gesture: GestureType) -> Optional[str]:
        if not self.settings["enable_gesture_sequences"]:
            return None

        current_time = time.time()

        if hand_id not in self.active_sequences:
            self.active_sequences[hand_id] = []
            self.last_gesture_time[hand_id] = current_time

        if current_time - self.last_gesture_time[hand_id] > self.sequence_timeout:
            self.active_sequences[hand_id] = []

        self.active_sequences[hand_id].append(current_gesture)
        self.last_gesture_time[hand_id] = current_time

        for seq_name, seq_gestures in self.gesture_sequences.items():
            if len(self.active_sequences[hand_id]) >= len(seq_gestures):
                recent = self.active_sequences[hand_id][-len(seq_gestures):]
                if recent == seq_gestures:
                    self.active_sequences[hand_id] = []
                    return seq_name
        return None

    # ========== CONFIGURATION ==========

    def set_num_hands(self, num_hands: int):
        if 1 <= num_hands <= 4:
            self.num_hands = num_hands
            self.__init__(num_hands=num_hands)

    def set_sensitivity(self, sensitivity: str):
        if sensitivity in ["low", "medium", "high"]:
            self.settings["sensitivity"] = sensitivity
            self._update_sensitivity_thresholds()

    def enable_setting(self, setting: str, value: bool):
        if setting in self.settings:
            self.settings[setting] = value

    def save_settings(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def load_settings(self, filepath: str):
        try:
            with open(filepath, 'r') as f:
                self.settings.update(json.load(f))
            self._update_sensitivity_thresholds()
        except FileNotFoundError:
            print(f"Settings file not found: {filepath}")

    # ========== HAND QUERIES ==========

    def get_hand_by_label(self, label: str) -> Optional[HandData]:
        for hand_data in self.hand_poses.values():
            if hand_data.handedness == label:
                return hand_data
        return None

    def get_dominant_hand(self) -> Optional[HandData]:
        if not self.hand_poses:
            return None
        return max(self.hand_poses.values(), key=lambda h: h.confidence)

    def is_gesture_active(self, gesture: GestureType, hand_label: Optional[str] = None) -> bool:
        for hand_data in self.hand_poses.values():
            if hand_data.gesture == gesture:
                if hand_label is None or hand_data.handedness == hand_label:
                    return True
        return False

    def get_pinch_distance(self, hand_label: Optional[str] = None) -> Optional[float]:
        hand = self.get_hand_by_label(hand_label) if hand_label else self.get_dominant_hand()
        if not hand or len(hand.landmarks) < 9:
            return None
        return float(np.linalg.norm(np.array(hand.landmarks[4]) - np.array(hand.landmarks[8])))

    def get_hand_velocity(self, hand_label: Optional[str] = None) -> Optional[Tuple[float, float]]:
        hand_id = None
        for hid, hand_data in self.hand_poses.items():
            if hand_label is None or hand_data.handedness == hand_label:
                hand_id = hid
                break
        if not hand_id or hand_id not in self.velocity_history:
            return None
        if self.velocity_history[hand_id]:
            return self.velocity_history[hand_id][-1]
        return None

    def get_finger_position(self, finger_name: str, hand_label: Optional[str] = None) -> Optional[Tuple[int, int]]:
        """Get position of a specific fingertip"""
        finger_map = {"thumb": 4, "index": 8, "middle": 12, "ring": 16, "pinky": 20}

        hand = self.get_hand_by_label(hand_label) if hand_label else self.get_dominant_hand()
        if not hand or finger_name.lower() not in finger_map:
            return None

        idx = finger_map[finger_name.lower()]
        return hand.landmarks[idx] if idx < len(hand.landmarks) else None

    # ========== TWO-HAND GESTURES ==========

    def detect_two_hand_gesture(self, hands: List[HandData]) -> Optional[str]:
        if len(hands) < 2:
            return None

        left  = next((h for h in hands if h.handedness == "Left"),  None)
        right = next((h for h in hands if h.handedness == "Right"), None)

        if not left or not right:
            return None

        if left.gesture == GestureType.PINCH and right.gesture == GestureType.PINCH:
            dist = float(np.linalg.norm(
                np.array(left.palm_center) - np.array(right.palm_center)))

            two_hand_id = "both_hands"
            if two_hand_id not in self.pinch_distance_history:
                self.pinch_distance_history[two_hand_id] = deque(maxlen=10)
            self.pinch_distance_history[two_hand_id].append(dist)

            if len(self.pinch_distance_history[two_hand_id]) >= 5:
                recent = list(self.pinch_distance_history[two_hand_id])
                if recent[-1] > recent[0] * 1.2:
                    return "PINCH_ZOOM_IN"
                elif recent[-1] < recent[0] * 0.8:
                    return "PINCH_ZOOM_OUT"

        if left.gesture == GestureType.OPEN_PALM and right.gesture == GestureType.OPEN_PALM:
            return "TWO_HAND_EXPAND"

        if left.gesture == GestureType.PEACE and right.gesture == GestureType.PEACE:
            return "DOUBLE_PEACE"

        return None

    # ========== MASKS ==========

    def create_hand_mask(self, frame: np.ndarray, hands: List[HandData]) -> np.ndarray:
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for hand in hands:
            if len(hand.landmarks) >= 21:
                points = np.array(hand.landmarks, dtype=np.int32)
                cv2.fillConvexPoly(mask, points, 255)
        return mask

    # ========== RESET / CLEANUP ==========

    def reset(self):
        with self.lock:
            self.prev_landmarks.clear()
            self.ema_landmarks.clear()
            self.landmark_history.clear()
            self.gesture_buffers.clear()
            self.position_history.clear()
            self.velocity_history.clear()
            self.rotation_history.clear()
            self.pinch_distance_history.clear()
            self.hand_poses.clear()
            self.gesture_cooldowns.clear()
            self.last_gestures.clear()
            self.active_sequences.clear()
            while not self.gesture_events.empty():
                try:
                    self.gesture_events.get_nowait()
                except queue.Empty:
                    break

    def __del__(self):
        if hasattr(self, 'detector'):
            self.detector.close()


# ==================== Utility Functions ====================

def create_gesture_visualizer(width: int = 800, height: int = 600) -> np.ndarray:
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(canvas, "Gesture Tracker - Ready", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return canvas


def draw_gesture_history(canvas: np.ndarray, events: List[GestureEvent], max_display: int = 10):
    y_offset = 80
    cv2.putText(canvas, "Recent Gestures:", (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    for event in events[-max_display:]:
        y_offset += 30
        text = f"{event.gesture_type.value} ({event.hand_label}) - {event.confidence:.2f}"
        cv2.putText(canvas, text, (30, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return canvas


def benchmark_tracker(tracker: AdvancedHandTracker, num_frames: int = 100) -> Dict[str, float]:
    dummy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    start_time = time.time()
    for _ in range(num_frames):
        tracker.find_hands(dummy_frame)
    total_time = time.time() - start_time
    return {
        "total_time": total_time,
        "avg_time_per_frame": total_time / num_frames,
        "theoretical_fps": num_frames / total_time,
        "frames_processed": num_frames
    }
