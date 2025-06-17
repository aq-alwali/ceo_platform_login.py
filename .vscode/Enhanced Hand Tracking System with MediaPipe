import cv2
import mediapipe as mp
import time
import numpy as np

class HandDetector():
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode 
        self.maxHands = maxHands
        self.modelComplexity = modelComplexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            model_complexity=self.modelComplexity,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None
        self.hand_connections = self.mpHands.HAND_CONNECTIONS
        self.landmark_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), 
                               (255, 255, 0), (255, 0, 255)]
        
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.drawHands(img, handLms)
        return img
    
    def drawHands(self, img, handLms):
        # Draw connections
        self.mpDraw.draw_landmarks(
            img, 
            handLms, 
            self.hand_connections,
            connection_drawing_spec=self.mpDraw.DrawingSpec(color=(200, 200, 200),
            ))
        
        # Draw landmarks with custom colors
        for id, lm in enumerate(handLms.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            color_idx = id % len(self.landmark_colors)
            cv2.circle(img, (cx, cy), 7, self.landmark_colors[color_idx], cv2.FILLED)
    
    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results and self.results.multi_hand_landmarks:
            if handNo < len(self.results.multi_hand_landmarks):
                myHand = self.results.multi_hand_landmarks[handNo]
                for id, lm in enumerate(myHand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
        return lmList
    
    def detectGesture(self, lmList):
        if len(lmList) < 21:
            return "Unknown"
        
        # Thumb detection
        thumb_tip = lmList[4][1:]
        thumb_base = lmList[2][1:]
        thumb_open = thumb_tip[0] > thumb_base[0]
        
        # Finger tips and base joints
        fingers = []
        for tip_id, pip_id in [(8, 6), (12, 10), (16, 14), (20, 18)]:  # Index, Middle, Ring, Pinky
            tip = lmList[tip_id][1:]
            pip = lmList[pip_id][1:]
            fingers.append(1 if tip[1] < pip[1] else 0)
        
        # Count open fingers
        open_fingers = fingers.count(1)
        
        # Gesture recognition
        if open_fingers == 0 and not thumb_open:
            return "Fist"
        elif open_fingers == 5:
            return "Open Hand"
        elif open_fingers == 1 and fingers[0] == 1 and not thumb_open:
            return "Pointing"
        elif open_fingers == 2 and fingers[0] == 1 and fingers[1] == 1:
            return "Victory"
        elif open_fingers == 3 and thumb_open:
            return "OK"
        elif open_fingers == 0 and thumb_open:
            return "Thumbs Up"
        
        return f"{open_fingers} fingers"

def main():
    pTime = 0
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return
    
    # Create detector with higher detection confidence
    detector = HandDetector(detectionCon=0.8, trackCon=0.8)
    
    # Create UI elements
    ui_elements = []
    
    while True:
        success, img = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
            
        img = cv2.flip(img, 1)  # Mirror the image
        img = detector.findHands(img)
        
        # Get hand positions
        lmList = detector.findPosition(img)
        
        # Create UI background
        ui_bg = np.zeros((img.shape[0], 300, 3), dtype=np.uint8)
        
        # Add title
        cv2.putText(ui_bg, "Hand Tracking", (30, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add instructions
        instructions = [
            "Q: Quit",
            "S: Save Frame",
            "C: Toggle Connections",
            "L: Toggle Landmarks"
        ]
        
        for i, text in enumerate(instructions):
            cv2.putText(ui_bg, text, (20, 80 + i*30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Detect gestures
        gesture = "No hand detected"
        if len(lmList) > 0:
            gesture = detector.detectGesture(lmList)
        
        # Display gesture
        cv2.putText(ui_bg, f"Gesture: {gesture}", (20, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Display hand count
        hand_count = len(detector.results.multi_hand_landmarks) if detector.results and detector.results.multi_hand_landmarks else 0
        cv2.putText(ui_bg, f"Hands: {hand_count}", (20, 250), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
        
        # Calculate and display FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, 30), 
                   cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        
        # Combine UI with video
        combined = np.hstack((img, ui_bg))
        
        cv2.imshow("Hand Tracking System", combined)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save current frame
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"hand_tracking_{timestamp}.jpg", combined)
            print(f"Frame saved as hand_tracking_{timestamp}.jpg")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
