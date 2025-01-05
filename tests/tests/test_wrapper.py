import random

import aiohttp
import pytest

from universalisapi.exceptions import UniversalisError
from universalisapi._wrapper import UniversalisAPIWrapper


@pytest.mark.unittest
class TestUniversalisAPIWrapper:

    wrapper = UniversalisAPIWrapper()

    @pytest.mark.asyncio
    async def test_session(self):
        assert isinstance(self.wrapper.session, aiohttp.ClientSession)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("code", [random.randint(201,500) for _ in range(10)])
    async def test__process_response_failures(self, code, mocked_response):
        with pytest.raises(UniversalisError):
            url = f'{self.wrapper.base_url}/test'
            mocked_response.get(url, status=code)
            async with self.wrapper.session as session:
                async with self.wrapper.session.get(url) as resp:
                    await self.wrapper._process_response(resp)

    @pytest.mark.asyncio
    async def test_get_endpoint(self):
        # Implicitly tested by basically everything
        pass

    @pytest.mark.parametrize('n',list(range(20)))
    def test__check_region_name(self, mocked_worlds, mocked_data_centers, valid_region_names, n,
                                      get_random_unicode):
        if n <= 10:
            test_name = random.choice(valid_region_names)
        else:
            test_name = get_random_unicode(random.randint(4,16))

        if test_name in valid_region_names:
            assert self.wrapper._check_region_name(test_name) is None
        else:
            with pytest.raises(UniversalisError):
                self.wrapper._check_region_name(test_name)

    @pytest.mark.asyncio
    async def test__get_mb_current_data_defaults(self, mocked_mb_current_data, mb_data_data_parser):
        w_d_r, region, items_str, item_ids, data = mb_data_data_parser
        mocked_mb_current_data(region, items_str, {}, data)
        resp = await self.wrapper._get_mb_current_data(item_ids, region)
        assert resp == data

    @pytest.mark.asyncio
    async def test__get_mb_current_data_too_many_items(self, mocked_mb_current_data):
        data = {'success': True}
        item_ids = list(range(200))
        region = 'coeurl'
        req_item_ids = list(range(100))
        mocked_mb_current_data(region, ','.join(map(str, req_item_ids)), {}, data)
        resp_data = await self.wrapper._get_mb_current_data(item_ids, region)

        assert resp_data == data

    @pytest.mark.asyncio
    @pytest.mark.parametrize("l,e,hq,s_w,e_w,f",
                             [
                                 (
                                     random.randint(0, 100),
                                     random.randint(0, 100),
                                     random.choice([True, False]),
                                     random.randint(0, 10000),
                                     random.randint(0, 10000),
                                     random.choices(wrapper.valid_fields, k=random.randint(1,3))
                                 )
                             ])
    async def test__get_mb_current_data_params(self, l, e, hq, s_w, e_w, f,
                                               mb_data_data_parser,
                                               mocked_mb_current_data):
        w_d_r, region, items_str, item_ids, data = mb_data_data_parser
        params = {
            'listings': l,
            'entries': e,
            'hq': str(hq).lower(),
            'statsWithin': s_w,
            'entriesWithin': e_w,
            'fields': ','.join(f)
        }
        mocked_mb_current_data(region, items_str, params, data)

        resp_data = await self.wrapper._get_mb_current_data(
            item_ids, region,
            listings=l, entries=e, hq=hq,
            stats_within=s_w, entries_within=e_w, fields=f)

        assert data == resp_data
