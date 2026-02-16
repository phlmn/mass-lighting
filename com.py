import asyncio
import time
import network
import aioespnow
import espnow
import os
from array import array

import log

def read_setting(name: str, default_value: str | None = None):
    file_name = f"settings/{name}.txt"

    if file_name in os.listdir():
        with open(file_name) as f:
            return f.read()

    return default_value


class Channel:
    def __init__(self, name: str, init_value: int):
        self.name = name
        self.value = init_value


class MsgType:
    DISCOVER = 1
    INTERVIEW = 2
    CONFIGURE = 3
    DATA = 4


class RingCacheU16:
    def __init__(self, size: int):
        self.arr = array('H', [0] * size)
        self.cursor = 0

    def push(self, val: int):
        self.arr[self.cursor] = val

        if self.cursor >= len(self.arr) - 1:
            self.cursor = 0
        else:
            self.cursor += 1

    def contains(self, val: int):
        for i in range(len(self.arr)):
            if self.arr[i] == val:
                return True
        return False


class Com:
    broadcast_addr = b'\xFF\xFF\xFF\xFF\xFF\xFF'

    def __init__(self, name: str):
        self.name = name
        self.channels = dict()
        self.max_channel_idx = -1
        self.start_channel = int(read_setting("start_channel", "0"))
        self.network_id = int(read_setting("network_id", "0"))
        # self.latest_package_ids = RingCacheU16(1024)

        # prepare WLAN interface
        sta = network.WLAN(network.WLAN.IF_STA)
        sta.active(True)
        sta.config(channel=6, protocol=network.WLAN.PROTOCOL_LR)

        self.e = aioespnow.AIOESPNow()
        self.e.config(rate=espnow.RATE_LORA_250K)
        self.e.active(True)
        self.e.add_peer(self.broadcast_addr)

        asyncio.create_task(self.update_task())

    def _broadcast(self, data):
        self.e.send(self.broadcast_addr, data, False)

    def _send_msg(self):
        pass

    def _check_magic_bytes(self, msg):
        return msg[0] == 0xCA and msg[1] == 0x70

    async def update_task(self):
        async for mac, msg in self.e:
            if mac is None:
                continue

            msg_mv = memoryview(msg)

            log.debug("Received msg: ", msg.hex())

            if not self._check_magic_bytes(msg_mv):
                # just a package from another espnow application
                continue

            net_id = int.from_bytes(msg[2:4])
            if net_id != self.network_id:
                continue

            package_id = int.from_bytes(msg[4:6])
            # if self.latest_package_ids.contains(package_id):
            #     print("Skipping already seen package")
            #     # skip already seen packages
            #     # TODO: this is fucked for multiple senders
            #     continue

            # self.latest_package_ids.push(package_id)

            msg_type = msg[6]
            msg_body = msg_mv[8:]

            if msg_type == MsgType.DISCOVER:
                self._handle_discover_msg(mac, msg_body)
            elif msg_type == MsgType.INTERVIEW:
                self._handle_interview_msg(mac, msg_body)
            elif msg_type == MsgType.CONFIGURE:
                self._handle_configure_msg(mac, msg_body)
            elif msg_type == MsgType.DATA:
                self._handle_data_msg(mac, msg_body)
            else:
                log.warn(f"Received unknown message type: {msg_type}")

    def _handle_discover_msg(self, from_mac, body):
        pass

    def _handle_interview_msg(self, from_mac, body):
        pass

    def _handle_configure_msg(self, from_mac, body):
        pass

    def _handle_data_msg(self, from_mac, body: memoryview[int]):
        log.debug("Received data message: ", body.hex())
        d_from = int.from_bytes(body[:2])
        d_len = body[2]
        d_to = d_from + d_len - 1

        if d_to < self.start_channel or d_from > self.start_channel + self.max_channel_idx:
            return

        for idx, channel in self.channels.items():
            abs_channel = self.start_channel + idx

            d_idx = abs_channel - d_from
            if d_idx >= 0 and d_idx < d_len:
                channel.value = body[d_idx + 3]

    def add_channel(self, idx, name, init_value) -> Channel:
        ch = Channel(name, init_value)
        self.channels[idx] = ch
        self.max_channel_idx = max(idx, self.max_channel_idx)
        return ch
