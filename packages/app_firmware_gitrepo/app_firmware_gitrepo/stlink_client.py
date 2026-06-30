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
            
            # Проверяем, есть ли подключенное устройство
            result = subprocess.run(
                ["st-info", "--chip"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            if "unknown" not in result.stdout.lower():
                info["connected"] = True
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
            
        return info
    
    def connect(self) -> Tuple[bool, str]:
        """
        Подключается к устройству через ST-Link.
        
        Returns:
            (success, message)
        """
        if not self._stlink_available:
            return False, "ST-Link не найден. Установите st-link (https://github.com/stlink-org/stlink)"
        
        try:
            # Получаем информацию о чипе
            result = subprocess.run(
                ["st-info", "--chip", "--core-id", "--serial", "--flash", "--sram"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            self.device_info = self._parse_st_info(result.stdout)
            self._connected = True
            
            return True, "Устройство успешно подключено"
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            
            # Анализируем ошибку
            if "no device found" in error_msg.lower():
                return False, "Устройство не найдено. Проверьте подключение программатора"
            elif "connect under reset" in error_msg.lower():
                return False, "Ошибка подключения. Попробуйте сбросить устройство"
            else:
                return False, f"Ошибка ST-Link: {error_msg}"
        except subprocess.TimeoutExpired:
            return False, "Таймаут подключения. Проверьте программатор"
        except FileNotFoundError:
            return False, "st-info не найден. Убедитесь, что ST-Link установлен и добавлен в PATH"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"
    
    def _parse_st_info(self, output: str) -> Dict[str, str]:
        """Парсит вывод st-info."""
        info = {
            "chip": "Unknown",
            "core_id": "Unknown",
            "serial": "Unknown",
            "flash_size": "Unknown",
            "sram_size": "Unknown"
        }
        
        # Парсим информацию
        patterns = {
            "chip": r"chip:\s*(\w+)",
            "core_id": r"core[-_]id:\s*([0-9a-fA-F]+)",
            "serial": r"serial:\s*([0-9a-fA-F]+)",
            "flash_size": r"flash:\s*(\d+)\s*KB",
            "sram_size": r"sram:\s*(\d+)\s*KB"
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
                timeout=120  # Таймаут 120 секунд
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
    
    def is_connected(self) -> bool:
        """Проверяет, подключено ли устройство."""
        return self._connected