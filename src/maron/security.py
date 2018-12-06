class Security:
    """銘柄を表すクラス. 
    {'__module__': 'maron.security', '__doc__': '
    銘柄を表すクラス
    ', 'Market': , '__init__': , 'setCurrent': , 'rec': , 'currency': , 'per': , 'pbr': , 'eps': ,
     'bps': , 'symbol': , 'code': , 'unit': , 'quote': , 'order': , 'order_value': , 'order_target_value': ,
     'order_target': , 'order_target_percent': , 'order_percent': , 'cancel_order': , 'get_open_orders': ,
      '__dict__': , '__weakref__': }
    Attributes:
        ctx: Context, 
        sym: str, Symbol of stock.
    """

    def __init__(self, ctx, sym):
        """銘柄を表すクラス. 
        
        Attributes:
            ctx: Context, 
            sym: str, Symbol of stock.
        """
        self.sym = sym
        self._code = int(sym.split(".")[-1])
        self.ctx = ctx

    def _Security__rec(self):
        pass

    def currentInfo(self):
        pass

    def code(self):
        return self._code

    def setCurrent(self, current):
        self.current = current

    def rec(self):
        pass

    def currency(self):
        pass

    def per(self):
        pass

    def pbr(self):
        pass

    def eps(self):
        pass

    def bps(self):
        pass

    def symbol(self):
        pass

    def unit(self):
        pass

    def quote(self):
        pass

    def order(self, amount, comment):
        """数量を指定して注文
        
        Args:
            amount: int, Amount of stock. e.g. 100. 
        """
        self.ctx.asset._order(amount, comment)

    def order_value(self, amount, comment):
        """金額を指定して注文
        Args:
            amount: int, Value of stock. e.g. 100000. 
        """
        self.ctx.asset._order_value(amount, comment)

    def order_percent(self, amount, comment):
        """現在のポートフォリオに比した割合で注文
        Args:
            amount: float, Ratio portfolio. e.g. 0.02. 
        """
        self.ctx.asset._order_percent(amount, comment)

    def order_target(self, amount, comment):
        """総保有数を指定して注文
        """
        self.ctx.asset._order_target(amount, comment)

    def order_target_value(self, amount, comment):
        """総額を指定して注文
        
        """
        self.ctx.asset._order_target_value(amount, comment)

    def order_target_percent(self, amount, comment):
        """総保有額が総資産評価額(現金+保有ポジション評価額)に対して指定の割合となるように注文

        """
        self.ctx.asset._order_target_percent(amount, comment)

    def cancel_order(self):
        pass

    def get_open_orders(self):
        pass
