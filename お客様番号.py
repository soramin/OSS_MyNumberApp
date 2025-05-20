# 仮想的なマイナンバーカードのデータ構造
my_number_card = {
    "name": "山田 太郎",
    "my_number": "1234-5678-9012",
    "birth_date": "1990-01-01",
    "address": "東京都千代田区",
    "airline_ids": {
        "JAL": None,
        "ANA": None,
        "Delta": None
    }
}

# 航空会社の顧客番号を追加
def add_airline_ids(card, jal_id, ana_id, delta_id):
    card['airline_ids']['JAL'] = jal_id
    card['airline_ids']['ANA'] = ana_id
    card['airline_ids']['Delta'] = delta_id
    return card

# 使用例 (JAL, ANA, デルタ航空)
updated_card = add_airline_ids(my_number_card, "JAL12345678", "ANA98765432", "DL24681012")

# 結果の表示
import json
print(json.dumps(updated_card, indent=4, ensure_ascii=False))

#整形された JSON
{
    "name": "山田 太郎",
    "my_number": "1234-5678-9012",
    "birth_date": "1990-01-01",
    "address": "東京都千代田区",
    "airline_ids": {
        "JAL": "JAL12345678",
        "ANA": "ANA98765432",
        "Delta": "DL24681012"
    }
}
