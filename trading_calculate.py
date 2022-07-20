#!/usr/bin/env python3
# get market price and calculate
from market_api import Market

# 距离加成,艾港是94.28%,格拉那113.85%
distance = "94.28%"
#distance = "113.85%"

# 讨价还价，贸易名匠1开始计算，每级提升0.5%
level = 3
level_addition = 0.005*(60+level)

def percentFormat(percent):
    return round(float(percent[:-1])*0.01,4)

#最終售價 = 原價 ╳ [1+貿易距離] ╳ [1+討價還價] × [1+沙漠buff]
trading_addition = (1+percentFormat(distance))*(1+level_addition)*1.5

box_map = {
    "鋼鐵":{"鋼鐵":10},
    "青銅":{"青銅鑄塊":10},
    "黃銅":{"黃銅鑄塊":10},
    "翡翠":{"翡翠":5,"綠鑄塊":5},
    "黑曜石":{"黑曜石":5,"鎳錠":5},
    "賽林":{"楓樹合板":5,"松樹合板":5},
    "梅迪":{"洋槐樹合板":5,"扁柏樹合板":5},
    "卡佩":{"白樺樹合板":5,"冷杉樹合板":5,"杉樹合板":5},
    "荊棘":{"雪原杉樹合板":5,"刺樹合板":5},
}

box_price = {
    "鋼鐵":33648,
    "黃銅":56862,
    "青銅":50439,
    "卡佩":98640,
    "梅迪":77850,
    "賽林":62730,
    "翡翠":100000,
    "黑曜石":107500,
    "荊棘":110575,
}


def tradingIncome(count):
    market_api = Market()
    price_data = market_api.priceData('TW-tw')

    for box in box_map:
        final_price = box_price[box]*count*trading_addition
        cost = 0
        print("{:<10} {:<10} {:<10}".format("材料","預售","日交易量"))
        for item in box_map[box]:
            print("{:<10} {:<10} {:<10}".format(item,price_data[item]['BasePrice'],price_data[item]['DailyVolume']))
            cost += price_data[item]['BasePrice']*box_map[box][item]*count
        print("{}箱子{}箱收益:{}E".format(box,count,(final_price-cost)/10**8))
        print('----------------------------------------------------------------------')

if __name__ == '__main__':
    tradingIncome(10000)

