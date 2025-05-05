from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from inference import predict

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image = request.files['image']
    
    if image.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        result = predict(image)
        return jsonify({
            'detections': result['detections'],
            'annotated_image': result['annotated_image']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
