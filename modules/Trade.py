#!/usr/bin/env python3
# get market price and calculate
from .market_api import Market

# 交易所稅率
tax=0.85
# 距离加成,艾港是94.28%,格拉那113.85%
distance_map = [
    (0.9428,"艾港"),
    (1.1385,"格拉那")
]

level_map = [
    (50,"匠人"),
    (60,"名匠"),
    (90,"道人"),
]

def percentFormat(percent):
    return round(float(percent[:-1])*0.01,4)

def tradeAddition(level,level_num,distance):
    # 讨价还价，每级提升0.5%
    level_addition = 0.005*(level+level_num)

    #最終售價 = 原價 ╳ [1+貿易距離] ╳ [1+討價還價] × [1+沙漠buff]
    trade_addition = (1+distance)*(1+level_addition)*1.5
    return trade_addition

box_map = {
    "鋼鐵":{"鋼鐵":10},
    "青銅":{"青銅鑄塊":10},
    "黃銅":{"黃銅鑄塊":10},
    "翡翠":{"翡翠":5,"綠鑄塊":5},
    "黑曜石":{"黑曜石":5,"鎳錠":5},
    "賽林迪亞木材":{"楓樹合板":5,"松樹合板":5},
    "梅迪亞木材":{"洋槐樹合板":5,"扁柏樹合板":5},
    "卡爾佩恩木材":{"白樺樹合板":5,"冷杉樹合板":5,"杉樹合板":5},
    "荊棘木材":{"雪原杉樹合板":5,"刺樹合板":5},
}

box_price = {
    "鋼鐵":33648,
    "黃銅":56862,
    "青銅":50439,
    "翡翠":100000,
    "黑曜石":107500,
    "賽林迪亞木材":62730,
    "梅迪亞木材":77850,
    "卡爾佩恩木材":98640,
    "荊棘木材":110575,
}

# 加工材料配比，粗略計算,實際有跳階會更多
base_map = {
    "鋼鐵":{"鐵礦石":4,"煤炭":2},
    "青銅鑄塊":{"銅礦石":4,"錫礦石":4},
    "黃銅鑄塊":{"銅礦石":4,"鋅礦石":4},
    "翡翠":{"翡翠原石":4},
    "綠鑄塊":{"綠礦石":8},
    "黑曜石":{"黑曜石原石":4},
    "鎳錠":{"鎳礦石":8},
    "楓樹合板":{"楓樹原木":8},
    "松樹合板":{"松樹原木":8},
    "扁柏樹合板":{"扁柏樹原木":8},
    "洋槐樹合板":{"洋槐樹原木":8},
    "白樺樹合板":{"白樺樹原木":8},
    "冷杉樹合板":{"冷杉樹原木":8},
    "杉樹合板":{"杉樹原木":8},
    "雪原杉樹合板":{"雪原杉樹原木":8},
    "刺樹合板":{"刺樹原木":8},
}

def boxData(box,count,level,level_num,distence):
    trade_addition = tradeAddition(level,level_num,distence)
    final_price = round(box_price[box]*count*trade_addition)

    data = {
        "名稱":box,
        "數量":count,
        "貿易加成": "{}%".format(round(trade_addition*100)),
        "原價": box_price[box],
        "總價": final_price,
    }

    market_api = Market()
    price_data = market_api.priceData('TW-tw')

    total_cost = 0
    total_base_cost = 0
    item_data = {}
    for item in box_map[box]:
        item_count = box_map[box][item]*count
        item_cost = price_data[item]['BasePrice']*item_count
        base_cost = 0
        base_data = {}
        for base in base_map[item]:
            base_count = base_map[item][base]*item_count
            base_cost += price_data[base]['BasePrice']*base_count
            base_data[base] = {
                "消耗量":base_count,
                "單價":price_data[base]['BasePrice'],
                "預售":price_data[base]['Count'],
                "日交易":price_data[base]['DailyVolume'],
                "買入價":base_cost,
                "賣出價":round(base_cost*tax),
            }

        cost = price_data[item]['BasePrice']*item_count
        #加工收益
        process_income = round((cost*tax - base_cost*tax)/10**8,2)
        #加工收益(買原料)
        process_income2 = round((cost*tax - base_cost)/10**8,2)
        item_data[item] = {
            "消耗量":item_count,
            "單價":price_data[item]['BasePrice'],
            "預售":price_data[item]['Count'],
            "日交易":price_data[item]['DailyVolume'],
            "買入價":cost,
            "賣出價":round(cost*tax),
            "原料":base_data,
        }
        total_cost += cost
        total_base_cost += base_cost
    data["材料"] = item_data
    data["原料售價"] = round(total_base_cost*tax)
    data["加工利潤"] = round((total_cost-total_base_cost)*tax)
    data["裝箱利潤"] = round(final_price-total_base_cost*tax)
    data["買原料加工利潤"] = round(total_cost*tax-total_base_cost)
    data["買原料裝箱利潤"] = final_price-total_base_cost
    data["買加工品裝箱利潤"] = final_price-total_cost

    return data

if __name__ == '__main__':
    import yaml
    print(yaml.dump(boxData('荊棘木材',1,60,2,0.9428),allow_unicode=True,sort_keys=False))
    print(yaml.dump(boxData('翡翠',1,60,2,0.9428),allow_unicode=True,sort_keys=False))

