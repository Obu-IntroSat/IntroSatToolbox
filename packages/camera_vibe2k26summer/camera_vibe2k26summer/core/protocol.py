"""Protocol handler for camera communication."""

from __future__ import annotations
import struct
import time
from typing import Optional
import serial

from .config import CameraCommandConfig


class ProtocolHandler:
    """Обработчик протокола общения с камерой"""
    
    def __init__(self, config: CameraCommandConfig):
        self.config = config
        self.ser: Optional[serial.Serial] = None
        self._chunk_struct = struct.Struct(config.chunk_format)
        self._prop_struct = struct.Struct(config.property_format)
        self._chunk_buffer = bytearray(config.chunk_size + 8)
    
    def connect(self, port: str) -> bool:
        try:
            self.ser = serial.Serial(
                port,
                self.config.baudrate,
                timeout=3.0,
                parity=serial.PARITY_NONE
            )
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            return True
        except Exception:
            return False
    
    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None
    
    @property
    def is_connected(self) -> bool:
        return self.ser is not None and self.ser.is_open
    
    def write(self, data: bytes):
        if self.ser and self.ser.is_open:
            self.ser.write(data)
            self.ser.flush()
    
    def write_command(self, cmd: str):
        cmd_bytes = self.config.get_command_bytes(cmd)
        self.write(cmd_bytes)
        return cmd_bytes
    
    def read_until(self, pattern: bytes, timeout: float = 3.0) -> bytes:
        if not self.ser or not self.ser.is_open:
            return b''
        start = time.time()
        data = b''
        while (time.time() - start) < timeout:
            if self.ser.in_waiting > 0:
                data += self.ser.read(self.ser.in_waiting)
                if pattern in data:
                    return data
            time.sleep(0.001)
        return data
    
    def read_exact(self, size: int, timeout: float = 3.0) -> bytes:
        if not self.ser or not self.ser.is_open:
            return b''
        data = b''
        start = time.time()
        while len(data) < size and (time.time() - start) < timeout:
            if self.ser.in_waiting > 0:
                available = self.ser.in_waiting
                to_read = min(available, size - len(data))
                data += self.ser.read(to_read)
            time.sleep(0.001)
        return data
    
    def read_chunk(self) -> Optional[tuple]:
        if not self.ser or not self.ser.is_open:
            return None
        
        preamble = bytes.fromhex(self.config.preamble)
        chunk_size = self.config.chunk_size + 8
        chunk_buffer = self._chunk_buffer
        
        self.read_until(preamble, timeout=self.config.timeout_chunk)
        
        read_total = 0
        start_time = time.time()
        timeout = self.config.timeout_chunk
        
        while read_total < chunk_size and (time.time() - start_time) < timeout:
            if self.ser.in_waiting > 0:
                available = self.ser.in_waiting
                to_read = min(available, chunk_size - read_total)
                chunk_buffer[read_total:read_total + to_read] = self.ser.read(to_read)
                read_total += to_read
            time.sleep(0.0005)
        
        if read_total < chunk_size:
            return None
        
        try:
            return self._chunk_struct.unpack_from(chunk_buffer)
        except Exception:
            return None
    
    def send_set_size(self, width: int, height: int):
        cmd = self.config.get_command_bytes(self.config.set_size)
        cmd += struct.pack('<HH', width, height)
        self.write(cmd)
        time.sleep(0.05)
    
    def send_set_exposure(self, exposure: int):
        cmd = self.config.get_command_bytes(self.config.set_exposure)
        cmd += struct.pack('<H', exposure)
        self.write(cmd)
        time.sleep(0.05)