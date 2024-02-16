from decimal import Decimal

class Sens():
    def __init__(self, game, dpi, sens):
        self.game = game
        self.dpi = dpi
        self.sens = sens



    def hurimuki(self): 
        def decimal_normalize(f):
            """数値fの小数点以下を正規化し、文字列で返す"""
            def _remove_exponent(d):
                return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()
            a = Decimal.normalize(Decimal(str(f)))
            b = _remove_exponent(a)
            return str(b)
        try:
            game_dict = {'apex':115.46666666666667, 'valorant':36.2844444, 'fortnite':457.24444444444447}
            game_value = game_dict[self.game]
            
            edpi = float(self.dpi) * float(self.sens)
            edpi = decimal_normalize(edpi)
            hurimuki = (180 / int(edpi)) * float(game_value)
            hurimuki = "%.2f" % hurimuki         
            return hurimuki
        except:
            return "error"
