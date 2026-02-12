import network
import espnow
import os

import log

def read_setting(name: str, default_value: str | None = None):
    file_name = f"settings/{name}.txt"

    if file_name in os.listdir():
        with open(file_name) as f:
            return f.read()

    return default_value


class MsgType:
    DISCOVER = 1
    INTERVIEW = 2
    CONFIGURE = 3
    DATA = 4


def make_msg_header(msg_type: int, network_id: int, package_id: int):
    if package_id == 0:
        raise ValueError("Package ID cannot be zero")

    msg = bytearray(8)
    msg[0] = 0xCA
    msg[1] = 0x70
    msg[2:4] = network_id.to_bytes(2)
    msg[4:6] = package_id.to_bytes(2)
    msg[6] = msg_type
    msg[7] = 0x00 # for future use
    return msg

def make_data_msg(package_id: int, d_from: int, data: bytes):
    header = make_msg_header(MsgType.DATA, 0, package_id)
    body = bytearray(len(data) + 3)
    body[0:2] = d_from.to_bytes(2)
    body[2] = len(data)
    body[3:] = data
    return header + body

class Sender:
    broadcast_addr = b'\xFF\xFF\xFF\xFF\xFF\xFF'

    def __init__(self):
        self.network_id = int(read_setting("network_id", "0"))

        # prepare WLAN interface
        sta = network.WLAN(network.WLAN.IF_STA)
        sta.active(True)
        sta.config(channel=6, protocol=network.WLAN.PROTOCOL_LR)

        self.e = espnow.ESPNow()
        self.e.config(rate=espnow.RATE_LORA_250K, timeout_ms=0)
        self.e.active(True)
        self.e.add_peer(self.broadcast_addr)

        self.last_package_id = 0

    def broadcast(self, msg):
        self.e.send(self.broadcast_addr, msg, False)

    def gen_package_id(self):
        if self.last_package_id < 0xFFFF:
            self.last_package_id += 1
        else:
            self.last_package_id = 1
        return self.last_package_id

    def _check_magic_bytes(self, msg):
        return msg[0] == 0xCA and msg[1] == 0x70

    def send_data_msg(self, d_from: int, data: bytes):
        msg = make_data_msg(self.gen_package_id(), d_from, data)
        self.e.send(self.broadcast_addr, msg, False)

    def update(self):
        for mac, msg in self.e:
            if mac is None:
                break

            if not self._check_magic_bytes(msg):
                # just a package from another espnow application
                continue

            net_id = int.from_bytes(msg[2:3])
            if net_id != self.network_id:
                continue

            package_id = int.from_bytes(msg[4:5])
            # if self.latest_package_ids.contains(package_id):
            #     # skip already seen packages
            #     # TODO: this is fucked for multiple senders
            #     continue

            # self.latest_package_ids.push(package_id)

            msg_type = msg[6]
            msg_body = msg[8:]

            if msg_type == MsgType.DISCOVER:
                self._handle_discover_msg(mac, msg_body)
            elif msg_type == MsgType.INTERVIEW:
                self._handle_interview_msg(mac, msg_body)
            elif msg_type == MsgType.CONFIGURE:
                self._handle_configure_msg(mac, msg_body)
            else:
                log.warn(f"Received unknown message type: {msg_type}")

    def _handle_discover_msg(self, from_mac, body):
        pass

    def _handle_interview_msg(self, from_mac, body):
        pass

    def _handle_configure_msg(self, from_mac, body):
        pass
