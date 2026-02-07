"""
Interfaz web para evaluación visual
Permite subir imágenes y obtener evaluación
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from evaluate_visual import evaluate_design_from_images, analyze_design_screenshot
from config import Config

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/evaluate_visual', methods=['POST'])
def api_evaluate_visual():
    """Endpoint para evaluar diseños con imágenes"""
    try:
        if 'reference_image' not in request.files or 'candidate_image' not in request.files:
            return jsonify({"error": "Se requieren ambas imágenes"}), 400
        
        ref_file = request.files['reference_image']
        cand_file = request.files['candidate_image']
        
        if ref_file.filename == '' or cand_file.filename == '':
            return jsonify({"error": "Archivos vacíos"}), 400
        
        if not (allowed_file(ref_file.filename) and allowed_file(cand_file.filename)):
            return jsonify({"error": "Formato de imagen no válido"}), 400
        
        # Guardar archivos
        ref_filename = secure_filename(ref_file.filename)
        cand_filename = secure_filename(cand_file.filename)
        
        ref_path = os.path.join(app.config['UPLOAD_FOLDER'], 'ref_' + ref_filename)
        cand_path = os.path.join(app.config['UPLOAD_FOLDER'], 'cand_' + cand_filename)
        
        ref_file.save(ref_path)
        cand_file.save(cand_path)
        
        print(f"\n📁 Archivos guardados:")
        print(f"   Referencia: {ref_path}")
        print(f"   Candidato: {cand_path}")
        
        # Evaluar
        result = evaluate_design_from_images(ref_path, cand_path)
        
        if result:
            return jsonify({
                "success": True,
                "score": result['score'],
                "deviations": result['comparison']['deviations'],
                "assessment": result['comparison'].get('overall_assessment'),
                "strengths": result['comparison'].get('strengths', []),
                "weaknesses": result['comparison'].get('weaknesses', []),
                "confidence": result['comparison'].get('comparison_confidence')
            })
        else:
            return jsonify({"error": "Evaluación falló"}), 500
            
    except Exception as e:
        print(f"❌ Error en evaluación: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not Config.validate():
        print("❌ Configura tu .env antes de iniciar el servidor")
        exit(1)
    
    print("\n" + "="*60)
    print("🚀 SERVIDOR DE EVALUACIÓN VISUAL")
    print("="*60)
    print("\n📍 Abre en tu navegador: http://localhost:5000")
    print("\n💡 Arrastra y suelta imágenes para evaluar")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
