"""
Module: Image Processor
Purpose: Apply realistic aging effects to synthesized documents
Technology: OpenCV for perspective transform, noise, blur
"""

import cv2
import numpy as np
import random
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Applies various image transformations to make synthesized documents
    appear more realistic (as if photographed by mobile device)
    """
    
    def __init__(self):
        pass
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Load image from file"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        logger.info(f"Loaded image: {image_path} {img.shape}")
        return img
    
    def save_image(self, image: np.ndarray, output_path: str):
        """Save image to file"""
        cv2.imwrite(output_path, image)
        logger.info(f"Saved image: {output_path}")
    
    def perspective_transform(self, image: np.ndarray, 
                             angle_range: Tuple[float, float] = (-5, 5),
                             scale_range: Tuple[float, float] = (0.95, 1.0)) -> np.ndarray:
        """
        Apply perspective transformation to simulate angled photo
        
        Args:
            image: Input image
            angle_range: Min/max rotation angle in degrees
            scale_range: Min/max scale factor
            
        Returns:
            Transformed image
        """
        h, w = image.shape[:2]
        
        # Random rotation angle
        angle = random.uniform(*angle_range)
        
        # Random scale
        scale = random.uniform(*scale_range)
        
        # Get rotation matrix
        center = (w / 2, h / 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
        
        # Apply rotation
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h), 
                                borderMode=cv2.BORDER_REPLICATE)
        
        # Random perspective distortion
        pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        
        # Random offsets for perspective
        offset = random.randint(5, 20)
        pts2 = np.float32([
            [random.randint(0, offset), random.randint(0, offset)],
            [w - random.randint(0, offset), random.randint(0, offset)],
            [random.randint(0, offset), h - random.randint(0, offset)],
            [w - random.randint(0, offset), h - random.randint(0, offset)]
        ])
        
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        result = cv2.warpPerspective(rotated, matrix, (w, h), 
                                     borderMode=cv2.BORDER_REPLICATE)
        
        logger.info(f"Applied perspective transform (angle: {angle:.2f}°, scale: {scale:.2f})")
        return result
    
    def add_gaussian_noise(self, image: np.ndarray, 
                          mean: float = 0, std: float = 10) -> np.ndarray:
        """
        Add Gaussian noise to simulate camera sensor noise
        
        Args:
            image: Input image
            mean: Mean of noise distribution
            std: Standard deviation of noise
            
        Returns:
            Noisy image
        """
        noise = np.random.normal(mean, std, image.shape).astype(np.float32)
        noisy_image = cv2.add(image.astype(np.float32), noise)
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        
        logger.info(f"Added Gaussian noise (mean: {mean}, std: {std})")
        return noisy_image
    
    def apply_blur(self, image: np.ndarray, blur_type: str = 'gaussian',
                   kernel_size: int = 3) -> np.ndarray:
        """
        Apply blur to simulate camera focus issues
        
        Args:
            image: Input image
            blur_type: 'gaussian', 'motion', or 'median'
            kernel_size: Blur kernel size (must be odd)
            
        Returns:
            Blurred image
        """
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        if blur_type == 'gaussian':
            result = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif blur_type == 'motion':
            kernel = np.zeros((kernel_size, kernel_size))
            kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
            kernel = kernel / kernel_size
            result = cv2.filter2D(image, -1, kernel)
        elif blur_type == 'median':
            result = cv2.medianBlur(image, kernel_size)
        else:
            result = image
        
        logger.info(f"Applied {blur_type} blur (kernel: {kernel_size})")
        return result
    
    def adjust_brightness_contrast(self, image: np.ndarray,
                                   brightness: int = 0, 
                                   contrast: float = 1.0) -> np.ndarray:
        """
        Adjust brightness and contrast
        
        Args:
            image: Input image
            brightness: Brightness offset (-100 to 100)
            contrast: Contrast multiplier (0.5 to 1.5)
            
        Returns:
            Adjusted image
        """
        adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
        logger.info(f"Adjusted brightness: {brightness}, contrast: {contrast}")
        return adjusted
    
    def add_jpeg_compression(self, image: np.ndarray, 
                            quality: int = 85) -> np.ndarray:
        """
        Simulate JPEG compression artifacts
        
        Args:
            image: Input image
            quality: JPEG quality (0-100, lower = more artifacts)
            
        Returns:
            Compressed image
        """
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encoded = cv2.imencode('.jpg', image, encode_param)
        decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        
        logger.info(f"Applied JPEG compression (quality: {quality})")
        return decoded
    
    def add_shadow(self, image: np.ndarray, intensity: float = 0.3) -> np.ndarray:
        """
        Add subtle shadow effect to simulate lighting conditions
        
        Args:
            image: Input image
            intensity: Shadow intensity (0.0 to 1.0)
            
        Returns:
            Image with shadow
        """
        h, w = image.shape[:2]
        
        # Create gradient shadow
        shadow_mask = np.zeros((h, w), dtype=np.float32)
        cv2.ellipse(shadow_mask, (w//2, h//2), (w//3, h//3), 0, 0, 360, 1, -1)
        shadow_mask = cv2.GaussianBlur(shadow_mask, (99, 99), 50)
        shadow_mask = 1 - (shadow_mask * intensity)
        
        # Apply shadow
        result = image.copy().astype(np.float32)
        for c in range(3):
            result[:, :, c] = result[:, :, c] * shadow_mask
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        logger.info(f"Added shadow effect (intensity: {intensity})")
        return result
    
    def process_realistic_photo(self, image_path: str, output_path: str,
                                intensity: str = 'medium') -> str:
        """
        Complete processing pipeline to make document look like real photo
        
        Args:
            image_path: Input image path
            output_path: Output image path
            intensity: 'light', 'medium', or 'heavy'
            
        Returns:
            Path to processed image
        """
        # Load image
        img = self.load_image(image_path)
        
        # Set parameters based on intensity
        params = {
            'light': {
                'angle_range': (-2, 2),
                'noise_std': 5,
                'blur_kernel': 3,
                'jpeg_quality': 92,
                'brightness': random.randint(-5, 5),
                'contrast': random.uniform(0.95, 1.05)
            },
            'medium': {
                'angle_range': (-5, 5),
                'noise_std': 10,
                'blur_kernel': 3,
                'jpeg_quality': 85,
                'brightness': random.randint(-10, 10),
                'contrast': random.uniform(0.9, 1.1)
            },
            'heavy': {
                'angle_range': (-8, 8),
                'noise_std': 15,
                'blur_kernel': 5,
                'jpeg_quality': 75,
                'brightness': random.randint(-15, 15),
                'contrast': random.uniform(0.85, 1.15)
            }
        }
        
        p = params.get(intensity, params['medium'])
        
        # Apply transformations
        img = self.perspective_transform(img, angle_range=p['angle_range'])
        img = self.add_gaussian_noise(img, std=p['noise_std'])
        img = self.apply_blur(img, blur_type='gaussian', kernel_size=p['blur_kernel'])
        img = self.adjust_brightness_contrast(img, p['brightness'], p['contrast'])
        img = self.add_shadow(img, intensity=0.2)
        img = self.add_jpeg_compression(img, quality=p['jpeg_quality'])
        
        # Save result
        self.save_image(img, output_path)
        
        logger.info(f"Completed realistic photo processing: {output_path}")
        return output_path


def main_example():
    """Example usage"""
    processor = ImageProcessor()
    
    # Process an image
    processor.process_realistic_photo(
        image_path='output/document.png',
        output_path='output/document_realistic.jpg',
        intensity='medium'
    )


if __name__ == "__main__":
    main_example()
