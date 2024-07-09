import cv2
import numpy as np

# 카메라 매트릭스 및 왜곡 계수 (예시 값, 실제 값 사용)
camera_matrix = np.array([[685.743002, 0, 354.820686],
                          [0, 691.365535, 226.926372],
                          [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.array([-0.374352, 0.081275, 0.000314, -0.002013, 0.000000])  # 왜곡이 없다고 가정


# QR 코드의 월드 좌표 정의 (10x10 cm 크기)
qr_size = 3.5
world_points = np.array([
    [0, 0, 0],
    [qr_size, 0, 0],
    [qr_size, qr_size, 0],
    [0, qr_size, 0]
], dtype=np.float32)

# 카메라 캡처 설정
cap = cv2.VideoCapture(0)  # 0번 카메라 (웹캠)
def print_hi():
    print("Hi")
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

detector = cv2.QRCodeDetector()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # QR 코드 검출 및 디코딩
    data, vertices, _ = detector.detectAndDecode(frame)

    if vertices is not None:
        vertices = vertices.reshape(-1, 2)  # (4, 2) 형태로 변환
        image_points = np.array(vertices, dtype=np.float32)

        # SolvePnP 적용
        success, rotation_vector, translation_vector = cv2.solvePnP(world_points, image_points, camera_matrix, dist_coeffs)

        if success:
            # 결과 출력
            print("Rotation Vector:\n", rotation_vector)
            print("Translation Vector:\n", translation_vector)

            # QR 코드의 모서리를 프레임에 그리기
            for point in image_points:
                cv2.circle(frame, (int(point[0]), int(point[1])), 5, (0, 255, 0), -1)

            # 카메라 좌표계를 프레임에 그리기
            axis = np.float32([[5, 0, 0], [0, 5, 0], [0, 0, -5]]).reshape(-1, 3)
            imgpts, _ = cv2.projectPoints(axis, rotation_vector, translation_vector, camera_matrix, dist_coeffs)
            imgpts = imgpts.astype(int)

            origin = (int(image_points[0][0]), int(image_points[0][1]))
            frame = cv2.line(frame, origin, tuple(imgpts[0].ravel()), (255, 0, 0), 3) # X축 (파란색)
            frame = cv2.line(frame, origin, tuple(imgpts[1].ravel()), (0, 255, 0), 3) # Y축 (초록색)
            frame = cv2.line(frame, origin, tuple(imgpts[2].ravel()), (0, 0, 255), 3) # Z축 (빨간색)

    # 프레임을 화면에 표시
    cv2.imshow('QR Code PnP', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 리소스 해제
cap.release()
cv2.destroyAllWindows()
