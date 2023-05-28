import pytest
from binance import Client
from dotenv import load_dotenv

from algo_binance.main import create_order, API_KEY, SEKRET_KEY


load_dotenv()


@pytest.fixture
def binance_client():
    # Создаем экземпляр клиента Binance для тестов

    return Client(API_KEY, SEKRET_KEY)

def test_create_order_success(binance_client):
    # Проверяем успешное создание ордеров
    data = {
        "volume": 100.0,
        "number": 5,
        "amountDif": 1.0,
        "side": "SELL",
        "priceMin": 10,
        "priceMax": 12,
        "symbol": "LDOUSDT",
        "orderType": "LIMIT",
    }
    result = create_order(data, binance_client)
    assert len(result) == data['number']  # Ожидаем, что ордера успешно созданы

def test_create_order_invalid_symbol(binance_client):
    # Проверяем обработку ошибки при неверном значении symbol
    data = {
        "volume": 100.0,
        "number": 5,
        "amountDif": 1.0,
        "side": "SELL",
        "priceMin": 10,
        "priceMax": 12,
        "symbol": "INVALID",  # Неверный символ
        "orderType": "LIMIT",
    }
    with pytest.raises(ValueError):
        create_order(data, binance_client)


def test_create_order_error_exception(binance_client):
    # Проверяем обработку ошибки типа исключения при создании ордеров
    data = {
        "volume": 100.0,
        "number": 5,
        "amountDif": 1.0,
        "side": "SELL",
        "priceMin": 10,
        "priceMax": 12,
        "symbol": "LDOUSDT",
        "orderType": "INVALID_TYPE",  # Неверный тип ордера
    }
    with pytest.raises(ValueError):
        create_order(data, binance_client)
