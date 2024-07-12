import qrcode

# 책 정보를 포함하는 데이터 (예시)
book_info = "Title: Deep Learning\nAuthor: Ian Goodfellow\nISBN: 9780262035613"

# QR 코드 생성
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(book_info)
qr.make(fit=True)

# QR 코드 이미지 생성 및 저장 경로 설정
qr_code_image_path = "C:/Users/82108/Desktop/qr_code/qr.png"  # 저장할 경로와 파일명 설정
img = qr.make_image(fill='black', back_color='white')
img.save(qr_code_image_path)

print(f"QR 코드가 '{qr_code_image_path}'에 저장되었습니다.")
