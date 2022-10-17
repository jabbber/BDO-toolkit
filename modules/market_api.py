# market api by https://docs.google.com/spreadsheets/d/1HJpWrM05pDmreys8pmg0VuV0e5ZDJ0ePp_mXI-hGsJc/
import time
import pathlib
import os.path
from urllib.request import urlopen

regions='''
CNA-us	1QzB2AvZQXXkgc1CInu07XFxCx0oHBUFkFhEunYBvcEw
NA-de	1O7WfmIKezbSrIyWYewiqM_WnhrzGZlT_Z0lnLbY0so8
EU-de	1j1fIyV_Gzn6iryAVzKwobk5pm8eLGBy8BGvZro6ja6Y
EU-es	1hMJOyddJKVGbyBjUUwGWWGwWp-0hn452p6eRgLRDTj4
KR-kr	1N4x4hfihUSoe9ETA8fn0dISRSyf2PQvDYtxEtv3F7Qg
NA-es	1XH4oRQeTtecHBGYd87RmgMCZUZhCoq3AdC20akEgf38
CEU-us	1VKMOsY2N2MYba-3ufidw5lPlbGb_1mXszA0KZ09nM9s
SA-es	1BqU9WpfmensP8fgKV4Ji-a7cZAO8pcVhfsQqkysEUms
TH-th	14vHOAsIj2kQfcsPsfQDYVspp38KFP_2dwFjrrapqQrU
RU-us	18W68acOUsF7R09152mpJtqdnZSVhtj83k1v84t1tF0A
NA-us	1NsGi5c648KgnCyLdYWvtfkr36zjXK6FdBFxMjVQ_-9I
SEA-us	1MImPpNxX47JfblbJVWatItMNYK0U0QtPM-g-Xl3z2gA
TW-tw	1SACVeQqcIecs4kPwPhd2x0nJy54BCAprf2YA_xnaLgA
JP-us	1M256U1m3u3c6JC6iVtbpkdS-j4Dqj17U_uGBxc0I4TI
RU-ru	1ox0o-r9Ybff6UZk_4N4-Lh23m-NQvZ3aKvGCBWWbS8o
JP-jp	1yHXcMWUC-797E50Lob-VUsyBNusC9ccbxzgt88qJLDs
TH-us	1PrbdGNuP812PZQaEW6seFvygzzI3zO5PlnNvJemqg2s
EU-us	1q50gm4O8Vx6qfXEOmZ7xOgSZ_h70oExmtagTZM1TvUk
EU-fr	1LqIi0RAm5pAtF66HTSNhTp5LRX5bPo_cc2sKarzg9Vw
CEU-de	1dBwNNUa4hA8aFNNb5DG3FKUGn4heiVg8C-98A5lFbWs
KR-us	1wLh6u4NwKXn_RZjoNdpKnGDrzh0fOgWJbojmLFVCny0
MENA-us	1EFP3DLWPq76bVD6Z9z8-yoyjtJSlpOwbd7XHPd3YgqM
SA-us	1hBBWZkRRPdGiUWZWp1hSTPnH2xl37G39COW3lUekW2k
TW-us	1tPVsHE3mBawHp3tlzbj82nUq00gPto9Selc_Z3pJlY8
SA-pt	1p9SiQEGn8fuK7314ujdYasejjT4ponxgsUdf9SgYmdg
MENA-tr	1imwi55_O92okrpnkdlrThVuHa4J_Kth0kepc6v3O8iA
SA-sp	18vP9JqQXoWu27bXfcLg-z-rKpBw-s6yj1OE292rkgAA
'''

class Market:
    def __init__(self):
        region_map={}
        for line in regions.split('\n'):
            if not line:
                continue
            key,value = line.split('\t')
            region_map[key] = value
        self.region_map = region_map
    def priceData(self,region):
        url = "https://docs.google.com/spreadsheets/d/{region_id}/export?format=tsv".format(region_id=self.region_map[region])
        current_dir = pathlib.Path(__file__).parent.resolve()
        cache = 1800
        cache_name = 'market_'+region+'.tsv.tmp'
        cache_file = os.path.join(current_dir,cache_name)
        out = ''
        if os.path.isfile(cache_file):
            cache_time = os.path.getmtime(cache_file)
            if (time.time() - cache_time) < cache:
                with open(cache_file) as f:
                    out = f.read()
                if out.find('FatchError:') == 0:
                    #raise Exception(out)
                    pass
        if not out:
            with open(cache_file, 'w+') as f:
                try:
                    url_fatch = urlopen(url)
                    out = url_fatch.read().decode('utf-8')
                except Exception as err:
                    out = 'FatchError:\n'
                    out += str(err)
                    f.write(out)
                    raise err
                else:
                    f.write(out)
        data = {}
        for line in out.split('\n'):
            name,index,count,total_trades,base_price,daily_volume,enhance_level = line.split('\t')
            data[name] = {
                'Name': name,
                'Index': index,
                'Count': int(count),
                'TotalTrades': int(total_trades),
                'BasePrice': int(base_price),
                'DailyVolume': int(daily_volume),
                'EnhanceLevel': int(enhance_level),
                }
            # 根據供需關係，售價需要+-7.5%取整,0預售的頂價，日交易*10<預售的底價
            if data[name]['BasePrice'] < 1000:
                shift = -1
            elif data[name]['BasePrice'] > 1000:
                shift = -2
            if data[name]['Count'] == 0:
                data[name]['BasePrice'] = round(data[name]['BasePrice']*1.075,-2)
            elif data[name]['DailyVolume'] > data[name]['Count']*10:
                data[name]['BasePrice'] = round(data[name]['BasePrice']*1.075,-2)
            elif data[name]['DailyVolume']*10 < data[name]['Count']:
                data[name]['BasePrice'] = round(data[name]['BasePrice']*0.925,-2)
        return data


if __name__ == '__main__':
    api = Market()
    print(api.priceData('TW-tw'))
