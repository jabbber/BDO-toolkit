from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask_wtf import FlaskForm
from wtforms import fields,validators

from .modules import Cook,Trade

import json
import os

if os.getenv('FLASK_ENV') == 'development':
    url_path = '/develop'
else:
    url_path = '/toolkit'

bp = Blueprint('toolkit', __name__, url_prefix=url_path)

class CookForm(FlaskForm):
    count = fields.IntegerField('目标箱数', [validators.NumberRange(1,50000,"差不多得了啊，只能输入%(min)-%(max)"),],default=200)
    skill = fields.IntegerField('熟练度', [validators.NumberRange(0,2000,"差不多得了啊，只能输入%(min)-%(max)"),],default=1000)
    tribute_skill = fields.IntegerField('纳贡熟练度', [validators.NumberRange(0,2000,"差不多得了啊，只能输入%(min)-%(max)"),],default=1200)

@bp.route('/', methods=('GET', 'POST'))
def cook():
    form = CookForm()
    data_title = ["納貢收入","成本","總利潤","單箱利潤","耗時(分)","魔女湯","買入裝箱利潤","成品登記數量","成品日交易","特製登記數量","特製日交易"]
    if request.method == 'POST':
        if form.validate_on_submit():
            data = {}
            box_data = {}
            for target in Cook.recipe:
                if Cook.recipe[target].get('support'):
                    box_data[target] = Cook.boxData(target,form.count.data,form.skill.data,form.tribute_skill.data)
                    data[target] = {title:box_data[target].get(title,'') for title in data_title}
        else:
            redirect(url_for('toolkit.cook'))

    if request.method == 'GET':
        formdata = session.get('formdata', None)
        if not formdata:
            redirect(url_for('toolkit.cook'))
        if formdata:
            if not form.validate():
                redirect(url_for('toolkit.cook'))
        data = {}
        for target in Cook.recipe:
            if Cook.recipe[target].get('support'):
                data[target] = {title:"" for title in data_title}
    return render_template('cook/result.html', form=form,data=data,data_title=data_title)

@bp.route('/cook/<name>',methods=('GET','POST'))
def cookDetail(name):
    if Cook.recipe.get(name,{}).get('support'):
        pass
    else:
        redirect(url_for('toolkit.cook'))

    form = CookForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            pass
        else:
            redirect(url_for('toolkit.cook'))
    if request.method == 'GET':
        formdata = session.get('formdata', None)
        if not formdata:
            redirect(url_for('toolkit.cook'))
        if formdata:
            form.validate()
    box_data = Cook.boxData(name,form.count.data,form.skill.data,form.tribute_skill.data)
    data = cookTable(box_data["生產明細"])
    data_title = ["料理","材料","數量","單價","價格","登記數量","日交易"]

    total = []
    total_title = ["需求量","單價","價格","登記數量","日交易"]
    for item in box_data['價格']:
        if item in Cook.npc_items:
            item_type = 'NPC'
        elif item == '總計':
            item_type = ''
        else:
            item_type = '交易所'
        value_list = [item_type,item,]
        for value in total_title:
            value_list.append(box_data[value].get(item,''))

        total.append(value_list)

    summary = {}
    for item in box_data:
        if type(box_data[item]) in (str,int,float):
            summary[item] = box_data[item]

    return render_template('cook/detail.html', form=form,data=data,data_title=data_title,name=name,total=total,total_title=total_title,summary=summary)

def cookTable(data):
    import string
    table = []
    n = 0
    for line in data:
        base_info = "{}:{} 材料份數:{} 耗时(分):{} 產物 普通({})".format(string.ascii_lowercase[n],line["料理"],line["料理次數"],line['耗時(分)'],line['普通'])
        n += 1
        if "特製" in line:
            base_info += " 特製({})".format(line["特製"])
        if "裝箱數" in line:
            base_info += " 裝箱數({})".format(line["裝箱數"])
        if line["上級料理"]:
            base_info += "上級料理: "+line["上級料理"]
        if 'buy' in Cook.recipe[line["料理"]]:
            base_info += " (成本用成品計算，材料未計算) 建議: {}".format(Cook.recipe[line["料理"]]['buy'])
        for item in line['材料']:
            row = [base_info,item]
            for key in ("數量","單價","價格","登記數量","日交易"):
                row.append(line['材料'][item].get(key,''))
        
            table.append(row)
    return table

class TradeForm(FlaskForm):
    count = fields.IntegerField('目标箱数', [validators.NumberRange(1,10000,"差不多得了啊，只能输入%(min)-%(max)"),],default=1)
    level = fields.SelectField('貿易等級', choices=Trade.level_map,coerce=int,default=60)
    level_num = fields.IntegerField('等級數', [validators.NumberRange(1,50,"差不多得了啊，只能输入%(min)-%(max)"),],default=1)
    location = fields.SelectField('裝箱地', choices=Trade.distance_map,coerce=float,default=0.9428)

@bp.route('/trade', methods=('GET', 'POST'))
def trade():
    form = TradeForm()
    data_title = ["數量","原價","總價","原料售價","加工利潤","裝箱利潤","買原料加工利潤","買原料裝箱利潤","買加工品裝箱利潤"]
    if request.method == 'POST':
        if form.validate_on_submit():
            data = {}
            box_data = {}
            for box in Trade.box_map:
                box_data[box] = Trade.boxData(box,form.count.data,form.level.data,form.level_num.data,form.location.data)
                data[box] = {title:box_data[box].get(title,'') for title in data_title}
        else:
            redirect(url_for('toolkit.trade'))

    if request.method == 'GET':
        formdata = session.get('formdata', None)
        if not formdata:
            redirect(url_for('toolkit.trade'))
        if formdata:
            if not form.validate():
                redirect(url_for('toolkit.trade'))
        data = {}
        for box in Trade.box_map:
            data[box] = {title:"" for title in data_title}
    return render_template('trade/result.html', form=form,data=data,data_title=data_title)

@bp.route('/trade/<name>',methods=('GET','POST'))
def tradeDetail(name):
    if name in Trade.box_map:
        pass
    else:
        redirect(url_for('toolkit.trade'))

    form = TradeForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            pass
        else:
            redirect(url_for('toolkit.trade'))
    if request.method == 'GET':
        formdata = session.get('formdata', None)
        if not formdata:
            redirect(url_for('toolkit.trade'))
        if formdata:
            form.validate()
    box_data = Trade.boxData(name,form.count.data,form.level.data,form.level_num.data,form.location.data)

    total = []
    total_title = ["消耗量","單價","預售","日交易","買入價","賣出價"]
    for item in box_data['材料']:
        item_type = '加工品'
        value_list = [item_type,item,]
        for value in total_title:
            value_list.append(box_data['材料'][item].get(value,''))
        total.append(value_list)
        for base in box_data['材料'][item]['原料']:
            item_type = '原料'
            value_list = [item_type,base,]
            for value in total_title:
                value_list.append(box_data['材料'][item]['原料'][base].get(value,''))
            total.append(value_list)

    summary = {}
    for item in box_data:
        if type(box_data[item]) in (str,int,float):
            summary[item] = box_data[item]

    return render_template('trade/detail.html', form=form,total=total,total_title=total_title,name=name,summary=summary)

