from pathlib import Path
import json
import asyncio
import random

from universalisapi.client import UniversalisAPIClient
from universalisapi.exceptions import UniversalisError

client = UniversalisAPIClient()

async def get_least_recent_items(n):
    l = {}
    worlds = await client.world_names()
    dcs = await client.data_center_names()
    for _ in range(n):
        w_d = ['world', 'dcName']
        opt = random.choice(w_d)
        entries = random.randint(1,200)
        if opt == 'world':
            world = random.choice(worlds)
            stem = f'world_{world}_{entries}'
            try:
                data = await client.least_recent_items(world=world, entries=entries)
            except UniversalisError:
                pass
            else:
                l[stem] = data
        else:
            dc = random.choice(dcs)
            stem = f'dcName_{dc}_{entries}'
            try:
                data = await client.least_recent_items(dc=dc, entries=entries)
            except UniversalisError:
                pass
            else:
                l[stem] = data
    return l


async def get_aggregate_data(items, n):
    l = {}
    ids = []
    for item in items:
        ids.append(item['itemID'])
    regions = client.valid_regions
    regions.extend(await client.world_names())
    regions.extend(await client.data_center_names())
    for _ in range(n):
        region = random.choice(regions)
        try:
            data = await client.current_item_price_data(region, ids)
        except UniversalisError:
            pass
        else:
            stem = region + '_'
            stem += ','.join(map(str,ids))
            l[stem] = data
    return l


async def get_mb_data_data(items, n):
    l = {}
    ids = []
    for item in items:
        ids.append(item['itemID'])
    opts = {'worldName': await client.world_names(),
            'dcName': await client.data_center_names(),
            'regionName': client.valid_regions}
    opt = random.choice(list(opts.keys()))
    for _ in range(n):
        region = random.choice(opts[opt])
        try:
            data = await client._get_mb_current_data(ids,region)
        except UniversalisError:
            pass
        else:
            stem = f'{opt}_{region}_{",".join(map(str,ids))}'
            l[stem] = data
    return l


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    # start by getting 20 batches of least recent item info
    least_recent_item_data = loop.run_until_complete(get_least_recent_items(20))
    base_lri_path = Path('.') / 'least_recent_data'
    items_for_agg_data = []
    for stem, data in least_recent_item_data.items():
        stem += '.json'
        file_path = base_lri_path / stem
        print(file_path.resolve())
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(data, f)

        items_for_agg_data.extend(random.choices(data['items'], k=min(2,len(data['items']))))
    #print(least_recent_item_data)
    agg_data = loop.run_until_complete(get_aggregate_data(items_for_agg_data, 20))
    base_ad_path = Path('.') / 'aggregate_data'
    for stem, data in agg_data.items():
        stem += '.json'
        file_path = base_ad_path / stem
        print(file_path.resolve())
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(data, f)

    mb_data_data = loop.run_until_complete(get_mb_data_data(items_for_agg_data, 20))
    base_mbd_path = Path('.') / 'mb_data_data'
    for stem, data in mb_data_data.items():
        stem += '.json'
        file_path = base_mbd_path / stem
        print(file_path.resolve())
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(data, f)

    loop.run_until_complete(client.session.close())