import asyncio
import os
import threading
import time
from itertools import product
from unittest import IsolatedAsyncioTestCase

from PIL import Image

from ahk import AsyncAHK


class TestScreen(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        print('setting up')
        self.ahk = AsyncAHK()
        self.before_windows = await self.ahk.list_windows()
        self.im = Image.new('RGB', (20, 20))
        for coord in product(range(20), range(20)):
            self.im.putpixel(coord, (255, 0, 0))
        await asyncio.sleep(2)

    async def asyncTearDown(self):
        print('tearing down')
        for win in await self.ahk.list_windows():
            if win not in self.before_windows:
                print('closing', win)
                await win.close()
        print('killing proc')
        self.ahk._transport._proc.kill()

    #
    # async def test_pixel_search(self):
    #     result = await self.ahk.pixel_search(0xFF0000)
    #     self.assertIsNotNone(result)

    def _show_in_thread(self):
        t = threading.Thread(target=self.im.show)
        t.start()
        return t

    async def test_image_search(self):
        self._show_in_thread()
        time.sleep(2)
        self.im.save('testimage.png')
        position = await self.ahk.image_search('testimage.png')
        assert isinstance(position, tuple)

    async def test_pixel_search(self):
        self._show_in_thread()
        time.sleep(2)
        self.im.save('testimage.png')
        position = await self.ahk.image_search('testimage.png')
        x, y = position
        color = await self.ahk.pixel_get_color(x, y)
        region_start = (x - 1, y - 1)
        region_end = (x + 1, y + 1)
        pos = await self.ahk.pixel_search(region_start, region_end, color)
        assert pos is not None
        x2, y2 = pos
        assert abs(x2 - x) < 3 and abs(y2 - y) < 3

    # async def test_pixel_get_color(self):
    #     x, y = await self.ahk.pixel_search(0xFF0000)
    #     result = await self.ahk.pixel_get_color(x, y)
    #     self.assertIsNotNone(result)
    #     self.assertEqual(int(result, 16), 0xFF0000)
