#!/usr/bin/env python3
# get market price and calculate
from .market_api import Market

# 交易所稅率
tax=0.85
# 距离加成,艾港是94.28%,格拉那113.85%
# 改版后，卖到晨曦最优，距离加成重新计算
distance_map = [
    (1.153,"貝爾利亞村莊"),
    (1.215,"海地爾"),
    (1.406,"爾提諾巴"),
    (1.5,"首都瓦倫西亞"),
    (1.451,"艾亦爾村莊"),
    (1.355,"德本克倫"),
    (1.418,"奧德羅西亞"),
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
    #trade_addition = (1+distance)*(1+level_addition)*1.5
    #2023/3/29 update取消沙漠buff，基础价格改为2倍
    trade_addition = (1+distance)*(1+level_addition)
    return trade_addition

box_map = {
    "鋼鐵鑄塊箱子":{"鋼鐵":10,"黑石粉末":1},
    "青銅鑄塊箱子":{"青銅鑄塊":10,"黑石粉末":1},
    "黃銅鑄塊箱子":{"黃銅鑄塊":10,"黑石粉末":1},
    "釩鑄塊箱子":{"釩鑄塊":10,"黑石粉末":1},
    "鈦鑄塊箱子":{"鈦鑄塊":10,"黑石粉末":1},
    "雪原翡翠箱子":{"翡翠":5,"綠鑄塊":5,"黑石粉末":1},
    "雪原黑曜石箱子":{"黑曜石":5,"鎳錠":5,"黑石粉末":1},
    "貴金屬箱子":{"金鑄塊":5,"銀鑄塊":5,"白金鑄塊":5,"黑石粉末":1},
    "深銀鑄塊箱子":{"深銀鑄塊":10,"黑石粉末":1},
    "賽林迪亞木材":{"楓樹合板":5,"松樹合板":5,"黑石粉末":1},
    "梅迪亞木材":{"洋槐樹合板":5,"扁柏樹合板":5,"黑石粉末":1},
    "卡爾佩恩木材":{"白樺樹合板":5,"冷杉樹合板":5,"杉樹合板":5,"黑石粉末":1},
    "荊棘木材":{"雪原杉樹合板":5,"刺樹合板":5,"黑石粉末":1},
    "雪原木材":{"雪原杉樹合板":5,"側柏合板":5,"黑石粉末":1},
}

box_price = {
    "鋼鐵鑄塊箱子":33648*2,
    "青銅鑄塊箱子":50439*2,
    "黃銅鑄塊箱子":56862*2,
    "釩鑄塊箱子":95097*2,
    "鈦鑄塊箱子":96198*2,
    "雪原翡翠箱子":100000*2,
    "雪原黑曜石箱子":107500*2,
    "貴金屬箱子":340254*2,
    "深銀鑄塊箱子":384866*2,
    "賽林迪亞木材":62730*2,
    "梅迪亞木材":77850*2,
    "卡爾佩恩木材":98640*2,
    "荊棘木材":100575*2,
    "雪原木材":100575*2,
}

# 加工材料配比，粗略計算,實際有跳階會更多
base_map = {
    "鋼鐵":[{"鐵礦石":4,"煤炭":2,},{"熔化的鐵碎片":2,"煤炭":2,}],
    "青銅鑄塊":[{"銅礦石":4,"錫礦石":4},{"熔化的銅塊":2,"熔化的錫塊":2}],
    "黃銅鑄塊":[{"銅礦石":4,"鋅礦石":4},{"熔化的銅塊":2,"熔化的鋅塊":2}],
    "釩鑄塊":[{"釩礦石":7.4},{"熔化的釩碎片":4}],
    "鈦鑄塊":[{"鈦礦石":7.4},{"熔化的鈦碎片":4}],
    "金鑄塊":[{"金礦石":7.4},{"熔化的黃金碎片":4}],
    "銀鑄塊":[{"銀礦石":7.4},{"熔化的銀塊":4}],
    "白金鑄塊":[{"白金礦石":7.4},{"熔化的白金碎片":4}],
    "深銀鑄塊":[{"深銀":7.4},{"熔化的深銀碎片":4}],
    "綠鑄塊":[{"綠礦石":7.4},{"熔化的綠碎片":4}],
    "翡翠":[{"翡翠原石":2},{"翡翠原石":2}],
    "黑曜石":[{"黑曜石原石":2},{"黑曜石原石":2}],
    "鎳錠":[{"鎳礦石":7.4},{"熔化的鎳碎片":4}],
    "楓樹合板":[{"楓樹原木":7.4},{"楓樹木板":4}],
    "松樹合板":[{"松樹原木":7.4},{"松樹木板":4}],
    "扁柏樹合板":[{"扁柏樹原木":7.4},{"扁柏樹木板":4}],
    "洋槐樹合板":[{"洋槐樹原木":7.4},{"洋槐樹木板":4}],
    "白樺樹合板":[{"白樺樹原木":7.4},{"白樺樹木板":4}],
    "冷杉樹合板":[{"冷杉樹原木":7.4},{"冷杉樹木板":4}],
    "杉樹合板":[{"杉樹原木":7.4},{"杉樹木板":4}],
    "雪原杉樹合板":[{"雪原杉樹原木":7.4},{"雪原杉樹木板":4}],
    "刺樹合板":[{"刺樹原木":7.4},{"刺樹木板":4}],
    "側柏合板":[{"側柏原木":7.4},{"側柏木板":4}],
    "黑石粉末":[{"黑石(武器)":0.0125},{"黑石(武器)":0.0125}],
}

def boxData(box,count,level,level_num,distence):
    trade_addition = tradeAddition(level,level_num,distence)
    final_price = round(box_price[box]*count*trade_addition)

    data = {
        "名稱":box,
        "數量":count,
        "貿易加成": "{}%".format(round(trade_addition*100)),
        "箱價": box_price[box],
        "瓦倫售價": final_price,
    }

    market_api = Market()
    price_data = market_api.priceData('TW-tw')

    total_cost = 0
    total_base_cost = 0
    total_semi_cost = 0
    item_data = {}
    for item in box_map[box]:
        item_count = box_map[box][item]*count
        item_cost = price_data[item]['BasePrice']*item_count

        # c初級原料
        base_cost = 0
        base_data = {}
        for base in base_map[item][0]:
            base_count = base_map[item][0][base]*item_count
            base_cost += price_data[base]['BasePrice']*base_count
            base_data[base] = {
                "消耗量":base_count,
                "單價":price_data[base]['BasePrice'],
                "預售":price_data[base]['Count'],
                "日交易":price_data[base]['DailyVolume'],
                "買入價":base_cost,
                "賣出價":round(base_cost*tax),
            }

        # 二級原料
        semi_cost = 0
        semi_data = {}
        for semi in base_map[item][1]:
            semi_count = base_map[item][1][semi]*item_count
            semi_cost += price_data[semi]['BasePrice']*semi_count
            semi_data[semi] = {
                "消耗量":semi_count,
                "單價":price_data[semi]['BasePrice'],
                "預售":price_data[semi]['Count'],
                "日交易":price_data[semi]['DailyVolume'],
                "買入價":semi_cost,
                "賣出價":round(semi_cost*tax),
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
            "半成品": semi_data,
        }
        total_cost += cost
        total_base_cost += base_cost
        total_semi_cost += semi_cost
    data["成品"] = item_data
    data["原料售價"] = round(total_base_cost*tax)
    data["加工利潤"] = round((total_cost-total_base_cost)*tax)
    data["裝箱利潤"] = round(final_price-total_base_cost*tax)
    data["買原料加工"] = round(total_cost*tax-total_base_cost)
    data["買原料裝箱"] = final_price-total_base_cost
    data["買半成品裝箱"] = final_price-total_semi_cost
    data["買成品裝箱"] = final_price-total_cost

    return data

if __name__ == '__main__':
    import yaml
    print(yaml.dump(boxData('荊棘木材',1,60,2,0.9428),allow_unicode=True,sort_keys=False))
    print(yaml.dump(boxData('翡翠',1,60,2,0.9428),allow_unicode=True,sort_keys=False))

