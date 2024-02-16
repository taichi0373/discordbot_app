import requests, json, os

class Apex():
    def __init__(self, platform, playerId):
        self.platform = platform
        self.playerId = playerId
    
    # ユーザープロフィールを取得    
    def GetProfile(self):
        TRN_URL = ''
        Apex_KEY = os.environ['API_KEY']
        url = TRN_URL
        url += '/' + self.platform
        url += '/' + self.playerId
        header = {"TRN-Api-Key":Apex_KEY}
        # http getリクエスト送信
        response_dict = requests.get(url, headers=header).json()
        response = json.dumps(response_dict)        # 辞書型をJSON形式の文字列に変換する
        return response

    # jsonの戦績を表示        
    def DispStats(json):
        stats = json['data']['segments'][0]['stats']
        res_stats = {}
        try:
            for key, value in stats.items():
                if key == 'level':
                    res_stats["レベル"] = value["displayValue"]
                if key == 'kills':
                    res_stats["総キル数"] = value["displayValue"]
                if key == 'damage':
                    res_stats["総ダメージ数"] = value["displayValue"]
            return res_stats
        except:
            return "データがありません"
        
    # rankを表示        
    def Disprank(json):
        rank_name = json['data']['segments'][0]['stats']['rankScore']['metadata']
        res_rank = {}
        try:
            if 'rankName' in rank_name:
                res_rank["ランク"] = rank_name["rankName"]
            rank_score = json['data']['segments'][0]['stats']['rankScore']
            if 'value' in rank_score:
                res_rank["ランクポイント"] = rank_score["value"]
            return res_rank
        except:
            return "データがありません"