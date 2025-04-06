import cv2
import numpy as np
import time

# === 설정 ===
chessboard_size = (8, 6)       # 체스보드 내부 코너 수 (가로, 세로)
square_size = 0.025            # 각 사각형의 한 변 길이 (미터 단위)
video_path = "D:\\ComputerVision\\CV_image\\my_chessboard.mp4"
max_frames_to_use = 20         # 캘리브레이션에 사용할 최대 프레임 수
frame_skip = 10                # 몇 프레임마다 체스보드 감지 시도

# === 체스보드 3D 객체 포인트 설정 ===
objp = np.zeros((chessboard_size[0]*chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * square_size

obj_points = []  # 3D 실세계 좌표
img_points = []  # 2D 이미지 좌표
image_size = None

# 코너 정제 기준
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# === 동영상 로드 ===
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("❌ 오류: 동영상을 열 수 없습니다.")
    exit()

frame_idx = 0
collected = 0

print("📷 체스보드 감지 시작 (감지되면 'q'로 중단 가능)...")
while cap.isOpened():
    ret, frame = cap.read()
    if not ret or collected >= max_frames_to_use:
        break

    frame_idx += 1
    if frame_idx % frame_skip != 0:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    found, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
    if found:
        if image_size is None:
            image_size = gray.shape[::-1]

        corners_sub = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        obj_points.append(objp)
        img_points.append(corners_sub)
        collected += 1

        cv2.drawChessboardCorners(frame, chessboard_size, corners_sub, found)
        print(f"✅ 체스보드 감지됨: {collected}/{max_frames_to_use}")

    cv2.imshow("Chessboard Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# === 캘리브레이션 ===
if len(obj_points) >= 3:
    print("\n🧮 캘리브레이션 시작...")
    start_time = time.time()
    try:
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            obj_points, img_points, image_size, None, None)
        elapsed = time.time() - start_time

        print("\n✅ 캘리브레이션 성공!")
        print("카메라 매트릭스:\n", mtx)
        print("\n왜곡 계수:\n", dist.ravel())
        print(f"\n📉 RMSE (재투영 오차): {ret:.4f}")
        print(f"⏱ 소요 시간: {elapsed:.2f}초")

        # 결과 저장
        np.savez('calibration_data.npz', mtx=mtx, dist=dist)
        print("💾 결과가 'calibration_data.npz'로 저장되었습니다.")
    except cv2.error as e:
        print("❌ 캘리브레이션 중 오류 발생:", e)
else:
    print("⚠️ 캘리브레이션을 위한 충분한 체스보드가 감지되지 않았습니다.")
