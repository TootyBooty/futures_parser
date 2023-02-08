# pip3 install aiohttp
from aiohttp import ClientSession

import asyncio
import time
from decimal import Decimal


BASE_BINANCE_API_URL = 'https://fapi.binance.com/fapi'


async def get_futures_current_price(futures_name:str):
    # Создаем сессию aiohttp внутри которой будем отправлять все запросы
    async with ClientSession() as session:
        # Полный адрес и параметры запроса для получения информации о фьючерсе за текущий час
        url = f'{BASE_BINANCE_API_URL}/v1/markPriceKlines'
        params = {'symbol': futures_name, 'interval': '1h', 'limit': 1}

        async with session.get(url=url, params=params) as response:
            response_json = await response.json()

            # При неуспешном запросе останавливаем цикл чтобы перестать отправлять некорректные запросы
            if response.status != 200:
                raise RuntimeError(response_json.get('msg', 'Ошибка при отправке запроса!'))

            # Получив список со списками, достаем из него нужные значения
            futures_data = response_json[0]
            current_price = Decimal(futures_data[4])
            high_price_in_last_hour = Decimal(futures_data[2])

            # Если разница между максимальной и текущей ценой >= 1 проценту максимальной цены, то сообщаем об этом в консоли
            if (high_price_in_last_hour - current_price) >= high_price_in_last_hour * Decimal('0.01'):
                print(f'\n\n    !!! За этот час цена {futures_name} упала более чем на 1% !!!')
            # Выводим текущую и максимальную за час цены

            print(f'\n{futures_name}: \n    Текущая цена: {current_price} \n    Максимальная цена за час: {high_price_in_last_hour}\n')


async def main(waiting_time: int):
    # Запускаем бесконечный цикл с синхронным сном, чтобы не спамить запросами
    print('Используйте ^C для остановки скрипта')
    while True:
        await get_futures_current_price('XRPUSDT')
        time.sleep(waiting_time)
        

if __name__ == '__main__':
    try:
        asyncio.run(main(waiting_time=10))
    except RuntimeError as e:
        print(e)
    except KeyboardInterrupt:
        print(' Stopping...')
