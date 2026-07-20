"""Управление загрузкой прошивок из GitHub Releases."""

from __future__ import annotations

import json
import os
import shutil
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import zipfile
import re
import hashlib


class GitHubReleaseManager:
    """Класс для работы с GitHub Releases API."""
    
    def __init__(self, config_path: Path, storage_path: Path, token: Optional[str] = None):
        """
        Инициализация менеджера.
        
        Args:
            config_path: Путь к файлу конфигурации с репозиториями
            storage_path: Путь для хранения загруженных прошивок
            token: GitHub Personal Access Token (опционально)
        """
        self.config_path = config_path
        self.storage_path = storage_path
        self.token = token
        self.repositories = []
        self.max_releases = 10
        self._current_owner = ""
        self._current_repo = ""
        self.load_config()
        print(f"[DEBUG] GitHubReleaseManager config path: {self.config_path}")
        print(f"[DEBUG] GitHubReleaseManager config exists: {self.config_path.exists()}")
        
    def load_config(self):
        """Загружает конфигурацию из JSON файла."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.repositories = data.get('repositories', [])
                    settings = data.get('settings', {})
                    
                    if settings.get('local_storage'):
                        self.storage_path = Path.home() / settings['local_storage']
                    
                    self.max_releases = settings.get('max_releases_per_repo', 10)
                    print(f"[DEBUG] Loaded {len(self.repositories)} repositories")
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                self.repositories = []
        else:
            print(f"Файл конфигурации не найден: {self.config_path}")
            self.repositories = []
    
    def get_all_releases(self, progress_callback=None) -> List[Dict]:
        """
        Получает все релизы из всех репозиториев.
        
        Returns:
            Список прошивок с метаданными
        """
        all_firmware = []
        total = len(self.repositories)
        
        for idx, repo in enumerate(self.repositories, 1):
            if progress_callback:
                progress_callback(f"Загрузка {idx}/{total}: {repo['name']}")
            
            releases = self.get_repo_releases(repo)
            all_firmware.extend(releases)
        
        all_firmware.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        return all_firmware
    
    def get_repo_releases(self, repo: Dict) -> List[Dict]:
        """
        Получает релизы для одного репозитория через GitHub API.
        
        Args:
            repo: Словарь с информацией о репозитории
            
        Returns:
            Список прошивок
        """
        firmware_list = []
        repo_name = repo['name']
        repo_url = repo['url']
        device = repo.get('device', 'Unknown')
        pattern = repo.get('file_pattern', '*.elf')
        
        parts = repo_url.rstrip('/').split('/')
        self._current_owner = parts[-2]
        self._current_repo = parts[-1]
        
        api_url = f"https://api.github.com/repos/{self._current_owner}/{self._current_repo}/releases"
        
        try:
            headers = {
                "Accept": "application/vnd.github+json"
            }
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            response = requests.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()
            releases = response.json()
            
            releases = releases[:self.max_releases]
            
            for release in releases:
                tag_name = release.get('tag_name', 'unknown')
                published_at = release.get('published_at', '')
                release_name = release.get('name', tag_name)
                prerelease = release.get('prerelease', False)
                
                release_dir = self.storage_path / repo_name / tag_name
                
                assets = release.get('assets', [])
                for asset in assets:
                    asset_name = asset.get('name', '')
                    asset_id = asset.get('id')
                    asset_url = asset.get('browser_download_url', '')
                    
                    if re.search(pattern.replace('*', '.*'), asset_name):
                        local_path = self.download_asset(
                            asset_url, 
                            release_dir, 
                            asset_name,
                            asset_id=asset_id
                        )
                        
                        if local_path:
                            firmware_list.append({
                                'name': asset_name,
                                'path': str(local_path),
                                'version': tag_name,
                                'release_name': release_name,
                                'published_at': published_at,
                                'prerelease': prerelease,
                                'device': device,
                                'repo': repo_name,
                                'repo_url': repo_url,
                                'download_url': asset_url,
                                'asset_id': asset_id,
                                'size': asset.get('size', 0)
                            })
                
                for asset in assets:
                    asset_name = asset.get('name', '')
                    if asset_name.endswith('.zip'):
                        asset_id = asset.get('id')
                        zip_url = asset.get('browser_download_url', '')
                        zip_path = self.download_asset(
                            zip_url, 
                            release_dir, 
                            asset_name,
                            asset_id=asset_id
                        )
                        if zip_path:
                            extracted_files = self.extract_firmware_from_zip(
                                zip_path,
                                release_dir,
                                pattern
                            )
                            for fw in extracted_files:
                                firmware_list.append({
                                    'name': fw.name,
                                    'path': str(fw),
                                    'version': tag_name,
                                    'release_name': release_name,
                                    'published_at': published_at,
                                    'prerelease': prerelease,
                                    'device': device,
                                    'repo': repo_name,
                                    'repo_url': repo_url,
                                    'from_zip': True,
                                    'asset_id': asset_id
                                })
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка API для {repo_name}: {e}")
        except Exception as e:
            print(f"Ошибка при обработке {repo_name}: {e}")
        
        return firmware_list
    
    def download_asset(self, url: str, target_dir: Path, filename: str, asset_id: Optional[int] = None) -> Optional[Path]:
        """
        Скачивает файл с GitHub через API.
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / filename
        
        if file_path.exists():
            return file_path
        
        try:
            headers = {
                "Accept": "application/octet-stream",
                "User-Agent": "IntroSatToolbox/1.0"
            }
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            if asset_id and self._current_owner and self._current_repo:
                download_url = f"https://api.github.com/repos/{self._current_owner}/{self._current_repo}/releases/assets/{asset_id}"
                print(f"Скачивание через API: {download_url}")
            else:
                download_url = url
                print(f"Скачивание через browser URL: {download_url}")
            
            response = requests.get(download_url, headers=headers, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            
            return file_path
            
        except Exception as e:
            print(f"Ошибка скачивания {filename}: {e}")
            if file_path.exists():
                file_path.unlink()
            return None
    
    def extract_firmware_from_zip(self, zip_path: Path, extract_dir: Path, pattern: str) -> List[Path]:
        """
        Извлекает файлы прошивок из zip архива.
        """
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if re.search(pattern.replace('*', '.*'), file_info.filename):
                        extracted_path = zip_ref.extract(file_info, extract_dir)
                        extracted_files.append(Path(extracted_path))
        except Exception as e:
            print(f"Ошибка распаковки {zip_path}: {e}")
        
        return extracted_files
    
    def get_cached_firmware(self) -> List[Dict]:
        """
        Получает список локально кэшированных прошивок.
        """
        firmware_list = []
        
        if not self.storage_path.exists():
            return firmware_list
        
        for repo_dir in self.storage_path.iterdir():
            if not repo_dir.is_dir():
                continue
            
            for version_dir in repo_dir.iterdir():
                if not version_dir.is_dir():
                    continue
                
                for file_path in version_dir.glob('*.elf'):
                    firmware_list.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'version': version_dir.name,
                        'device': self._detect_device_from_path(repo_dir.name),
                        'repo': repo_dir.name,
                        'cached': True
                    })
                
                for file_path in version_dir.glob('*.bin'):
                    firmware_list.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'version': version_dir.name,
                        'device': self._detect_device_from_path(repo_dir.name),
                        'repo': repo_dir.name,
                        'cached': True
                    })
                
                for file_path in version_dir.glob('*.hex'):
                    firmware_list.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'version': version_dir.name,
                        'device': self._detect_device_from_path(repo_dir.name),
                        'repo': repo_dir.name,
                        'cached': True
                    })
        
        return firmware_list
    
    def _detect_device_from_path(self, path: str) -> str:
        """Определяет тип устройства из имени папки."""
        path_lower = path.lower()
        if 'stm' in path_lower:
            return 'STM32'
        elif 'atmega' in path_lower or 'mega' in path_lower:
            return 'ATmega'
        else:
            return 'Unknown'
    
    def cleanup_old_releases(self, keep_count: int = 10):
        """
        Удаляет старые версии прошивок.
        """
        if not self.storage_path.exists():
            return
        
        for repo_dir in self.storage_path.iterdir():
            if not repo_dir.is_dir():
                continue
            
            versions = [d for d in repo_dir.iterdir() if d.is_dir()]
            versions.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for version_dir in versions[keep_count:]:
                try:
                    shutil.rmtree(version_dir)
                    print(f"Удалена старая версия: {version_dir}")
                except Exception as e:
                    print(f"Ошибка удаления {version_dir}: {e}")