"""Клиент для работы с ST-Link программатором с поддержкой встроенных бинарников."""

from __future__ import annotations

import subprocess
import re
import sys
import os
from typing import Dict, Optional, Tuple, List
from pathlib import Path


class STLinkClient:
    """Класс для работы с ST-Link программатором."""
    
    def __init__(self):
        self.device_info = {}
        self._connected = False
        
        # Определяем путь к папке с бинарниками ST-Link
        self.stlink_bin_path = self._get_stlink_bin_path()
        
        # Проверяем доступность ST-Link (локально или в системе)
        self._stlink_available = self._check_stlink_available()
    
    def _get_stlink_bin_path(self) -> Optional[Path]:
        """
        Определяет путь к папке с бинарниками ST-Link.
        Сначала проверяет локальную папку в приложении, затем системный PATH.
        """
        # 1. Проверяем локальную папку рядом со скриптом
        local_bin = Path(__file__).parent / "bin"
        if local_bin.exists() and any(local_bin.glob("st-info*")):
            return local_bin
        
        # 2. Проверяем папку, где находится сам скрипт (для PyInstaller)
        if getattr(sys, 'frozen', False):
            # Запущено как собранное приложение
            app_path = Path(sys.executable).parent
            local_bin_frozen = app_path / "bin"
            if local_bin_frozen.exists() and any(local_bin_frozen.glob("st-info*")):
                return local_bin_frozen
        
        # 3. Проверяем папку с бинарниками через переменную окружения
        env_bin = os.environ.get('STLINK_BIN_PATH')
        if env_bin:
            env_bin_path = Path(env_bin)
            if env_bin_path.exists() and any(env_bin_path.glob("st-info*")):
                return env_bin_path
        
        # 4. Если ничего не нашли, возвращаем None (будем искать в PATH)
        return None
    
    def _get_st_command_path(self, command: str) -> Optional[Path]:
        """
        Возвращает полный путь к команде ST-Link.
        """
        # Добавляем .exe для Windows
        if sys.platform == 'win32' and not command.endswith('.exe'):
            command_exe = command + '.exe'
        else:
            command_exe = command
        
        # Проверяем локальную папку
        if self.stlink_bin_path:
            local_path = self.stlink_bin_path / command_exe
            if local_path.exists():
                return local_path
        
        # Проверяем системный PATH через which/where
        try:
            import shutil
            system_path = shutil.which(command)
            if system_path:
                return Path(system_path)
        except Exception:
            pass
        
        return None
    
    def _run_st_command(self, args: list, timeout: int = 10, check: bool = True) -> subprocess.CompletedProcess:
        """
        Запускает команду ST-Link, используя локальные файлы или системные.
        """
        command = args[0]
        cmd_args = args[1:] if len(args) > 1 else []
        
        # Пытаемся найти команду
        cmd_path = self._get_st_command_path(command)
        
        if cmd_path:
            cmd = [str(cmd_path)] + cmd_args
        else:
            # Если не нашли, пробуем использовать как есть (может быть в PATH)
            cmd = args
        
        # Добавляем .exe для Windows если нужно
        if sys.platform == 'win32' and not cmd[0].endswith('.exe'):
            cmd[0] = cmd[0] + '.exe'
        
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check
        )
    
    def _check_stlink_available(self) -> bool:
        """Проверяет, доступен ли ST-Link (локально или в системе)."""
        try:
            # Проверяем через st-info --version
            result = self._run_st_command(
                ["st-info", "--version"],
                timeout=5,
                check=False
            )
            return result.returncode == 0
        except Exception:
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
            result = self._run_st_command(
                ["st-info", "--version"],
                timeout=5,
                check=True
            )
            info["version"] = result.stdout.strip()
            
            # Проверяем через probe, есть ли подключенное устройство
            result = self._run_st_command(
                ["st-info", "--probe"],
                timeout=5,
                check=True
            )
            if "Found 1 stlink programmers" in result.stdout:
                info["connected"] = True
                
        except Exception:
            pass
            
        return info
    
    def _run_st_info(self, arg: str) -> str:
        """Выполняет одну команду st-info и возвращает вывод."""
        try:
            result = self._run_st_command(
                ["st-info", arg],
                timeout=5,
                check=True
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
            return False, "ST-Link не найден. Установите st-link (https://github.com/stlink-org/stlink) или добавьте бинарники в папку bin"
        
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
            verify: Проверять после прошивки (всегда False)
            
        Returns:
            (success, message)
        """
        if not self._connected:
            return False, "Устройство не подключено"
        
        if not Path(firmware_path).exists():
            return False, f"Файл прошивки не найден: {firmware_path}"
        
        try:
            # Формируем команду БЕЗ verify
            # st-flash write <path> <addr>
            cmd = ["st-flash", "write", firmware_path, "0x08000000"]
            
            # Выполняем прошивку через _run_st_command
            result = self._run_st_command(
                cmd,
                timeout=120,
                check=True
            )
            
            # Проверяем вывод на ошибки
            if "error" in result.stdout.lower() or "failed" in result.stdout.lower():
                return False, "Ошибка при прошивке"
            
            # После успешной прошивки выполняем сброс
            try:
                self._run_st_command(
                    ["st-flash", "reset"],
                    timeout=5,
                    check=False
                )
            except Exception:
                pass
            
            return True, "Прошивка успешно завершена, устройство сброшено"
            
        except subprocess.TimeoutExpired:
            return False, "Таймаут прошивки. Проверьте подключение устройства"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
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