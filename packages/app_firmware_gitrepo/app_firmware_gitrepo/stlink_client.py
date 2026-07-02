"""Клиент для работы с ST-Link программатором."""

from __future__ import annotations

import subprocess
import re
from typing import Dict, Optional, Tuple, List
from pathlib import Path


class STLinkClient:
    """Класс для работы с ST-Link программатором."""
    
    def __init__(self):
        self.device_info = {}
        self._connected = False
        self._stlink_available = self._check_stlink_available()
    
    def _check_stlink_available(self) -> bool:
        """Проверяет, доступен ли ST-Link."""
        try:
            result = subprocess.run(
                ["st-info", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_stlink_info(self) -> Dict[str, str]:
        """Возвращает информацию о ST-Link программаторе."""
        info = {
            "available": self._stlink_available,
            "version": "unknown",
            "connected": False
        }
        
        if not self._stlink_available:
            return info
        
        try:
            result = subprocess.run(
                ["st-info", "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            info["version"] = result.stdout.strip()
            
            # Проверяем через probe, есть ли подключенное устройство
            result = subprocess.run(
                ["st-info", "--probe"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            if "Found 1 stlink programmers" in result.stdout:
                info["connected"] = True
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
            
        return info
    
    def _run_st_info(self, arg: str) -> str:
        """Выполняет одну команду st-info и возвращает вывод."""
        try:
            result = subprocess.run(
                ["st-info", arg],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return ""
    
    def _parse_hex_value(self, hex_str: str) -> int:
        """Преобразует hex-строку в число."""
        try:
            if hex_str.startswith("0x"):
                return int(hex_str, 16)
            return int(hex_str)
        except Exception:
            return 0
    
    def _format_size(self, hex_str: str) -> str:
        """Преобразует размер из hex в KB или MB."""
        bytes_val = self._parse_hex_value(hex_str)
        if bytes_val == 0:
            return hex_str
        if bytes_val >= 1024 * 1024:
            return f"{bytes_val // (1024 * 1024)} MB"
        else:
            return f"{bytes_val // 1024} KB"
    
    def connect(self) -> Tuple[bool, str]:
        """
        Подключается к устройству через ST-Link.
        
        Returns:
            (success, message)
        """
        if not self._stlink_available:
            return False, "ST-Link не найден. Установите st-link (https://github.com/stlink-org/stlink)"
        
        try:
            # Вызываем каждый параметр отдельно
            chipid = self._run_st_info("--chipid")
            serial = self._run_st_info("--serial")
            flash = self._run_st_info("--flash")
            sram = self._run_st_info("--sram")
            descr = self._run_st_info("--descr")
            
            # Проверяем, что устройство найдено
            if not chipid and not serial:
                return False, "Устройство не найдено. Проверьте подключение программатора"
            
            self.device_info = {
                "chipid": chipid if chipid else "Unknown",
                "serial": serial if serial else "Unknown",
                "flash_size": self._format_size(flash) if flash else "Unknown",
                "sram_size": self._format_size(sram) if sram else "Unknown",
                "description": descr if descr else "Unknown",
                "chip": descr if descr else f"STM32 (ID: {chipid})"
            }
            
            self._connected = True
            return True, "Устройство успешно подключено"
            
        except subprocess.TimeoutExpired:
            return False, "Таймаут подключения. Проверьте программатор"
        except FileNotFoundError:
            return False, "st-info не найден. Убедитесь, что ST-Link установлен и добавлен в PATH"
        except Exception as e:
            return False, f"Ошибка подключения: {str(e)}"
    
    def _parse_st_info(self, output: str) -> Dict[str, str]:
        """Парсит вывод st-info (устаревший, оставлен для совместимости)."""
        info = {
            "chip": "Unknown",
            "chipid": "Unknown",
            "serial": "Unknown",
            "flash_size": "Unknown",
            "sram_size": "Unknown",
            "description": "Unknown"
        }
        
        patterns = {
            "chip": r"chip:\s*(\w+)",
            "chipid": r"chipid:\s*([0-9a-fA-F]+)",
            "serial": r"serial:\s*([0-9a-fA-F]+)",
            "flash_size": r"flash:\s*(\d+)\s*KB",
            "sram_size": r"sram:\s*(\d+)\s*KB",
            "description": r"descr:\s*(.+)"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                info[key] = match.group(1)
        
        return info
    
    def flash(self, firmware_path: str, verify: bool = True) -> Tuple[bool, str]:
        """
        Прошивает устройство.
        
        Args:
            firmware_path: Путь к файлу прошивки
            verify: Проверять после прошивки
            
        Returns:
            (success, message)
        """
        if not self._connected:
            return False, "Устройство не подключено"
        
        if not Path(firmware_path).exists():
            return False, f"Файл прошивки не найден: {firmware_path}"
        
        try:
            # Формируем команду
            cmd = ["st-flash", "write", firmware_path, "0x8000000"]
            if verify:
                cmd.append("--verify")
            
            # Выполняем прошивку
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=120
            )
            
            # Проверяем вывод на ошибки
            if "error" in result.stdout.lower() or "failed" in result.stdout.lower():
                return False, "Ошибка при прошивке"
            
            return True, "Прошивка успешно завершена"
            
        except subprocess.TimeoutExpired:
            return False, "Таймаут прошивки. Проверьте подключение устройства"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            if "verify failed" in error_msg.lower():
                return False, "Ошибка верификации прошивки"
            else:
                return False, f"Ошибка прошивки: {error_msg}"
        except FileNotFoundError:
            return False, "st-flash не найден. Убедитесь, что ST-Link установлен"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"
    
    def get_device_info(self) -> Dict[str, str]:
        """Возвращает информацию об устройстве."""
        return self.device_info
    
    def get_device_family(self) -> str:
        """
        Определяет семейство устройства по информации о чипе.
        
        Returns:
            'STM32', 'ATmega' или 'Unknown'
        """
        descr = self.device_info.get('description', '').upper()
        chipid = self.device_info.get('chipid', '').upper()
        
        if 'F1' in descr or 'F4' in descr or 'F0' in descr or 'F2' in descr or 'F3' in descr:
            return 'STM32'
        elif 'STM32' in descr or 'STM' in descr:
            return 'STM32'
        elif 'AT' in chipid or 'MEGA' in descr:
            return 'ATmega'
        else:
            return 'STM32' if chipid else 'Unknown'
    
    def is_connected(self) -> bool:
        """Проверяет, подключено ли устройство."""
        return self._connected