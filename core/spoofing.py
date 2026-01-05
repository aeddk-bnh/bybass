"""
Module: EXIF Metadata Spoofing
Purpose: Manipulate image metadata to simulate mobile device capture
Technology: ExifTool wrapper via subprocess
"""

import subprocess
import os
import json
from typing import Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataSpoofing:
    """
    Manipulates EXIF metadata to make synthesized images appear
    as if captured by real mobile devices
    """
    
    # Common device profiles
    DEVICE_PROFILES = {
        'iphone_13_pro': {
            'Make': 'Apple',
            'Model': 'iPhone 13 Pro',
            'Software': 'iOS 17.1.1',
            'LensModel': 'iPhone 13 Pro back camera 5.7mm f/1.5',
            'LensMake': 'Apple',
            'FocalLength': '5.7 mm',
            'FNumber': 1.5,
            'ISO': 80,
            'ExposureTime': '1/120',
            'Flash': 'Off, Did not fire',
            'WhiteBalance': 'Auto',
            'ColorSpace': 'sRGB',
            'ExifImageWidth': 4032,
            'ExifImageHeight': 3024,
            'XResolution': 72,
            'YResolution': 72,
            'ResolutionUnit': 'inches'
        },
        'iphone_14': {
            'Make': 'Apple',
            'Model': 'iPhone 14',
            'Software': 'iOS 17.2',
            'LensModel': 'iPhone 14 back dual wide camera 6.86mm f/1.5',
            'LensMake': 'Apple',
            'FocalLength': '6.86 mm',
            'FNumber': 1.5,
            'ISO': 64,
            'ExposureTime': '1/100',
            'Flash': 'Off, Did not fire',
            'WhiteBalance': 'Auto'
        },
        'samsung_s23': {
            'Make': 'Samsung',
            'Model': 'SM-S911U',
            'Software': 'S23',
            'LensModel': 'Samsung S23 Ultra Rear Camera',
            'FocalLength': '6.4 mm',
            'FNumber': 1.8,
            'ISO': 50,
            'ExposureTime': '1/100',
            'Flash': 'Off, Did not fire',
            'WhiteBalance': 'Auto',
            'ColorSpace': 'sRGB'
        },
        'pixel_8_pro': {
            'Make': 'Google',
            'Model': 'Pixel 8 Pro',
            'Software': 'Android 14',
            'LensModel': 'Pixel 8 Pro Main Camera',
            'FocalLength': '6.9 mm',
            'FNumber': 1.68,
            'ISO': 55,
            'ExposureTime': '1/120',
            'Flash': 'Off',
            'WhiteBalance': 'Auto'
        }
    }
    
    def __init__(self, exiftool_path: str = 'exiftool'):
        """
        Initialize metadata spoofing
        
        Args:
            exiftool_path: Path to exiftool executable
        """
        self.exiftool_path = exiftool_path
        self._check_exiftool()
    
    def _check_exiftool(self):
        """Verify exiftool is installed and accessible"""
        try:
            result = subprocess.run(
                [self.exiftool_path, '-ver'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"ExifTool version: {result.stdout.strip()}")
            else:
                logger.warning("ExifTool not found. Install from https://exiftool.org/")
        except FileNotFoundError:
            logger.warning("ExifTool not found in PATH. Metadata spoofing will not work.")
        except Exception as e:
            logger.error(f"Error checking ExifTool: {e}")
    
    def strip_metadata(self, image_path: str) -> bool:
        """
        Remove all existing metadata from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if successful
        """
        try:
            subprocess.run(
                [self.exiftool_path, '-all=', '-overwrite_original', image_path],
                capture_output=True,
                check=True,
                timeout=30
            )
            logger.info(f"Stripped metadata from: {image_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to strip metadata: {e}")
            return False
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
    
    def apply_metadata(self, image_path: str, metadata: Dict[str, any]) -> bool:
        """
        Apply custom metadata to image
        
        Args:
            image_path: Path to image file
            metadata: Dictionary of EXIF tags and values
            
        Returns:
            True if successful
        """
        try:
            # Build exiftool command
            cmd = [self.exiftool_path, '-overwrite_original']
            
            for tag, value in metadata.items():
                cmd.append(f'-{tag}={value}')
            
            cmd.append(image_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            logger.info(f"Applied metadata to: {image_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to apply metadata: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
    
    def spoof_device(self, image_path: str, device: str = 'iphone_13_pro',
                    custom_metadata: Optional[Dict] = None) -> bool:
        """
        Spoof image metadata to simulate capture from specific device
        
        Args:
            image_path: Path to image file
            device: Device profile name from DEVICE_PROFILES
            custom_metadata: Additional metadata to apply
            
        Returns:
            True if successful
        """
        # Get device profile
        if device not in self.DEVICE_PROFILES:
            logger.warning(f"Unknown device: {device}. Using iphone_13_pro")
            device = 'iphone_13_pro'
        
        metadata = self.DEVICE_PROFILES[device].copy()
        
        # Add timestamp (recent)
        now = datetime.now()
        timestamp = now.strftime('%Y:%m:%d %H:%M:%S')
        metadata['DateTimeOriginal'] = timestamp
        metadata['CreateDate'] = timestamp
        metadata['ModifyDate'] = timestamp
        
        # Add GPS data (optional, can be randomized)
        # Commenting out by default for privacy
        # metadata['GPSLatitude'] = '37.7749'
        # metadata['GPSLongitude'] = '-122.4194'
        # metadata['GPSLatitudeRef'] = 'N'
        # metadata['GPSLongitudeRef'] = 'W'
        
        # Merge custom metadata
        if custom_metadata:
            metadata.update(custom_metadata)
        
        # First strip existing metadata
        self.strip_metadata(image_path)
        
        # Apply new metadata
        success = self.apply_metadata(image_path, metadata)
        
        if success:
            logger.info(f"Spoofed device metadata: {device}")
        
        return success
    
    def read_metadata(self, image_path: str) -> Dict:
        """
        Read all metadata from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary of metadata tags
        """
        try:
            result = subprocess.run(
                [self.exiftool_path, '-j', image_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            metadata = json.loads(result.stdout)[0]
            logger.info(f"Read metadata from: {image_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to read metadata: {e}")
            return {}
    
    def spoof_realistic_photo(self, image_path: str, device: str = 'iphone_13_pro') -> bool:
        """
        Complete workflow: strip and apply realistic mobile device metadata
        
        Args:
            image_path: Path to image file
            device: Device profile to use
            
        Returns:
            True if successful
        """
        logger.info(f"Starting metadata spoofing for: {image_path}")
        
        # Custom adjustments for realism
        custom = {
            'Orientation': 'Horizontal (normal)',
            'YCbCrPositioning': 'Centered',
            'ExposureProgram': 'Program AE',
            'MeteringMode': 'Multi-segment',
            'SensingMethod': 'One-chip color area',
            'SceneCaptureType': 'Standard',
            'SubjectDistanceRange': 'Unknown'
        }
        
        return self.spoof_device(image_path, device, custom)
    
    @staticmethod
    def list_available_devices() -> list:
        """Get list of available device profiles"""
        return list(MetadataSpoofing.DEVICE_PROFILES.keys())


def main_example():
    """Example usage"""
    spoofing = MetadataSpoofing()
    
    # List available devices
    print("Available devices:")
    for device in spoofing.list_available_devices():
        print(f"  - {device}")
    
    # Spoof image metadata
    image_path = 'output/document_realistic.jpg'
    if os.path.exists(image_path):
        success = spoofing.spoof_realistic_photo(image_path, device='iphone_13_pro')
        
        if success:
            # Read and display metadata
            metadata = spoofing.read_metadata(image_path)
            print("\nApplied metadata:")
            for key in ['Make', 'Model', 'Software', 'DateTimeOriginal']:
                print(f"  {key}: {metadata.get(key, 'N/A')}")
    else:
        print(f"Image not found: {image_path}")


if __name__ == "__main__":
    main_example()
