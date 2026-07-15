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
        Проверяет встроенную папку bin или системный PATH.
        """
        # 1. Папка bin рядом с исполняемым файлом (для собранного приложения)
        if getattr(sys, 'frozen', False):
            app_dir = Path(sys.executable).parent
            bin_path = app_dir / "bin"
            if bin_path.exists():
                # Проверяем наличие st-info
                st_info_path = bin_path / ("st-info.exe" if sys.platform == 'win32' else "st-info")
                if st_info_path.exists():
                    print(f"[DEBUG] ST-Link бинарники найдены в: {bin_path}")
                    return bin_path
        
        # 2. Папка bin в папке с приложением (для разработки)
        bin_path = Path(__file__).parent / "bin"
        if bin_path.exists():
            st_info_path = bin_path / ("st-info.exe" if sys.platform == 'win32' else "st-info")
            if st_info_path.exists():
                print(f"[DEBUG] ST-Link бинарники найдены в: {bin_path}")
                return bin_path
        
        # 3. Проверяем родительскую папку
        bin_path = Path(__file__).parent.parent / "bin"
        if bin_path.exists():
            st_info_path = bin_path / ("st-info.exe" if sys.platform == 'win32' else "st-info")
            if st_info_path.exists():
                print(f"[DEBUG] ST-Link бинарники найдены в: {bin_path}")
                return bin_path
        
        print("[DEBUG] ST-Link бинарники не найдены в папке bin, будет использован системный PATH")
        return None
    
    def _check_stlink_available(self) -> bool:
        """Проверяет, доступен ли ST-Link (локально или в системе)."""
        # 1. Проверяем локальные бинарники
        if self.stlink_bin_path:
            try:
                st_info_path = self.stlink_bin_path / ("st-info.exe" if sys.platform == 'win32' else "st-info")
                if st_info_path.exists():
                    result = subprocess.run(
                        [str(st_info_path), "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print("[DEBUG] ST-Link работает из локальной папки")
                        return True
            except Exception:
                pass
        
        # 2. Проверяем системный PATH (fallback)
        try:
            result = subprocess.run(
                ["st-info", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("[DEBUG] ST-Link работает из системного PATH")
                return True
        except Exception:
            pass
        
        print("[DEBUG] ST-Link не найден")
        return False
    
    def _run_st_command(self, args: list, timeout: int = 10, check: bool = True) -> subprocess.CompletedProcess:
        """Запускает команду ST-Link, используя локальные файлы или системные."""
        command = args[0]
        cmd_args = args[1:] if len(args) > 1 else []
        
        cmd = []
        
        # Если есть локальная папка, пробуем использовать локальный бинарник
        if self.stlink_bin_path:
            if sys.platform == 'win32':
                cmd_path = self.stlink_bin_path / f"{command}.exe"
            else:
                cmd_path = self.stlink_bin_path / command
            
            if cmd_path.exists():
                cmd = [str(cmd_path)] + cmd_args
                return subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=check
                )
        
        # Если локальный бинарник не найден, используем системный
        cmd = args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check
        )
    
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
            return False, "ST-Link не найден. Установите st-link (https://github.com/stlink-org/stlink)"
        
        try:
            chipid = self._run_st_info("--chipid")
            serial = self._run_st_info("--serial")
            flash = self._run_st_info("--flash")
            sram = self._run_st_info("--sram")
            descr = self._run_st_info("--descr")
            
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
    
    def flash(self, firmware_path: str) -> Tuple[bool, str]:
        """
        Прошивает устройство.
        
        Args:
            firmware_path: Путь к файлу прошивки
            
        Returns:
            (success, message)
        """
        if not self._connected:
            return False, "Устройство не подключено"
        
        if not Path(firmware_path).exists():
            return False, f"Файл прошивки не найден: {firmware_path}"
        
        try:
            # Используем локальные бинарники или системные через _run_st_command
            result = self._run_st_command(
                ["st-flash", "write", firmware_path, "0x08000000"],
                timeout=120,
                check=True
            )
            
            if "error" in result.stdout.lower() or "failed" in result.stdout.lower():
                return False, "Ошибка при прошивке"
            
            # Сброс
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