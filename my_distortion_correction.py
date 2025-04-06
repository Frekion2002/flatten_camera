import cv2 as cv
import numpy as np

# === 캘리브레이션 데이터 로드 ===
data = np.load('calibration_data.npz')
mtx = data['mtx']
dist = data['dist']

# === 이미지 로드 ===
img = cv.imread("D:\\ComputerVision\\CV_image\\my_distortion_image.jpg")
if img is None:
    print("오류: 이미지 파일을 읽을 수 없습니다.")
    exit()

h, w = img.shape[:2]

# === 왜곡 보정 ===
new_mtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
undistorted = cv.undistort(img, mtx, dist, None, new_mtx)

# ✅ === 리사이즈 비율 계산 (가로 800px, 세로 600px 제한) ===
max_width = 800
max_height = 600

scale_w = max_width / w
scale_h = max_height / h
scale = min(scale_w, scale_h)  # 가장 작은 비율로 맞춤

new_size = (int(w * scale), int(h * scale))
img_resized = cv.resize(img, new_size)
undistorted_resized = cv.resize(undistorted, new_size)

# === before/after 나란히 비교 이미지 생성 ===
combined = np.hstack((img_resized, undistorted_resized))

# === 결과 저장 및 출력 ===
cv.imwrite('undistorted_image.jpg', undistorted)
cv.imwrite('comparison.jpg', combined)

cv.imshow('Before / After (Original vs undistortion)', combined)
cv.waitKey(0)
cv.destroyAllWindows()
