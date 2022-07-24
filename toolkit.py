from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask_wtf import FlaskForm
from wtforms import fields,validators

from .modules import Cook

import json
import os

if os.getenv('FLASK_ENV') == 'development':
    url_path = '/develop'
else:
    url_path = '/toolkit'

bp = Blueprint('toolkit', __name__, url_prefix=url_path)

class CookForm(FlaskForm):
    count = fields.IntegerField('目标箱数', [validators.NumberRange(1,10000,"差不多得了啊，只能输入%(min)-%(max)"),],default=200)
    skill = fields.IntegerField('熟练度', [validators.NumberRange(0,2000,"差不多得了啊，只能输入%(min)-%(max)"),],default=1000)
    tribute_skill = fields.IntegerField('纳贡熟练度', [validators.NumberRange(0,2000,"差不多得了啊，只能输入%(min)-%(max)"),],default=1200)

@bp.route('/', methods=('GET', 'POST'))
def cook():
    form = CookForm()
    data_title = ["納貢收入","成本","總利潤","單箱利潤","耗時(分)","買入裝箱利潤","魔女湯"]
    if request.method == 'POST':
        if form.validate_on_submit():
            data = {}
            box_data = {}
            for target in Cook.SUPPORTS:
                box_data[target] = Cook.boxData(target,form.count.data,form.skill.data,form.tribute_skill.data)
                data[target] = {title:box_data[target][title] for title in data_title}
        else:
            redirect(url_for('toolkit.cookSubmit'))

    if request.method == 'GET':
        formdata = session.get('formdata', None)
        if not formdata:
            redirect(url_for('toolkit.cookSubmit'))
        if formdata:
            form.validate()
        data = {}
        for target in Cook.SUPPORTS:
            data[target] = {title:"" for title in data_title}
    return render_template('cook/result.html', form=form,data=data,data_title=data_title)

@bp.route('/cook/submit', methods=('GET', 'POST'))
def cookSubmit():
    form = CookForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            redirect(url_for('toolkit.cook'))

    return render_template('cook/base.html', form=form)

@bp.route('/cook/<name>',methods=('GET','POST'))
def cookDetail(name):
    if name in Cook.SUPPORTS:
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
    data_title = ["數量","料理次數","單價","價格","普通","特製","名匠箱","納貢收入"]
    data = cookTable(name,box_data["生產明細"]['材料'],data_title)

    total = []
    for item in box_data['材料']:
        total.append([item,box_data["材料"][item],box_data['材料單價'][item],box_data['材料成本'][item],])

    summary = {}
    for item in box_data:
        if type(box_data[item]) != dict:
            summary[item] = box_data[item]

    return render_template('cook/detail.html', form=form,data=data,data_title=data_title,name=name,total=total,summary=summary)

def cookTable(cook,data,columes):
    table = []
    for item in data:
        child_cook = None
        if '材料' in data[item]:
            child_cook = item
            child_data = data[item].pop('材料')
        row = [cook,item]
        for key in columes:
            row.append(data[item].get(key,''))
        table.append(row)
        if child_cook:
            child_table = cookTable(child_cook,child_data,columes)
            table += child_table
    return table
