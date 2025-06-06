"""
概要
コンビニなどでのセルフレジでの年齢確認省略を実装。
ただ、正直筆者の展望としては、自動販売機で酒タバコが購入できることを見込んでいるため、これはあくまでもオマケ。
"""

"""
前提条件
「ICカードリーダーが接続されている（例：Sony RC-S380）」

・以下のライブラリがインストールされている：
　pyscard（ICカード読み取り用）
　pyOpenSSL（証明書解析用）
　cryptography（証明書処理）

・マイナンバーカードの利用者証明用電子証明書にアクセスする

・PIN入力処理は、ここでは簡略化（UI実装次第）
"""

"""
実現方法の概要
NFCでマイナンバーカードに接続
・利用者証明用証明書を読み出す（ここに生年月日が含まれる）
・生年月日を元に年齢を計算
・例えば「20歳以上か？」を確認
"""

from datetime import datetime
from smartcard.System import readers
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# 認証証明書のファイル識別子（マイナンバーカード利用者証明用）
EF_CERTIFICATE = [0x00, 0xA4, 0x04, 0x00, 0x0A]  # 実際には異なる可能性あり

def connect_card():
    reader_list = readers()
    if not reader_list:
        raise Exception("カードリーダーが見つかりません。")

    reader = reader_list[0]
    connection = reader.createConnection()
    connection.connect()
    print(f"カードに接続しました: {reader}")
    return connection

def select_file(connection):
    # ファイル選択コマンド（仮）
    # 実際はJPKI仕様書に基づくAPDUが必要
    SELECT_APDU = [0x00, 0xA4, 0x04, 0x00, 0x08] + [0xA0, 0x00, 0x00, 0x01, 0x67, 0x41, 0x00, 0x01]
    data, sw1, sw2 = connection.transmit(SELECT_APDU)
    if sw1 != 0x90:
        raise Exception("ファイル選択失敗")
    print("証明書ファイル選択成功")

def read_certificate(connection):
    # バイナリ読み出し（例: 256バイトずつ読む）
    certificate_bytes = bytearray()
    offset = 0
    while True:
        READ_BINARY = [0x00, 0xB0, (offset >> 8) & 0xFF, offset & 0xFF, 0xFF]
        chunk, sw1, sw2 = connection.transmit(READ_BINARY)
        if sw1 != 0x90:
            break
        certificate_bytes.extend(chunk)
        if len(chunk) < 0xFF:
            break
        offset += len(chunk)
    return bytes(certificate_bytes)

def extract_birthdate_from_cert(cert_der):
    cert = x509.load_der_x509_certificate(cert_der, default_backend())
    subject = cert.subject
    for attr in subject:
        if attr.oid.dotted_string == '1.2.392.200119.4.403.1.3':  # 生年月日 OID
            birthdate_str = attr.value  # 'YYYYMMDD'
            return datetime.strptime(birthdate_str, "%Y%m%d")
    return None

def is_age_over(birthdate, age):
    today = datetime.today()
    return (today.year - birthdate.year) - ((today.month, today.day) < (birthdate.month, birthdate.day)) >= age

def main():
    connection = connect_card()
    select_file(connection)
    cert_bytes = read_certificate(connection())
    birthdate = extract_birthdate_from_cert(cert_bytes)
    
    if birthdate:
        if is_age_over(birthdate, 20):
            print("✅ 20歳以上です。購入可能。")
        else:
            print("❌ 20歳未満です。年齢制限商品は購入できません。")
    else:
        print("生年月日の取得に失敗しました。")

if __name__ == "__main__":
    main()
