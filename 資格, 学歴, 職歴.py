#bash (必要ライブラリ)

pip install reportlab
pip install reportlab pillow

#Python コード
import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

DATA_FILE = 'my_number_profile.json'
PDF_OUTPUT = 'rirekisho_output.pdf'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def set_basic_info(my_number, name, email, phone, address):
    data = load_data()
    user = data.setdefault(my_number, {
        "name": "", "email": "", "phone": "", "address": "",
        "qualifications": [], "education": [], "work_history": [], "photo": ""
    })
    user["name"] = name
    user["email"] = email
    user["phone"] = phone
    user["address"] = address
    save_data(data)

def set_photo(my_number, photo_path):
    data = load_data()
    user = data.setdefault(my_number, {
        "name": "", "email": "", "phone": "", "address": "",
        "qualifications": [], "education": [], "work_history": [], "photo": ""
    })
    user["photo"] = photo_path
    save_data(data)

def add_qualification(my_number, qualification):
    data = load_data()
    user = data.setdefault(my_number, {
        "name": "", "email": "", "phone": "", "address": "",
        "qualifications": [], "education": [], "work_history": [], "photo": ""
    })
    user["qualifications"].append(qualification)
    save_data(data)

def add_education(my_number, education):
    data = load_data()
    user = data.setdefault(my_number, {
        "name": "", "email": "", "phone": "", "address": "",
        "qualifications": [], "education": [], "work_history": [], "photo": ""
    })
    user["education"].append(education)
    save_data(data)

def add_work_history(my_number, work):
    data = load_data()
    user = data.setdefault(my_number, {
        "name": "", "email": "", "phone": "", "address": "",
        "qualifications": [], "education": [], "work_history": [], "photo": ""
    })
    user["work_history"].append(work)
    save_data(data)

def generate_resume_pdf(my_number):
    data = load_data()
    user = data.get(my_number)

    if not user:
        print("データが見つかりません。")
        return

    c = canvas.Canvas(PDF_OUTPUT, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(220, y, "履歴書")
    y -= 40

    # 基本情報
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"氏名: {user.get('name', '')}")
    y -= 20
    c.drawString(50, y, f"メール: {user.get('email', '')}")
    y -= 20
    c.drawString(50, y, f"電話: {user.get('phone', '')}")
    y -= 20
    c.drawString(50, y, f"住所: {user.get('address', '')}")
    y -= 30

    # 顔写真
    photo_path = user.get("photo", "")
    if photo_path and os.path.exists(photo_path):
        try:
            img = Image.open(photo_path)
            img.thumbnail((100, 120))
            img_io = ImageReader(img)
            c.drawImage(img_io, width - 150, height - 200, width=100, height=120)
        except Exception as e:
            print(f"写真の読み込みに失敗しました: {e}")

    # 学歴
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "学歴")
    y -= 20
    c.setFont("Helvetica", 12)
    for edu in user.get("education", []):
        c.drawString(60, y, f"{edu['start']}〜{edu['end']}：{edu['school']}（{edu['degree']}）")
        y -= 20

    y -= 20

    # 職歴
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "職歴")
    y -= 20
    c.setFont("Helvetica", 12)
    for work in user.get("work_history", []):
        c.drawString(60, y, f"{work['start']}〜{work['end']}：{work['company']}（{work['position']}）")
        y -= 20

    y -= 20

    # 資格
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "資格")
    y -= 20
    c.setFont("Helvetica", 12)
    for qual in user.get("qualifications", []):
        c.drawString(60, y, f"{qual['date']}：{qual['name']}（{qual['issuer']}）")
        y -= 20

  #このままコンビニで履歴書をプリントできる
    c.save()
    print(f"履歴書PDFを出力しました: {PDF_OUTPUT}")

# --- 使用例 --- 
if __name__ == '__main__':
    my_number = "1234567890123"

    set_basic_info(
        my_number,
        name="山田 太郎",
        email="taro.yamada@example.com",
        phone="090-1234-5678",
        address="東京都新宿区1-2-3"
    )

    set_photo(my_number, "photo.jpg")

    add_education(my_number, {
        "school": "東京大学 工学部",
        "degree": "学士",
        "start": "2015-04",
        "end": "2019-03"
    })

    add_work_history(my_number, {
        "company": "株式会社テックジャパン",
        "position": "ソフトウェアエンジニア",
        "start": "2019-04",
        "end": "2023-03"
    })

    add_qualification(my_number, {
        "name": "基本情報技術者試験",
        "date": "2018-10-01",
        "issuer": "IPA"
    })

    generate_resume_pdf(my_number)
