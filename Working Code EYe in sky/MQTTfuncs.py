import socket
import struct
from binascii import hexlify

class MQTTException(Exception):
    pass

class MQTTClient:
    def __init__(self, client_id, server, port=1883, user=None, password=None, keepalive=0, ssl=None):
        self.client_id = client_id.encode()
        self.sock = None
        self.server = server
        self.port = port
        self.ssl = ssl
        self.pid = 0
        self.cb = None
        self.user = user.encode() if user else None
        self.pswd = password.encode() if password else None
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False

    def _send(self, data):
        self.sock.sendall(data)# type: ignore

    def _recv_exact(self, n):
        buf = b''
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))# type: ignore
            if not chunk:
                raise ConnectionError("Socket connection broken")
            buf += chunk
        return buf

    def _send_str(self, s):
        if isinstance(s, str):
            s = s.encode()
        self._send(struct.pack("!H", len(s)) + s)

    def _recv_len(self):
        n = 0
        sh = 0
        while True:
            b = self._recv_exact(1)[0]
            n |= (b & 0x7F) << sh
            if not b & 0x80:
                break
            sh += 7
        return n

    def set_callback(self, f):
        self.cb = f

    def set_last_will(self, topic, msg, retain=False, qos=0):
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic.encode()
        self.lw_msg = msg.encode()
        self.lw_qos = qos
        self.lw_retain = retain

    def connect(self, clean_session=True, timeout=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.connect((self.server, self.port))

        premsg = bytearray(b"\x10\0\0\0\0\0")
        msg = bytearray(b"\x04MQTT\x04\x02\0\0")
        sz = 10 + 2 + len(self.client_id)

        msg[6] = clean_session << 1
        if self.user:
            sz += 2 + len(self.user) + 2 + len(self.pswd)# type: ignore
            msg[6] |= 0xC0
        if self.keepalive:
            msg[7] = self.keepalive >> 8
            msg[8] = self.keepalive & 0x00FF
        if self.lw_topic:
            sz += 2 + len(self.lw_topic) + 2 + len(self.lw_msg)# type: ignore
            msg[6] |= 0x4 | (self.lw_qos & 0x1) << 3 | (self.lw_qos & 0x2) << 3
            msg[6] |= self.lw_retain << 5

        i = 1
        while sz > 0x7F:
            premsg[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        premsg[i] = sz

        self._send(premsg[:i+2])
        self._send(msg)
        self._send_str(self.client_id)
        if self.lw_topic:
            self._send_str(self.lw_topic)
            self._send_str(self.lw_msg)
        if self.user:
            self._send_str(self.user)
            self._send_str(self.pswd)

        resp = self._recv_exact(4)
        assert resp[0] == 0x20 and resp[1] == 0x02
        if resp[3] != 0:
            raise MQTTException(resp[3])
        return resp[2] & 1

    def disconnect(self):
        self._send(b"\xe0\0")
        self.sock.close()# type: ignore

    def ping(self):
        self._send(b"\xc0\0")

    def publish(self, topic, msg, retain=False, qos=0):
        if isinstance(topic, str):
            topic = topic.encode()
        if isinstance(msg, str):
            msg = msg.encode()

        pkt = bytearray(b"\x30\0\0\0")
        pkt[0] |= qos << 1 | retain
        sz = 2 + len(topic) + len(msg)
        if qos > 0:
            sz += 2
        i = 1
        while sz > 0x7F:
            pkt[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz

        self._send(pkt[:i+1])
        self._send_str(topic)
        if qos > 0:
            self.pid += 1
            pid = self.pid
            self._send(struct.pack("!H", pid))
        self._send(msg)

    def subscribe(self, topic, qos=0):
        assert self.cb is not None, "Subscribe callback is not set"
        if isinstance(topic, str):
            topic = topic.encode()
        pkt = bytearray(b"\x82\0\0\0")
        self.pid += 1
        pkt_len = 2 + 2 + len(topic) + 1
        struct.pack_into("!BH", pkt, 1, pkt_len, self.pid)
        self._send(pkt)
        self._send_str(topic)
        self._send(bytes([qos]))

    def wait_msg(self):
        res = self._recv_exact(1)
        self.sock.setblocking(True)# type: ignore
        if res == b"":
            raise OSError(-1)
        if res == b"\xd0":  # PINGRESP
            sz = self._recv_exact(1)[0]
            assert sz == 0
            return None
        op = res[0]
        if op & 0xF0 != 0x30:
            return op
        sz = self._recv_len()
        topic_len = self._recv_exact(2)
        topic_len = (topic_len[0] << 8) | topic_len[1]
        topic = self._recv_exact(topic_len)
        sz -= topic_len + 2
        if op & 6:
            pid = self._recv_exact(2)
            pid = pid[0] << 8 | pid[1]
            sz -= 2
        msg = self._recv_exact(sz)
        if self.cb:
            self.cb(topic, msg)
        if op & 6 == 2:
            pkt = bytearray(b"\x40\x02\0\0")
            struct.pack_into("!H", pkt, 2, pid)
            self._send(pkt)
        return op

    def check_msg(self):
        self.sock.setblocking(False) # type: ignore
        try:
            return self.wait_msg()
        except BlockingIOError:
            return None

    
client_id = "SouleyC"
server = "10.247.137.92"
topic = "SlidePuzzle/send"

mqtt1 = MQTTClient(client_id=client_id, server=server)
mqtt1.connect()
mqtt1.publish(topic, msg="hi -julian")
mqtt1.disconnect()


