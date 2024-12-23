import cv2
import numpy as np
import csv
import os

# 카메라 매트릭스 및 왜곡 계수
camera_matrix = np.array([[685.743002, 0, 354.820686],
                          [0, 691.365535, 226.926372],
                          [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.array([-0.374352, 0.081275, 0.000314, -0.002013, 0.000000])

# QR 코드의 월드 좌표 정의 (2x2 cm 크기)
qr_size = 2.0
world_points = np.array([
    [0, 0, 0],
    [qr_size, 0, 0],
    [qr_size, qr_size, 0],
    [0, qr_size, 0]
], dtype=np.float32)


# CSV 파일 설정 -> 여기수정
csv_file_path = "C:/Users/82108/Desktop/2024_ugrp/save_qr_code_info_20241223.csv"
fieldnames = ["Title", "Author", "ISBN", "X", "Y", "Z"]

# CSV 파일 생성
if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()


# 카메라 캡처 설정
cap = cv2.VideoCapture(0)  # 0번 카메라 (웹캠)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

detector = cv2.QRCodeDetector()
previous_qr_codes = []

while True:
    ret, frame = cap.read()
    # ret은 프레임 정상적으로 읽었는지(True/false), frame은 이미지 프레임 데이터(높이, 너비, 채널)
    if not ret:
        break

    # 그레이스케일로 변환(연산량 감소)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 이진화(그레이스케일 이미지 -> 이진 이미지 변환) 100 기준으로 흰/검 나눔
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(contours)

    qr_codes = []

    for cnt in contours:
        # 외곽선 단순화해서 꼭짓점 얻는 함수, approx는 꼭짓점 좌표 포함한 리스트 형식
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4:  # 사각형 검출
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 20 and h > 20:  # 너무 작은 사각형은 무시
                region_of_interest = frame[y:y+h, x:x+w]
                data, vertices, _ = detector.detectAndDecode(region_of_interest)
                if vertices is not None:
                    vertices = vertices.reshape(-1, 2) + np.array([x, y])
                    qr_codes.append((data, vertices))

 # 왼쪽부터 차례대로 정렬
    qr_codes.sort(key=lambda code: code[1].min(axis=0)[0])

    # 겹치는 책이 있는 경우 이를 기준으로 전체 순서 다시 인식
    if previous_qr_codes:
        prev_titles = [code[0].split('\n')[0].split(': ')[1] for code in previous_qr_codes if len(code[0].split('\n')) > 0 and ': ' in code[0].split('\n')[0]]
        current_titles = [code[0].split('\n')[0].split(': ')[1] for code in qr_codes if len(code[0].split('\n')) > 0 and ': ' in code[0].split('\n')[0]]
        matched_indices = []

        for i, prev_title in enumerate(prev_titles):
            if prev_title in current_titles:
                j = current_titles.index(prev_title)
                matched_indices.append((i, j))

        # 정렬된 순서로 재배치
        if matched_indices:
            sorted_indices = sorted(matched_indices, key=lambda x: x[0])
            qr_codes = [qr_codes[j] for _, j in sorted_indices]

    for data, vertices in qr_codes:
        image_points = np.array(vertices, dtype=np.float32)
        success, rotation_vector, translation_vector = cv2.solvePnP(world_points, image_points, camera_matrix, dist_coeffs)

        if success:

            # QR 코드의 모서리
            for point in image_points:
                cv2.circle(frame, (int(point[0]), int(point[1])), 5, (0, 255, 0), -1)

            # 카메라 좌표계
            axis = np.float32([[5, 0, 0], [0, 5, 0], [0, 0, -5]]).reshape(-1, 3)
            imgpts, _ = cv2.projectPoints(axis, rotation_vector, translation_vector, camera_matrix, dist_coeffs)
            imgpts = imgpts.astype(int)

            origin = (int(image_points[0][0]), int(image_points[0][1]))
            frame = cv2.line(frame, origin, tuple(imgpts[0].ravel()), (255, 0, 0), 3)  # X축 (파란색)
            frame = cv2.line(frame, origin, tuple(imgpts[1].ravel()), (0, 255, 0), 3)  # Y축 (초록색)
            frame = cv2.line(frame, origin, tuple(imgpts[2].ravel()), (0, 0, 255), 3)  # Z축 (빨간색)

            # QR 코드데이터 표시
            try:
                if data:
                    x, y = int(vertices[0][0]), int(vertices[0][1]) - 10
                    title, author, isbn = [line.split(': ')[1] for line in data.split('\n') if ': ' in line]
                    for i, line in enumerate(data.split('\n')):
                        cv2.putText(frame, line, (x, y - (i * 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                    with open(csv_file_path, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([title, author, isbn, translation_vector[0][0], translation_vector[1][0], translation_vector[2][0]])
            except Exception as e:
                print("Error parsing QR data:", e)

    previous_qr_codes = qr_codes

    cv2.imshow('QR Code PnP', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()