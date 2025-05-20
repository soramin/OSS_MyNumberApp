#必要なライブラリ
pip install pyscard

"""
処理の全体像
ICカードに接続
券面入力補助APを選択
PIN（券面PIN）の認証（Verify）
データ読み出し（Read Binary）で生年月日を取得
年齢計算・判定
"""

from smartcard.System import readers
from smartcard.util import toHexString
import datetime

# 証明書格納先APのAID（券面入力補助AP）
KENMEN_INPUT_AID = [0xD3, 0x92, 0xF0, 0x00, 0x26, 0x01, 0x01]  # JPKI 券面入力補助AP

# PIN入力後に使うPIN識別子（券面用：0x01）
PIN_REFERENCE = 0x01

# 生年月日読み出し時に指定するファイルID（'住民票コード'や'生年月日'などを含む）
# 本例では仮にEF01の構成で生年月日が含まれているとする
BIRTHDATE_FILE_ID = [0x00, 0x11]  # ※実際の構成により異なる。開発キットで要確認。

# APDU送信用関数
def send_apdu(connection, apdu, expect_success=True):
    response, sw1, sw2 = connection.transmit(apdu)
    status = (sw1 << 8) | sw2
    if expect_success and status != 0x9000:
        raise RuntimeError(f"APDU失敗: SW={hex(status)}")
    return response

# AP選択
def select_ap(connection):
    select_apdu = [0x00, 0xA4, 0x04, 0x00, len(KENMEN_INPUT_AID)] + KENMEN_INPUT_AID
    send_apdu(connection, select_apdu)

# PIN認証（券面PIN）
def verify_pin(connection, pin: str):
    pin_bytes = [ord(c) for c in pin]
    # VERIFY command: CLA INS P1 P2 Lc [PIN]
    apdu = [0x00, 0x20, 0x00, PIN_REFERENCE, len(pin_bytes)] + pin_bytes
    send_apdu(connection, apdu)

# ファイル選択
def select_file(connection, file_id):
    apdu = [0x00, 0xA4, 0x00, 0x0C, len(file_id)] + file_id
    send_apdu(connection, apdu)

# バイナリデータ読み出し（最大256バイト）
def read_binary(connection, length=256):
    apdu = [0x00, 0xB0, 0x00, 0x00, length]
    response = send_apdu(connection, apdu)
    return bytes(response)

# 誕生日抽出（仮定：YYYYMMDDの8桁が含まれているバイナリデータ）
def extract_birthdate_from_binary(data):
    # 仮に文字列形式で含まれているとして検索
    for i in range(len(data) - 8):
        segment = data[i:i+8]
        try:
            s = segment.decode("ascii")
            if s.isdigit():
                year = int(s[:4])
                month = int(s[4:6])
                day = int(s[6:8])
                return datetime.date(year, month, day)
        except:
            continue
    raise ValueError("生年月日の抽出に失敗しました")

# 年齢を計算
def calculate_age(birthdate):
    today = datetime.date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

# メイン処理
def main():
    r = readers()
    if not r:
        print("カードリーダーが見つかりません")
        return

    reader = r[0]
    connection = reader.createConnection()
    connection.connect()
    print(f"接続成功：{reader}")

    # AP選択
    print("券面入力補助APを選択中...")
    select_ap(connection)

    # PIN入力
    pin = input("券面入力補助APのPIN（4桁）を入力してください：")
    verify_pin(connection, pin)
    print("PIN認証成功")

    # 生年月日ファイル選択
    print("生年月日データのファイル選択...")
    select_file(connection, BIRTHDATE_FILE_ID)

    # バイナリ読み出し
    print("データ読み出し中...")
    binary_data = read_binary(connection)

    # 生年月日抽出
    birthdate = extract_birthdate_from_binary(binary_data)
    print(f"生年月日：{birthdate}")

    # 年齢確認
    age = calculate_age(birthdate)
    print(f"年齢：{age}歳")

    if age >= 20:
        print("成人確認済み：購入許可")
    else:
        print("未成年のため購入不可")

if __name__ == "__main__":
    main()
