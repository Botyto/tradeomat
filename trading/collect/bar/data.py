from datetime import datetime
import io
import struct


class Bar:
    MARKER = "BAR8"
    BINARY_SIZE = 8 + 4*8 + 8
    BINARY_FORMAT = "<QQQQQQ"
    FIXED_POINT_MULTIPLIER = 1000000
    
    __slots__ = ("date", "iopen", "ihigh", "ilow", "iclose", "volume")
    date: datetime
    iopen: int
    ihigh: int
    ilow: int
    iclose: int
    volume: int

    def __init__(self, date: datetime, iopen: int, ihigh: int, ilow: int, iclose: int, volume: int):
        self.date = date
        self.iopen = iopen
        self.ihigh = ihigh
        self.ilow = ilow
        self.iclose = iclose
        self.volume = volume

    def write(self, stream: io.BytesIO):
        buffer = struct.pack(
            self.BINARY_FORMAT,
            self.date.timestamp(),
            self.iopen,
            self.ihigh,
            self.ilow,
            self.iclose,
            self.volume,
        )
        stream.write(buffer)

    @classmethod
    def read(cls, stream: io.BytesIO):
        buffer = stream.read(cls.BINARY_SIZE)
        data = struct.unpack(cls.BINARY_FORMAT, buffer)
        return Bar(
            date=datetime.fromtimestamp(data[0]),
            iopen=data[1],
            ihigh=data[2],
            ilow = data[3],
            iclose = data[4],
            volume = data[5],
        )
    
    def __repr__(self):
        return f"Bar({self.date}, {self.iopen}, {self.ihigh}, {self.ilow}, {self.iclose}, {self.volume})"
    
    @property
    def open(self):
        return self.iopen / self.FIXED_POINT_MULTIPLIER
    
    @open.setter
    def open(self, value):
        self.iopen = int(value * self.FIXED_POINT_MULTIPLIER)

    @property
    def high(self):
        return self.ihigh / self.FIXED_POINT_MULTIPLIER
    
    @high.setter
    def high(self, value):
        self.ihigh = int(value * self.FIXED_POINT_MULTIPLIER)

    @property
    def low(self):
        return self.ilow / self.FIXED_POINT_MULTIPLIER
    
    @low.setter
    def low(self, value):
        self.ilow = int(value * self.FIXED_POINT_MULTIPLIER)

    @property
    def close(self):
        return self.iclose / self.FIXED_POINT_MULTIPLIER
    
    @close.setter
    def close(self, value):
        self.iclose = int(value * self.FIXED_POINT_MULTIPLIER)
