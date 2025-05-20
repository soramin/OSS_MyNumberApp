#「マイナンバーカード連携による年齢確認＋自販機連携」用Pythonアプリケーションの本格実装

"""
構成概要
1. ICカード読み取り	マイナンバーカードから氏名・生年月日を取得。JPKI対応。
2. 年齢検証処理	20歳未満は拒否。法令に基づくアルゴリズムで年齢を算出。
3. 自販機と連携	HTTP/BLE通信で販売OK/NG信号を送信。
4. ログ記録（オプション）	ログに個人情報を記録しないように設計。
"""

"""
ディレクトリ構成 (arduino 例)
age_verification_app/
├── main.py
├── card_reader.py
├── verifier.py
├── vending_interface.py
├── config.py
├── utils.py
└── requirements.txt
"""

"""
requirements.txt
requests
python-dotenv
"""

"""
config.py
import os
from dotenv import load_dotenv

load_dotenv()

# 自販機通信先設定
VENDING_MACHINE_API = os.getenv("VENDING_MACHINE_API", "http://localhost:8000/verify")
AGE_LIMIT = 20
"""

#card_reader.py（仮想のカードリーダースクリプト呼び出し）
import datetime
import subprocess

def get_user_birthdate():
    """
    ICカードから生年月日を取得する仮関数
    実際はJPKI API等と連携する必要あり
    """
    try:
        result = subprocess.check_output(["./read_card_info.sh"], universal_newlines=True)
        for line in result.splitlines():
            if "Birthdate" in line:
                birth_str = line.split(":")[1].strip()
                return datetime.datetime.strptime(birth_str, "%Y-%m-%d").date()
    except Exception as e:
        print(f"[ERROR] カード読み取り失敗: {e}")
        return None

#verifier.py（年齢検証）
import datetime
from config import AGE_LIMIT

def calculate_age(birthdate):
    today = datetime.date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def is_eligible(birthdate):
    age = calculate_age(birthdate)
    print(f"[INFO] ユーザー年齢: {age}")
    return age >= AGE_LIMIT

#vending_interface.py（自販機に結果送信）
import requests
from config import VENDING_MACHINE_API

def notify_machine(result: bool):
    status = "ok" if result else "denied"
    data = {"result": status}
    try:
        res = requests.post(VENDING_MACHINE_API, json=data, timeout=3)
        if res.status_code == 200:
            print(f"[INFO] 自販機通知成功: {status}")
        else:
            print(f"[WARN] 自販機通知失敗: {res.status_code}")
    except Exception as e:
        print(f"[ERROR] 自販機通信エラー: {e}")

#utils.py（補助機能）
def log(message: str):
    print(f"[LOG] {message}")

#main.py（全体制御）
from card_reader import get_user_birthdate
from verifier import is_eligible
from vending_interface import notify_machine

def main():
    print("=== 年齢確認システム 起動 ===")
    birthdate = get_user_birthdate()
    if not birthdate:
        print("[ERROR] 生年月日取得に失敗しました")
        notify_machine(False)
        return

    if is_eligible(birthdate):
        print("[INFO] 年齢確認OK")
        notify_machine(True)
    else:
        print("[INFO] 年齢未満：販売不可")
        notify_machine(False)

if __name__ == "__main__":
    main()
