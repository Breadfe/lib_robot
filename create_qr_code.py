import qrcode
import os

# 책 정보를 포함하는 데이터 (예시)
book_info = [# "Title: Deep Learning\nAuthor: Ian Goodfellow\nISBN: 9780262035613",
             "Foundation\nIsaac Asimov\n9788960177567",
             "Foundation and Empire\nIsaac Asimov\n9788960177574",
             "Second Foundation\nIsaac Asimov\n9788960177581",
             "Foundation's Edge\nIsaac Asimov\n9788960177598",
             "Foundation and earth\nIsaac Asimov\n9788960177604",
             "Prelude to Foundation\nIsaac Asimov\n9788960177611",
             "Forward the Foundation\nIsaac Asimov\n9788960177628",]


# QR 코드 생성
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

for idx, data in enumerate(book_info):
    print(len(data))
    qr.clear()
    qr.add_data(data)
    qr.make(fit=True)
    

# QR 코드 이미지 생성 및 저장 경로 설정

    qr_code_image_path = "qr_code"  # 저장할 경로
    qr_code_image_name = "qr.png" #파일명
    path = qr_code_image_path + "/" + str(idx) + "_" + qr_code_image_name

    if not os.path.isdir(qr_code_image_path):
        os.mkdir(qr_code_image_path)

    img = qr.make_image(fill='black', back_color='white')
    img.save(path)

    print(f"QR 코드가 '{path}'에 저장되었습니다.")
