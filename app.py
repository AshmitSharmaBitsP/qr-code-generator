from flask import Flask, request, jsonify
from flask_cors import CORS
import qrcode
from io import BytesIO
import base64
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class QRCodeService:
    """Service class to handle QR code generation"""
    
    @staticmethod
    def generate_qr_code(text, size=300):
        """
        Generate QR code from text
        
        Args:
            text (str): Text to encode in QR code
            size (int): Size of the QR code image
            
        Returns:
            PIL.Image: QR code image
        """
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,  # Controls the size of the QR code
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Add data to QR code
            qr.add_data(text)
            qr.make(fit=True)
            
            # Create image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Resize image to specified size
            qr_image = qr_image.resize((size, size), Image.Resampling.LANCZOS)
            
            return qr_image
            
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            raise
    
    @staticmethod
    def image_to_base64(image):
        """
        Convert PIL image to base64 string
        
        Args:
            image (PIL.Image): Image to convert
            
        Returns:
            str: Base64 encoded image string
        """
        try:
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Encode to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return image_base64
            
        except Exception as e:
            logger.error(f"Error converting image to base64: {str(e)}")
            raise

@app.route('/generate-qr', methods=['POST'])
def generate_qr():
    """
    Generate QR code endpoint
    
    Expected JSON payload:
    {
        "text": "Text to encode",
        "size": 300  # Optional, defaults to 300
    }
    
    Returns:
    {
        "success": true,
        "image": "base64_encoded_image",
        "text": "original_text",
        "size": 300
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Extract parameters
        text = data.get('text', '').strip()
        size = data.get('size', 300)
        
        # Validate input
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text is required'
            }), 400
        
        # Validate size
        if not isinstance(size, int) or size < 100 or size > 1000:
            return jsonify({
                'success': False,
                'error': 'Size must be an integer between 100 and 1000'
            }), 400
        
        # Log the request
        logger.info(f"Generating QR code for text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # Generate QR code
        qr_service = QRCodeService()
        qr_image = qr_service.generate_qr_code(text, size)
        
        # Convert to base64
        image_base64 = qr_service.image_to_base64(qr_image)
        
        # Return success response
        response = {
            'success': True,
            'image': image_base64,
            'text': text,
            'size': size,
            'message': 'QR code generated successfully'
        }
        
        logger.info("QR code generated successfully")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in generate_qr endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error occurred while generating QR code'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'QR Code Generator API is running'
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'QR Code Generator API',
        'version': '1.0.0',
        'endpoints': {
            'generate_qr': '/generate-qr (POST)',
            'health': '/health (GET)'
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("Starting QR Code Generator API...")
    print("API will be available at: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("Generate QR: POST http://localhost:8000/generate-qr")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )