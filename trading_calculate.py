#!/usr/bin/env python3
# get market price and calculate
from market_api import Market

# 交易所稅率
tax=0.85
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

def tradingIncome(count):
    market_api = Market()
    price_data = market_api.priceData('TW-tw')

    for box in box_map:
        print("{}箱子{}箱:".format(box,count))
        final_price = box_price[box]*count*trading_addition
        total_cost = 0
        total_base_cost = 0
        print("{:\u3000<7} {:\u3000<5} {:\u3000<5} {:\u3000<5} {:\u3000<5} {}".format("材料","消耗量","預售","日交易量","賣交易所","加工收益(自采/買原料)"))
        for item in box_map[box]:
            item_count = box_map[box][item]*count
            item_cost = price_data[item]['BasePrice']*item_count
            base_cost = 0
            for base in base_map[item]:
                base_count = base_map[item][base]*item_count
                base_cost += price_data[base]['BasePrice']*base_count
                print("{:\u3000<7} {:<10} {:<10} {:<10} {:<10}".format(base,base_count,price_data[base]['Count'],price_data[base]['DailyVolume'],round(base_cost*tax/10**8,2)))

            cost = price_data[item]['BasePrice']*item_count
            #加工收益
            process_income = round((cost*tax - base_cost*tax)/10**8,2)
            #加工收益(買原料)
            process_income2 = round((cost*tax - base_cost)/10**8,2)
            print("{:\u3000<7} {:<10} {:<10} {:<10} {:<10} {}/{}".format(item,item_count,price_data[item]['Count'],price_data[item]['DailyVolume'],round(cost*tax/10**8,2),process_income,process_income2))
            total_cost += cost
            total_base_cost += base_cost
        print('------------------------')
        print("裝箱收益(E):")
        print("交易所買最終材料: ",end='')
        print(round((final_price-total_cost)/10**8,2))
        print("自產:             ",end='')
        print(round((final_price-total_cost*tax)/10**8,2))
        print('------------------------')
        print("總價(E): ",end='')
        print(round(final_price/10**8,2))
        print("收益構成(採集/加工/裝箱): ",end='')
        print(round(total_base_cost*tax/final_price*100),end='%/')
        print(round((total_cost-total_base_cost)*tax/final_price*100),end='%/')
        print(round((final_price-total_cost*tax)/final_price*100),end='%\n')
        print()

if __name__ == '__main__':
    tradingIncome(10000)

