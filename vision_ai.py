"""
Vision AI Module for Axon AI
Provides: Image Recognition, OCR, Face Detection, Object Detection
Uses: OpenCV, Tesseract OCR, Hugging Face Vision Models (Free), Transformers
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import requests
import json
import os
from datetime import datetime
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Transformers/Torch not available. Advanced vision features disabled.")
except OSError:
    TRANSFORMERS_AVAILABLE = False
    print("Torch DLL load failed. Advanced vision features disabled.")

try:
    # Configure Tesseract path - check common locations
    import os
    
    # Common installation paths
    _tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        os.path.join(os.getenv('LOCALAPPDATA', ''), r'Programs\Tesseract-OCR\tesseract.exe')
    ]
    
    _tesseract_found = False
    for _path in _tesseract_paths:
        if os.path.exists(_path):
            pytesseract.pytesseract.tesseract_cmd = _path
            _tesseract_found = True
            break
            
    TESSERACT_AVAILABLE = True
    if not _tesseract_found:
        print("Warning: Tesseract executable not found in common paths. OCR may fail if not in PATH.")

except ImportError:
    TESSERACT_AVAILABLE = False
    print("Tesseract not available. Install with: pip install pytesseract")


class ImageAnalyzer:
    """Analyzes images for objects, text, and faces"""
    
    def __init__(self, REMOVED_HF_TOKEN=None):
        self.REMOVED_HF_TOKEN = REMOVED_HF_TOKEN
        self.face_cascade = None
        self.detector = None
        self.DETECTION_AVAILABLE = False
        
        self._load_face_detector()
        self._load_object_detector()
        
    def _load_face_detector(self):
        """Load OpenCV face detection cascade"""
        try:
            # Try to load Haar Cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception as e:
            print(f"Face detector loading error: {e}")

    def _load_object_detector(self):
        """Load Transformers Object Detection model"""
        if not TRANSFORMERS_AVAILABLE:
            self.DETECTION_AVAILABLE = False
            return

        try:
            # Check if transformers is available
            self.detector = pipeline("object-detection", model="facebook/detr-resnet-50")
            self.DETECTION_AVAILABLE = True
            print("[OK] Object Detection Model Loaded")
        except Exception as e:
            print(f"[WARNING] Object Detection Model failed to load: {e}")
            self.DETECTION_AVAILABLE = False
    
    def detect_faces(self, image_path):
        """
        Detect faces in an image
        Returns: Number of faces and their locations
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return {'success': False, 'error': 'Could not read image'}
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            if self.face_cascade is not None:
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                
                return {
                    'success': True,
                    'face_count': len(faces),
                    'faces': [{'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)} 
                             for (x, y, w, h) in faces]
                }
            else:
                return {'success': False, 'error': 'Face detector not available'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def detect_objects(self, image_path):
        """
        Detect objects in the image using DETR
        """
        if not self.DETECTION_AVAILABLE:
            return {'success': False, 'error': 'Object Detection model not available'}
            
        try:
            # Use pipeline
            results = self.detector(image_path)
            
            # Count objects
            counts = {}
            objects_list = []
            
            for res in results:
                label = res['label']
                score = res['score']
                if score > 0.7:  # Confidence threshold
                    if label in counts:
                        counts[label] += 1
                    else:
                        counts[label] = 1
                        
            # Format list
            for label, count in counts.items():
                objects_list.append({'label': label, 'count': count})
                
            return {
                'success': True,
                'objects': objects_list,
                'raw_results': results
            }
            
        except Exception as e:
            print(f"Object detection error: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_text_ocr(self, image_path):
        """
        Extract text from image using OCR
        """
        if not TESSERACT_AVAILABLE:
            return {
                'success': False, 
                'error': 'Tesseract OCR not installed',
                'text': ''
            }
        
        try:
            # Open image
            img = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(img)
            
            return {
                'success': True,
                'text': text.strip(),
                'length': len(text.strip())
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'text': ''}
    
    def describe_image(self, image_path):
        """
        Generate description of image using Hugging Face Vision model
        """
        if not self.REMOVED_HF_TOKEN:
            return self._basic_image_analysis(image_path)
        
        try:
            # Use Hugging Face Image-to-Text model
            api_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
            headers = {"Authorization": f"Bearer {self.REMOVED_HF_TOKEN}"}
            
            # Read image as bytes
            with open(image_path, "rb") as f:
                data = f.read()
            
            response = requests.post(
                api_url, 
                headers=headers, 
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    description = result[0].get('generated_text', 'Unable to describe image')
                    return {
                        'success': True,
                        'description': description,
                        'method': 'huggingface'
                    }
            
            # Fallback to basic analysis
            return self._basic_image_analysis(image_path)
            
        except Exception as e:
            print(f"Image description error: {e}")
            return self._basic_image_analysis(image_path)
    
    def _basic_image_analysis(self, image_path):
        """Basic image analysis without AI (fallback)"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'success': False, 'error': 'Could not read image'}
            
            height, width, channels = img.shape
            
            # Detect dominant color
            avg_color = np.mean(img, axis=(0, 1))
            dominant_color = self._get_color_name(avg_color)
            
            # Basic description
            description = f"An image of size {width}x{height} pixels with {dominant_color} tones."
            
            # Check for text using OCR here as well to improve fallback
            ocr_res = self.extract_text_ocr(image_path)
            if ocr_res.get('success') and ocr_res.get('text'):
                 description += " It contains text."
            
            return {
                'success': True,
                'description': description,
                'method': 'basic',
                'dimensions': {'width': width, 'height': height},
                'dominant_color': dominant_color
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_color_name(self, bgr_color):
        """Get color name from BGR values"""
        b, g, r = bgr_color
        
        if r > 200 and g > 200 and b > 200:
            return "bright"
        elif r < 50 and g < 50 and b < 50:
            return "dark"
        elif r > g and r > b:
            return "reddish"
        elif g > r and g > b:
            return "greenish"
        elif b > r and b > g:
            return "bluish"
        else:
            return "neutral"
    
    def analyze_image_complete(self, image_path):
        """
        Complete image analysis: faces, text, description, objects
        """
        result = {
            'image_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }
        
        # Face detection
        face_result = self.detect_faces(image_path)
        result['analyses']['faces'] = face_result
        
        # Object Detection
        object_result = self.detect_objects(image_path)
        result['analyses']['objects'] = object_result
        
        # OCR
        ocr_result = self.extract_text_ocr(image_path)
        result['analyses']['ocr'] = ocr_result
        
        # Description
        desc_result = self.describe_image(image_path)
        result['analyses']['description'] = desc_result
        
        # Generate summary
        summary_parts = []
        
        # 1. Start with the AI description
        if desc_result.get('success'):
            summary_parts.append(desc_result.get('description', ''))
            
        # 2. Add Face info if significant
        if face_result.get('success') and face_result.get('face_count', 0) > 0:
            count = face_result['face_count']
            summary_parts.append(f"It contains {count} face{'s' if count > 1 else ''}")

        # 3. Add Object info
        if object_result.get('success') and object_result.get('objects'):
            obj_summary = []
            for obj in object_result['objects']:
                obj_summary.append(f"{obj['count']} {obj['label']}")
            if obj_summary:
                summary_parts.append("I also spotted: " + ", ".join(obj_summary))
        
        # 4. Add OCR Text
        if ocr_result.get('success') and ocr_result.get('text'):
            text = ocr_result['text'].strip()
            if text:
                if len(text) < 200:
                    summary_parts.append(f"The text in the image says: '{text}'")
                else:
                    summary_parts.append(f"The image contains this text: '{text[:200]}...'")
        
        result['summary'] = '. '.join(summary_parts) if summary_parts else "Image analyzed but no specific details found."
        
        return result


class QRCodeScanner:
    """Enhanced QR code and barcode scanning"""
    
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
    
    def scan_qr_code(self, image_path):
        """Scan QR code from image"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'success': False, 'error': 'Could not read image'}
            
            # Detect and decode QR code
            data, bbox, _ = self.detector.detectAndDecode(img)
            
            if data:
                return {
                    'success': True,
                    'data': data,
                    'type': 'QR Code'
                }
            else:
                return {
                    'success': False,
                    'error': 'No QR code found in image'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


class VisionAI:
    """Main Vision AI class combining all features"""
    
    def __init__(self, REMOVED_HF_TOKEN=None):
        self.image_analyzer = ImageAnalyzer(REMOVED_HF_TOKEN=REMOVED_HF_TOKEN)
        self.qr_scanner = QRCodeScanner()
        
    def analyze_image(self, image_path, analysis_type='complete'):
        """
        Analyze image based on type
        Types: 'complete', 'faces', 'text', 'description', 'qr'
        """
        if not os.path.exists(image_path):
            return {'success': False, 'error': 'Image file not found'}
        
        if analysis_type == 'complete':
            return self.image_analyzer.analyze_image_complete(image_path)
        elif analysis_type == 'faces':
            return self.image_analyzer.detect_faces(image_path)
        elif analysis_type == 'text' or analysis_type == 'ocr':
            return self.image_analyzer.extract_text_ocr(image_path)
        elif analysis_type == 'description':
            return self.image_analyzer.describe_image(image_path)
        elif analysis_type == 'qr':
            return self.qr_scanner.scan_qr_code(image_path)
        else:
            return {'success': False, 'error': f'Unknown analysis type: {analysis_type}'}
    
    def process_webcam_frame(self, detect_faces=True):
        """
        Capture and analyze frame from webcam
        """
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return {'success': False, 'error': 'Could not capture from webcam'}
            
            # Save temporary frame
            temp_path = 'temp_webcam_frame.jpg'
            cv2.imwrite(temp_path, frame)
            
            # Analyze based on options
            if detect_faces:
                result = self.image_analyzer.detect_faces(temp_path)
            else:
                result = self.image_analyzer.describe_image(temp_path)
            
            # Clean up
            try:
                os.remove(temp_path)
            except:
                pass
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Convenience functions
def create_vision_ai(REMOVED_HF_TOKEN=None):
    """Create and return VisionAI instance"""
    return VisionAI(REMOVED_HF_TOKEN=REMOVED_HF_TOKEN)


def analyze_image(image_path, REMOVED_HF_TOKEN=None, analysis_type='complete'):
    """Quick image analysis"""
    vision = VisionAI(REMOVED_HF_TOKEN=REMOVED_HF_TOKEN)
    return vision.analyze_image(image_path, analysis_type=analysis_type)


def detect_faces_in_image(image_path):
    """Quick face detection"""
    vision = VisionAI()
    return vision.analyze_image(image_path, analysis_type='faces')


def extract_text_from_image(image_path):
    """Quick OCR"""
    vision = VisionAI()
    return vision.analyze_image(image_path, analysis_type='text')


if __name__ == "__main__":
    # Test the module
    print("Testing Vision AI Module...\n")
    
    print("=== Vision AI Module ===")
    print("Available features:")
    print("1. Face Detection (OpenCV)")
    print("2. OCR - Text Extraction (Tesseract)")
    print("3. Image Description (Hugging Face)")
    print("4. QR Code Scanning (OpenCV)")
    print("5. Complete Image Analysis")
    print()
    
    # Note: Actual testing requires image files
    print("To test with an image:")
    print("  vision = create_vision_ai(REMOVED_HF_TOKEN='your_token')")
    print("  result = vision.analyze_image('path/to/image.jpg', 'complete')")
    print()
    
    print("Module loaded successfully!")
