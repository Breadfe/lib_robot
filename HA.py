import cv2
import numpy as np
import csv
import os

# 카메라 매트릭스 및 왜곡 계수 (예시 값, 실제 값 사용)
camera_matrix = np.array([[685.743002, 0, 354.820686],
                          [0, 691.365535, 226.926372],
                          [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.array([-0.374352, 0.081275, 0.000314, -0.002013, 0.000000])  # 왜곡이 없다고 가정

# QR 코드의 월드 좌표 정의 (3.5x3.5 cm 크기)
qr_size = 2.0
world_points = np.array([
    [0, 0, 0],
    [qr_size, 0, 0],
    [qr_size, qr_size, 0],
    [0, qr_size, 0]
], dtype=np.float32)

# 카메라 캡처 설정
cap = cv2.VideoCapture(1)  # 0번 카메라 (웹캠)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

detector = cv2.QRCodeDetector()

# CSV 파일 초기화
csv_file_path = "save_qr_code_info.csv"
file_exists = os.path.isfile(csv_file_path)
with open(csv_file_path, 'a', newline='') as csvfile:
    fieldnames = ['Title', 'Author', 'ISBN', 'X', 'Y', 'Z']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # QR 코드 검출 및 디코딩
    retval, decoded_info, vertices, straight_qrcode = detector.detectAndDecodeMulti(frame)
    print(decoded_info)

    if vertices is not None:
        for i in range(len(vertices)):
            vertices[i] = vertices[i].reshape(-1, 2)  # (4, 2) 형태로 변환
            image_points = np.array(vertices[i], dtype=np.float32)

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
                frame = cv2.line(frame, origin, tuple(imgpts[0].ravel()), (255, 0, 0), 3)  # X축 (파란색)
                frame = cv2.line(frame, origin, tuple(imgpts[1].ravel()), (0, 255, 0), 3)  # Y축 (초록색)
                frame = cv2.line(frame, origin, tuple(imgpts[2].ravel()), (0, 0, 255), 3)  # Z축 (빨간색)

                # QR 코드의 데이터를 프레임에 표시
                if decoded_info[i]:
                    x, y = int(vertices[i][0][0]), int(vertices[i][0][1]) - 10
                    for j, line in enumerate(decoded_info[i].split('\n')):
                        cv2.putText(frame, line, (x, y - (j * 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                    # QR 코드 데이터 파싱
                    qr_info = decoded_info[i].split(',')
                    if len(qr_info) == 3:
                        title, author, isbn = qr_info[0].strip(), qr_info[1].strip(), qr_info[2].strip()
                        x, y, z = translation_vector[0][0], translation_vector[1][0], translation_vector[2][0]
                        
                        # CSV 파일에 데이터 저장
                        with open(csv_file_path, 'a', newline='') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writerow({'Title': title, 'Author': author, 'ISBN': isbn, 'X': x, 'Y': y, 'Z': z})

    # 프레임을 화면에 표시
    cv2.imshow('QR Code PnP', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 리소스 해제
cap.release()
cv2.destroyAllWindows()
