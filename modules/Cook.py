#!/usr/bin/env python3
import math
import pathlib
import os.path
import yaml
#import yaml
# get market price and calculate
from .market_api import Market

def readRecipe():
    current_dir = pathlib.Path(__file__).parent.resolve()
    recipe_meta = os.path.join(current_dir,'recipe.yaml')
    with open(recipe_meta, "r") as stream:
        recipe_data = yaml.safe_load(stream)
    return recipe_data

recipe=readRecipe()

box_price={
    '專家': 120000,
    '名匠': 220000,
    '道人': 320000,
}

npc_items='''
鹽 20
砂糖 20
發酵劑 20
食用油 20
海鹽 200
黑糖 200
橄欖油 40
油炸用油 40
料理用紅酒 40
基本醬料 40
料理用飲用水 30
草莓 700
甜椒 850
純水 5000
'''

cooking_skillful='''
2000	61.15%	61.15%	19.36%	100.00%	144.96%
1950	58.37%	58.37%	18.49%	99.50%	141.37%
1900	55.65%	55.65%	17.64%	90.44%	137.83%
1850	53.00%	53.00%	16.81%	86.30%	134.33%
1800	50.41%	50.41%	16.00%	82.26%	130.87%
1750	47.89%	47.89%	15.21%	78.32%	127.46%
1700	45.43%	45.43%	14.44%	74.48%	124.10%
1650	43.03%	43.03%	13.69%	70.73%	120.78%
1600	40.70%	40.70%	12.96%	67.08%	117.51%
1550	38.44%	38.44%	12.25%	63.52%	114.28%
1500	36.24%	36.24%	11.56%	60.06%	111.09%
1450	34.11%	34.11%	10.89%	56.70%	107.95%
1400	32.04%	32.04%	10.24%	53.44%	104.86%
1350	30.03%	30.03%	9.61%	50.27%	101.81%
1300	28.09%	28.09%	9.00%	47.20%	98.80%
1250	26.21%	26.21%	8.41%	44.22%	95.84%
1200	24.40%	24.40%	7.84%	41.34%	92.93%
1150	22.66%	22.66%	7.29%	39.44%	86.12%
1100	20.98%	20.98%	6.76%	37.58%	79.57%
1050	19.36%	19.36%	6.25%	35.76%	73.27%
1000	17.81%	17.81%	5.76%	33.99%	67.24%
950	16.32%	16.32%	5.29%	32.26%	61.47%
900	14.90%	14.90%	4.84%	30.58%	55.95%
850	13.54%	13.54%	4.41%	28.94%	50.69%
800	12.25%	12.25%	4.00%	27.56%	45.70%
750	11.02%	11.02%	3.61%	26.21%	40.96%
700	9.86%	9.86%	3.24%	24.90%	36.48%
650	8.76%	8.76%	2.89%	23.62%	32.26%
600	7.73%	7.73%	2.56%	22.37%	28.30%
550	6.76%	6.76%	2.25%	21.16%	24.60%
500	5.86%	5.86%	1.96%	19.98%	21.16%
450	5.02%	5.02%	1.69%	18.84%	17.98%
400	4.24%	4.24%	1.44%	17.72%	15.05%
350	3.53%	3.53%	1.21%	16.65%	12.39%
300	2.89%	2.89%	1.00%	15.60%	9.99%
250	2.31%	2.31%	0.81%	14.59%	7.84%
200	1.80%	1.80%	0.64%	13.62%	5.95%
150	1.35%	1.35%	0.49%	12.67%	4.33%
100	0.96%	0.96%	0.36%	11.76%	2.96%
50	0.64%	0.64%	0.25%	10.89%	1.85%
0	0%	0%	0%	0%	0%
'''

def percentFormat(percent):
    return round(float(percent[:-1])*0.01,4)

skill_addition_map = {}
for line in cooking_skillful.split('\n'):
    if not line:
        continue
    items = line.split('\t')
    skill_addition_map[int(items[0])] = {
        '產品數量增加': percentFormat(items[1]),
        '以最大數量獲得成品的幾率': percentFormat(items[2]),
        '獲得特製料理幾率增加': percentFormat(items[3]),
        '發動大量料理幾率': percentFormat(items[4]),
        '皇室納貢增加額外金額': percentFormat(items[5]),
        }

def productivity(skill_point,max_product):
    # max_product為單次最大產出,適用於有特製的所有料理,一般為4，特製2
    skill_point = int(skill_point/50)*50
    skill_addition = skill_addition_map[skill_point]
    #原始产出期望,1~max_product数列求和再除以max_product
    original_product = max_product*(1+max_product)/2/max_product
    #最终产出期望,按"以最大數量獲得成品的幾率"为概率必定产出最大数量,剩余的概率套用原始产出期望
    product = original_product*(1-skill_addition['以最大數量獲得成品的幾率']) + max_product*skill_addition['以最大數量獲得成品的幾率']
    return product

def productivity5(skill_point):
    # 無特製的料理，單次產出1-5,但是原始產出期望為4，很費解，目前只有寵物飼料需要此公式
    skill_point = int(skill_point/50)*50
    skill_addition = skill_addition_map[skill_point]
    #原始产出期望,1~max_product数列求和再除以max_product
    original_product = 4
    #最终产出期望,按"以最大數量獲得成品的幾率"为概率必定产出最大数量,剩余的概率套用原始产出期望
    product = original_product*(1-skill_addition['以最大數量獲得成品的幾率']) + 5*(skill_addition['以最大數量獲得成品的幾率'])
    return round(product,4)

def special_productivity(skill_point):
    #特制产出1~2,套用普通产出公式再乘以特制触发概率,基础概率0.2+熟练度概率up
    skill_point = int(skill_point/50)*50
    skill_addition = skill_addition_map[skill_point]
    special_product = (0.2+skill_addition['獲得特製料理幾率增加']) * productivity(skill_point,2)
    return round(special_product,4)

# 工具耐久消耗
def durability(count,skill):
    #每點耐久料理次數，受大量料理影響，
    #(1-發動大量料理機率)*1+(發動大量料理機率*10)
    #另外料理耗時就等於耐久度消耗*料理秒數
    skill_point = int(skill/50)*50
    skill_addition = skill_addition_map[skill_point]
    return count/((1-skill_addition["發動大量料理幾率"])*1+skill_addition["發動大量料理幾率"]*10)

# 魔女湯
def soup(count):
    #料理次數*0.0236，大量料理也10倍獲得
    return 0.0236*count

npc_item_price = {}
for line in npc_items.split('\n'):
    if not line:
        continue
    key,value = line.split(' ')
    npc_item_price[key] = int(value)

def calMaterial(target,count,skill,tribute_skill,parent=""):
    # 產物數量
    product=productivity(skill,4)
    product5=productivity5(skill)
    special=special_productivity(skill)

    market_api = Market()
    price_data = market_api.priceData('TW-tw')
    material = recipe[target]['material']
    output = {}
    result = []
    for item in material:
        #單次材料數量
        item_count = count*material[item]
        #npc材料
        if item in npc_item_price:
            item_price = npc_item_price[item]
        else:
            item_price = price_data[item]['BasePrice']
        output[item] = {
            "數量":item_count,
            "單價":item_price,
            "價格":item_price*item_count,
        }
        if not item in npc_item_price:
            output[item]["登記數量"] = price_data[item]['Count']
            output[item]["日交易"] = price_data[item]['DailyVolume']

    base_info = {
        "料理":target,
        "料理次數":count,
        "耐久消耗":round(durability(count,skill),2),
        "上級料理":parent,
        "普通": round(product*count,2),
    }
    base_info['耗時(分)'] = round(base_info['耐久消耗']*1.2/60,1)
    if 'special' in recipe[target]:
        base_info["特製"] = round(special*count,2)
    ""
    if 'box' in recipe[target]:
        box,food_count = recipe[target]['box']
        box_count = 0
        # 只有第0層普通產物可以裝箱，其他普通產物需要當材料
        if not parent:
            box_count = base_info['普通']/food_count
        # 次級料理如果上級需要1個，且定義了裝箱信息，則進行裝箱，不用來料理
        price = base_info['普通']*price_data[target]['BasePrice']
        if 'special' in recipe[target]:
            if not parent:
                box_count += base_info['特製']*3/food_count
            else:
                if recipe[parent]['material'][target] == 1:
                    box_count += base_info['特製']*3/food_count
            price += base_info['特製']*price_data[recipe[target]['special']]['BasePrice']
        if box_count > 0:
            base_info['裝箱數'] = round(box_count,2)
            base_info['等級'] = box

        # 納貢加成
        skill_point = int(tribute_skill/50)*50
        skill_addition = skill_addition_map[skill_point]
        box_addition = 2.5+skill_addition["皇室納貢增加額外金額"]

        base_info["納貢收入"] = round(box_count*box_price[box]*box_addition)
        base_info["上架收入"] = round(0.85*price)
    base_info["材料"] = output

    result.append(base_info)
    for item in material:
        #次級料理
        if item in recipe:
            # 反推需要多少次料理
            cook_rate = product/material[item]
            if ( not 'box' in recipe[item] or material[item] > 1 ) and 'special' in recipe[item]:
                # 特製可以代替3普通做材料,所以消耗量是除以3取整
                cook_rate += special/math.ceil(material[item]/3)
            cook_count = round(count/cook_rate)
            
            #迭代計算
            result += calMaterial(item,cook_count,skill,tribute_skill,parent=target)

    return result

def boxData(target,count,skill,tribute_skill=0):
    market_api = Market()
    price_data = market_api.priceData('TW-tw')

    if not tribute_skill:
        tribute_skill=skill

    # 納貢價格
    skill_point = int(tribute_skill/50)*50
    skill_addition = skill_addition_map[skill_point]
    box_addition = 2.5+skill_addition["皇室納貢增加額外金額"]
    # 產物數量
    product=productivity(skill,4)
    product5=productivity5(skill)
    special=special_productivity(skill)

    # 單次料理產量
    product_count = product
    if 'special'in recipe[target]:
        product_count = product+special*3

    # 反推料理次數
    box,food_count = recipe[target]['box']
    total_price = round(box_price[box]*box_addition*count,2)
    cook_count = round(count*food_count/product_count)

    data = calMaterial(target,cook_count,skill,tribute_skill)

    box_data = {
        "料理": target,
        "熟練度": skill,
        "納貢熟練度": tribute_skill,
        "目標箱數": count,
        "實際箱數": '|'.join(["{}({})".format(key,value) for key,value in counter(data,'裝箱數').items()]),
        "納貢收入": counter(data,'納貢收入')['總計'],
        "上架收入": counter(data,'上架收入')['總計'],
        "成本": counter(data,'價格',sub=True)['總計'],
    }
    box_data["納貢利潤"] = round((box_data['納貢收入'] - box_data['成本']))
    box_data["上架利潤"] = round((box_data['上架收入'] - box_data['成本']))
    box_data["單箱利潤"] = round((box_data['納貢收入'] - box_data['成本'])/count)
    buy_price = price_data[target]['BasePrice']*food_count
    box_data["成品登記數量"] = price_data[target]['Count']
    box_data["成品日交易"] = price_data[target]['DailyVolume']
    if 'special' in recipe[target]:
        buy_price = price_data[recipe[target]['special']]['BasePrice']*food_count/3
        box_data["特製登記數量"] = price_data[recipe[target]['special']]['Count']
        box_data["特製日交易"] = price_data[recipe[target]['special']]['DailyVolume']
    box_data["買入裝箱利潤"] = round((box_price[box]*box_addition-buy_price)*count)
    final_cook_count = counter(data,'料理次數')["總計"]
    box_data['消耗耐久'] = round(durability(final_cook_count,skill),2)
    box_data['耗時(分)'] = round(box_data['消耗耐久']*1.2/60)
    box_data['魔女湯'] = round(soup(final_cook_count),2)
    box_data["需求量"] = counter(data,'數量',total=False,sub=True,sub_total=True)
    box_data["價格"] = counter(data,'價格',sub=True,sub_total=True)
    box_data["單價"] = counter(data,'單價',total=False,sub=True,sub_total=False)
    box_data["登記數量"] = counter(data,'登記數量',total=False,sub=True,sub_total=False)
    box_data["日交易"] = counter(data,'日交易',total=False,sub=True,sub_total=False)
    box_data["生產明細"] = data

    return box_data

def counter(data,key,sub=False,skip_child=True,total=True,sub_total=True):
    # skip_child 不累計中間產物
    # sub_total 不累計數量
    out = {}
    for line in data:
        if not sub and key in line:
            out[line['料理']] = line[key]
        else:
            for item in line["材料"]:
                if skip_child and item in recipe:
                    # 標記為buy的料理做為材料直接買
                    if not 'buy' in recipe[item]:
                        continue
                if key in line["材料"][item] and not 'buy' in recipe[line["料理"]]:
                    value = line["材料"][item][key]
                    if not item in out:
                        out[item] = value
                    elif sub_total:
                        out[item] += value
    if total:
        total_count = 0
        for i in out:
            total_count += out[i]
        out['總計'] = round(total_count,2)
    return out

if __name__ == '__main__':
    print(yaml.dump(boxData("奧迪爾利塔套餐",1000,1200,1400),allow_unicode=True,sort_keys=False))
