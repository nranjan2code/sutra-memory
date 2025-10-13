#!/usr/bin/env python3
"""
🥧 RASPBERRY PI CONFIGURATION
Optimized settings for biological intelligence on Pi 5 hardware.

This configuration ensures:
- No overheating (thermal management)
- Efficient memory usage (8GB RAM optimization)
- External HDD utilization (2TB storage)
- Remote access capabilities
"""

import os
import psutil
from pathlib import Path
from typing import Dict, Any


class PiConfig:
    """Configuration class optimized for Raspberry Pi 5."""
    
    # Hardware specifications
    TOTAL_RAM_GB = 8
    STORAGE_SD_GB = 64
    STORAGE_HDD_TB = 2
    CPU_CORES = 4
    
    # Thermal management
    TEMP_WARNING_C = 70    # Start throttling at 70°C
    TEMP_CRITICAL_C = 80   # Emergency shutdown at 80°C
    THERMAL_CHECK_INTERVAL = 30  # Check every 30 seconds
    
    # Performance settings (Pi-optimized)
    TRAINING_BATCH_SIZE = 5      # Smaller batches to prevent memory issues
    DREAM_INTERVAL = 600         # Dream every 10 minutes (vs 5 on desktop)
    MAINTENANCE_INTERVAL = 1200  # Maintenance every 20 minutes (vs 10)
    UPDATE_INTERVAL = 5          # GUI updates every 5 seconds (vs 2)
    MAX_CONCEPTS_MEMORY = 10000  # Limit in-memory concepts
    MAX_QUEUE_SIZE = 50          # Limit training queue size
    
    # Storage configuration
    SD_WORKSPACE = "/home/pi/biological_workspace"
    HDD_WORKSPACE = "/mnt/hdd/biological_intelligence"
    HDD_BACKUPS = "/mnt/hdd/biological_backups"
    
    # Network settings
    WEB_HOST = "0.0.0.0"  # Listen on all interfaces
    WEB_PORT = 8080
    WEBSOCKET_PORT = 8081
    
    # Service settings
    SERVICE_USER = "pi"
    SERVICE_GROUP = "pi"
    LOG_LEVEL = "INFO"
    LOG_MAX_SIZE_MB = 100  # Limit log files to 100MB
    
    @classmethod
    def get_cpu_temp(cls) -> float:
        """Get current CPU temperature in Celsius."""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
                return temp
        except:
            return 0.0
    
    @classmethod
    def get_memory_info(cls) -> Dict[str, float]:
        """Get memory usage information."""
        memory = psutil.virtual_memory()
        return {
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3),
            'used_gb': memory.used / (1024**3),
            'percent': memory.percent
        }
    
    @classmethod
    def get_disk_info(cls) -> Dict[str, Dict[str, float]]:
        """Get disk usage information."""
        info = {}
        
        # SD Card (root filesystem)
        try:
            sd_usage = psutil.disk_usage('/')
            info['sd_card'] = {
                'total_gb': sd_usage.total / (1024**3),
                'used_gb': sd_usage.used / (1024**3),
                'free_gb': sd_usage.free / (1024**3),
                'percent': (sd_usage.used / sd_usage.total) * 100
            }
        except:
            info['sd_card'] = {'error': 'Cannot read SD card'}
        
        # External HDD
        hdd_mount = "/mnt/hdd"
        if os.path.ismount(hdd_mount):
            try:
                hdd_usage = psutil.disk_usage(hdd_mount)
                info['hdd'] = {
                    'total_gb': hdd_usage.total / (1024**3),
                    'used_gb': hdd_usage.used / (1024**3),
                    'free_gb': hdd_usage.free / (1024**3),
                    'percent': (hdd_usage.used / hdd_usage.total) * 100
                }
            except:
                info['hdd'] = {'error': 'Cannot read HDD'}
        else:
            info['hdd'] = {'error': 'HDD not mounted'}
        
        return info
    
    @classmethod
    def is_thermal_throttling_needed(cls) -> bool:
        """Check if thermal throttling is needed."""
        temp = cls.get_cpu_temp()
        return temp > cls.TEMP_WARNING_C
    
    @classmethod
    def is_emergency_shutdown_needed(cls) -> bool:
        """Check if emergency thermal shutdown is needed."""
        temp = cls.get_cpu_temp()
        return temp > cls.TEMP_CRITICAL_C
    
    @classmethod
    def get_optimal_batch_size(cls) -> int:
        """Get optimal batch size based on current memory usage."""
        memory = cls.get_memory_info()
        
        if memory['percent'] > 80:
            return max(1, cls.TRAINING_BATCH_SIZE // 2)  # Halve batch size
        elif memory['percent'] > 60:
            return cls.TRAINING_BATCH_SIZE
        else:
            return min(10, cls.TRAINING_BATCH_SIZE * 2)  # Double batch size if plenty of memory
    
    @classmethod
    def setup_directories(cls):
        """Setup required directories."""
        directories = [
            cls.SD_WORKSPACE,
            cls.HDD_WORKSPACE,
            cls.HDD_BACKUPS,
            f"{cls.HDD_WORKSPACE}/english_biological_workspace",
            f"{cls.HDD_WORKSPACE}/biological_workspace",
            f"{cls.HDD_BACKUPS}/daily",
            f"{cls.HDD_BACKUPS}/weekly"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_system_status(cls) -> Dict[str, Any]:
        """Get comprehensive Pi system status."""
        return {
            'hardware': {
                'cpu_temp': cls.get_cpu_temp(),
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            },
            'memory': cls.get_memory_info(),
            'disk': cls.get_disk_info(),
            'thermal': {
                'throttling_needed': cls.is_thermal_throttling_needed(),
                'emergency_shutdown': cls.is_emergency_shutdown_needed(),
                'temp_warning': cls.TEMP_WARNING_C,
                'temp_critical': cls.TEMP_CRITICAL_C
            },
            'performance': {
                'optimal_batch_size': cls.get_optimal_batch_size(),
                'dream_interval': cls.DREAM_INTERVAL,
                'maintenance_interval': cls.MAINTENANCE_INTERVAL
            }
        }


# Pi-specific biological trainer configuration
PI_BIOLOGICAL_CONFIG = {
    'base_path': PiConfig.HDD_WORKSPACE,
    'use_full_swarm': True,  # Still use all 7 agents!
    'audit_enabled': True,
    'dream_interval': PiConfig.DREAM_INTERVAL,
    'maintenance_interval': PiConfig.MAINTENANCE_INTERVAL,
    'max_concepts_in_memory': PiConfig.MAX_CONCEPTS_MEMORY,
    'training_batch_size': PiConfig.TRAINING_BATCH_SIZE,
    'thermal_monitoring': True,
    'backup_enabled': True,
    'backup_path': PiConfig.HDD_BACKUPS
}


if __name__ == "__main__":
    # Test Pi configuration
    print("🥧 Raspberry Pi Configuration Test")
    print("=" * 50)
    
    status = PiConfig.get_system_status()
    
    print(f"🌡️  CPU Temperature: {status['hardware']['cpu_temp']:.1f}°C")
    print(f"🧠 Memory Usage: {status['memory']['used_gb']:.1f}GB / {status['memory']['total_gb']:.1f}GB ({status['memory']['percent']:.1f}%)")
    print(f"💾 SD Card: {status['disk']['sd_card'].get('used_gb', 0):.1f}GB used")
    
    if 'error' not in status['disk']['hdd']:
        print(f"🗄️  HDD: {status['disk']['hdd']['used_gb']:.1f}GB / {status['disk']['hdd']['total_gb']:.1f}GB")
    else:
        print(f"🗄️  HDD: {status['disk']['hdd']['error']}")
    
    print(f"⚡ Optimal Batch Size: {status['performance']['optimal_batch_size']}")
    
    if status['thermal']['throttling_needed']:
        print("🔥 THERMAL THROTTLING RECOMMENDED!")
    
    print("\n✅ Pi configuration loaded successfully!")