import random as r 
import os
from decimal import Decimal
# from binance.error import 
from binance import Client
from binance import exceptions
from pydantic import BaseModel, Field, validator
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
SEKRET_KEY = os.getenv('SEKRET_KEY')


###################################################
#    Воспользуемся пакетами ENUM и Pydantic для проверки
#    Блок проверки данных json

class OrderType(Enum):
    """Возможные значения поля orderType."""
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP = 'STOP'
    STOP_MARKET = 'STOP_MARKET'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'
    TRAILING_STOP_MARKET = 'TRAILING_STOP_MARKET'


class SideType(Enum):
    """Возможные значения поля side"""
    SELL = 'SELL'
    BAY = 'BAY'


class ValidateData(BaseModel):
    """Провалидируем данные"""
    volume: float = Field(ge=1)                  # Значение больше быть >= 1
    number: int = Field(ge=1)                    # Нужен как минимумм ордер.. 
    amonut: float = Field(alias='amountDif')     # приведем переменную из КамелКасе в снаке_касе
    side: SideType                               # будем сопоставлять данные через класс SideEnum
    price_min: float = Field(alias='priceMin')   # приведем переменную из КамелКасе в снаке_касе
    price_max: float = Field(alias='priceMax')   # приведем переменную из КамелКасе в снаке_касе
    symbol: str                                  # Данное поле будем валидировать через функцию valid_symbol_len
    type: OrderType = Field(alias='orderType')   # тип ордера
    
    @validator('symbol')
    def valid_symbol_len(cls, s):
        """Проверяем длину строки """
        if len(s) < 4:
            raise ValueError(f'Убедитесь в правильности написания символа: {s}')
        if 'USD' not in s:
            raise ValueError({'error': -1121, 'error_massage': 'Invalid symbol.'})
        return s
 

###################################################

data_order = {
   "volume": 100.0,      # Объем в долларах
   "number": 5,          # На сколько ордеров нужно разбить этот объем
   "amountDif": 1.0,     # Разброс в долларах, в пределах которого случайным образом выбирается объем в верхнюю и нижнюю сторону
   "side": "SELL",       # Сторона торговли (SELL или BUY)
   "priceMin": 10,       # Нижний диапазон цены, в пределах которого нужно случайным образом выбрать цену
   "priceMax": 12,       # Верхний диапазон цены, в пределах которого нужно случайным образом выбрать цену
   "symbol": "LDOUSDT",  # Символ
   "orderType": "LIMIT", # Тип ордера

}


def create_order(data: dict, cl: Client):
    """Создаем ордера"""
    data = ValidateData.parse_obj(data)
    value_one_order = round(data.volume / data.number, 2) # средний объем на сделку
    symbol_data = cl.futures_klines(symbol=data.symbol, interval='1m', limit=1)
    x = []
    for _ in range(data.number):

    #     # https://binance-docs.github.io/apidocs/futures/en/#new-order-trade

        amount_random = r.uniform(-data.amonut, data.amonut) # Случайный объем
        price_random = str(round(r.uniform(data.price_min, data.price_max),4)) # Случайная цена
        value = value_one_order + amount_random
        quantity = round(float(value)/float(symbol_data[-1][4]))

        try:
            order = cl.futures_create_order(
                symbol=data.symbol,
                price = price_random,
                quantity=quantity,
                type=data.type.value,
                side=data.side.value,
                timeInForce=cl.TIME_IN_FORCE_GTC
                )
        except exceptions.BinanceOrderException as er:
            return {'error_code': er.code, 'error_massage': er.message}
        x.append(order)
    return x
    # open_orders = cl.futures_get_open_orders(symbol=data.symbol)
    # for order in open_orders:
    #     cl.futures_cancel_order(symbol=data.symbol, orderId=order['orderId'])
    


if __name__ == '__main__':
    cl = Client(api_key= API_KEY, api_secret=SEKRET_KEY)
    create_order(data_order, cl)