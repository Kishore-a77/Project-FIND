import cv2
import time
import json
import numpy as np
import traceback
import sys

from app.services.face_service import detect_faces
from app.services.matching_service import find_best_match
from app.services.db_service import get_connection, create_pending_match

CAMERA_LOCATION = "Main Gate Camera"
PROCESS_INTERVAL = 0.7
DB_REFRESH_INTERVAL = 5.0
MATCH_DISPLAY_TIME = 1.5


def get_box_color(confidence):
    """Return box color based on confidence score"""
    if confidence >= 0.80:
        return (0, 255, 0)  # Green - Strong match
    elif confidence >= 0.65:
        return (0, 255, 255)  # Yellow - Probable match
    else:
        return (0, 0, 255)  # Red - Unknown/weak match


def get_label_text(match):
    """Generate label text for the bounding box"""
    if match:
        return f"{match['name']} ({match['score']:.2f})"
    else:
        return "Unknown Person"


def print_banner():
    """Print a nice banner"""
    print("╔" + "═" * 58 + "╗")
    print("║                 VISION ENGINE STARTED                 ║")
    print("╠" + "═" * 58 + "╣")
    print("║ 📹  Live Camera Feed Active                          ║")
    print("║ 🎯  Face Detection: ENABLED                          ║")
    print("║ 🔍  Person Matching: ENABLED                         ║")
    print("╠" + "═" * 58 + "╣")
    print("║ 📋  CONTROLS:                                        ║")
    print("║     • Press 'q' to quit                              ║")
    print("║     • Press ESC to quit                              ║")
    print("║     • Close window to stop                           ║")
    print("╠" + "═" * 58 + "╣")
    print("║ 🎨  COLOR LEGEND:                                    ║")
    print("║     🟢  Green:  Strong Match (≥ 0.80)                ║")
    print("║     🟡  Yellow: Probable Match (0.65-0.80)           ║")
    print("║     🔴  Red:    Unknown/Weak Match                   ║")
    print("╚" + "═" * 58 + "╝")
    print()


def try_cameras():
    """Try different camera indices"""
    for i in range(3):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Connected to camera index {i}")
                return cap, i
            cap.release()
    
    print("❌ No working camera found. Please check:")
    print("   1. Is camera connected?")
    print("   2. Is it being used by another app?")
    print("   3. Try reconnecting the camera")
    return None, -1


def main():
    print_banner()
    
    # Try to open camera
    cap, camera_index = try_cameras()
    if cap is None:
        print("\nPress Enter to exit...")
        input()
        return
    
    print(f"📊 Starting face recognition system...")
    print(f"📍 Camera Location: {CAMERA_LOCATION}")
    print(f"🎯 Matching Threshold: 0.45")
    print("-" * 60)
    
    db_embeddings = []
    last_process = 0.0
    last_db_refresh = 0.0
    active_log_id = None
    active_person_id = None
    last_match = None
    last_match_expiry = 0.0
    frame_count = 0
    start_time = time.time()
    
    # Set window properties
    window_name = "🔍 Face Recognition Camera - Press 'q' to exit"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Lost connection to camera")
                break
            
            frame_count += 1
            now = time.time()
            
            # Refresh database embeddings periodically
            if now - last_db_refresh > DB_REFRESH_INTERVAL:
                try:
                    conn = get_connection()
                    rows = conn.execute(
                        "SELECT PERSON_ID, NAME, EMBEDDING FROM MISSING_PERSONS"
                    ).fetchall()
                    conn.close()
                    
                    db_embeddings = [
                        {
                            "person_id": r[0],
                            "name": r[1],
                            "embedding": np.array(json.loads(r[2]), dtype="float32"),
                        }
                        for r in rows if r[2]
                    ]
                    
                    last_db_refresh = now
                    if frame_count % 30 == 0:
                        print(f"📊 Database: {len(db_embeddings)} persons loaded | FPS: {frame_count/(now-start_time):.1f}")
                except Exception as e:
                    print(f"⚠️ Database error: {e}")
            
            # Process faces at intervals
            if now - last_process > PROCESS_INTERVAL:
                last_process = now
                
                try:
                    faces = detect_faces(frame)
                    
                    for face in faces:
                        match = find_best_match(face.embedding, db_embeddings)
                        x1, y1, x2, y2 = face.bbox.astype(int)
                        
                        if match:
                            color = get_box_color(match['score'])
                            label = get_label_text(match)
                            
                            last_match = {
                                "bbox": (x1, y1, x2, y2),
                                "label": label,
                                "color": color,
                                "confidence": match['score']
                            }
                            last_match_expiry = now + MATCH_DISPLAY_TIME
                            
                            # Log new matches
                            if active_log_id is None or active_person_id != match["person_id"]:
                                active_log_id = create_pending_match(
                                    person_id=match["person_id"],
                                    confidence=match["score"],
                                    camera_location=CAMERA_LOCATION
                                )
                                active_person_id = match["person_id"]
                                print(f"✅ Match: {match['name']} (ID: {match['person_id'][:8]}..., Score: {match['score']:.2f})")
                        else:
                            # Unknown person
                            color = get_box_color(0)
                            label = "Unknown Person"
                            last_match = {
                                "bbox": (x1, y1, x2, y2),
                                "label": label,
                                "color": color,
                                "confidence": 0
                            }
                            last_match_expiry = now + MATCH_DISPLAY_TIME
                            active_log_id = None
                            active_person_id = None
                
                except Exception as e:
                    print(f"⚠️ Face processing error: {e}")
            
            # Draw bounding box if recent match
            if last_match and now < last_match_expiry:
                x1, y1, x2, y2 = last_match["bbox"]
                color = last_match["color"]
                label = last_match["label"]
                
                # Draw box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                
                # Draw label background
                (label_width, label_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                )
                cv2.rectangle(
                    frame,
                    (x1, y1 - label_height - 10),
                    (x1 + label_width + 10, y1),
                    color,
                    -1
                )
                
                # Draw label text
                text_color = (255, 255, 255) if color != (0, 255, 255) else (0, 0, 0)
                cv2.putText(
                    frame,
                    label,
                    (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    text_color,
                    2,
                )
            
            # Add status overlay
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (350, 130), (0, 0, 0), -1)
            frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
            
            # Status text
            status_lines = [
                f"Persons in DB: {len(db_embeddings)}",
                f"FPS: {frame_count/(time.time()-start_time):.1f}",
                f"Camera: {camera_index}",
                "Press 'q' to exit"
            ]
            
            for i, line in enumerate(status_lines):
                cv2.putText(
                    frame,
                    line,
                    (10, 25 + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1,
                )
            
            # Add color legend
            legend_x, legend_y = 10, 110
            colors = [(0, 255, 0), (0, 255, 255), (0, 0, 255)]
            labels = ["Strong", "Probable", "Unknown"]
            
            for i, (color, label) in enumerate(zip(colors, labels)):
                cv2.rectangle(frame, 
                            (legend_x, legend_y + i * 20),
                            (legend_x + 15, legend_y + 15 + i * 20),
                            color, -1)
                cv2.putText(frame, label,
                          (legend_x + 20, legend_y + 12 + i * 20),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                          (255, 255, 255), 1)
            
            # Show frame
            cv2.imshow(window_name, frame)
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27 or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("\n🛑 Shutting down camera...")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
    finally:
        # Cleanup
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        print("✅ Camera feed stopped")
        print("=" * 60)
        print("You can close this window now.")
        print("Or press Enter to close...")
        input()


if __name__ == "__main__":
    main()