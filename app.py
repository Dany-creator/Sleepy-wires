"""
Interfaz web para demostración
Flask app simple para evaluar diseños desde el navegador
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
from evaluate import evaluate_design
from config import Config
import uuid
from pathlib import Path

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Página principal"""
    # Serve the Figma-first UI
    return render_template('figma.html')


@app.route('/api/evaluate_visual', methods=['POST'])
def api_evaluate_visual():
    """Accepts multipart form with `reference_image`, `candidate_image`, optional `openai_key`"""
    try:
        if 'reference_image' not in request.files or 'candidate_image' not in request.files:
            return jsonify({'error': 'reference_image and candidate_image are required'}), 400

        ref = request.files['reference_image']
        cand = request.files['candidate_image']
        openai_key = request.form.get('openai_key') or request.values.get('openai_key')

        uploads_dir = Path('uploads')
        uploads_dir.mkdir(exist_ok=True)

        ref_name = f"ref_{uuid.uuid4().hex}{Path(ref.filename).suffix or '.png'}"
        cand_name = f"cand_{uuid.uuid4().hex}{Path(cand.filename).suffix or '.png'}"

        ref_path = uploads_dir / ref_name
        cand_path = uploads_dir / cand_name

        ref.save(str(ref_path))
        cand.save(str(cand_path))

        # lazy import to avoid heavy deps at app start
        from evaluate_visual import evaluate_design_from_images

        result = evaluate_design_from_images(str(ref_path), str(cand_path), api_key=openai_key)

        # cleanup: remove uploaded files
        try:
            ref_path.unlink(missing_ok=True)
            cand_path.unlink(missing_ok=True)
        except Exception:
            pass

        if not result:
            return jsonify({'error': 'evaluation failed'}), 500

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    """
    Endpoint para evaluar un diseño
    
    Body: {"file_key": "xxx", "post_comments": true}
    """
    try:
        data = request.json
        file_key = data.get('file_key')
        post_comments = data.get('post_comments', False)
        
        if not file_key:
            return jsonify({"error": "file_key requerido"}), 400
        
        # Ejecutar evaluación (acepta clave OpenAI opcional para análisis visual)
        openai_key = data.get('openai_key')
        result = evaluate_design(file_key, post_comments, openai_key)
        
        if result:
            return jsonify({
                "success": True,
                "score": result['score'],
                "deviations": result['comparison']['deviations'],
                "assessment": result['comparison'].get('overall_assessment'),
                "confidence": result['comparison'].get('comparison_confidence')
            })
        else:
            return jsonify({"error": "Evaluación falló"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reference')
def api_reference():
    """Devuelve información del diseño de referencia"""
    try:
        import json
        with open(Config.REFERENCE_PROFILE_PATH, 'r') as f:
            profile = json.load(f)
        
        return jsonify({
            "frames": profile['metadata']['total_frames'],
            "avg_words": profile['text_metrics']['avg_words_per_screen'],
            "has_progress": profile['ux_patterns']['uses_progress_indicators']
        })
    except:
        return jsonify({"error": "Referencia no encontrada"}), 404

if __name__ == '__main__':
    if not Config.validate():
        print("❌ Configura tu .env antes de iniciar el servidor")
        exit(1)
    
    print("\n" + "="*60)
    print("🚀 SERVIDOR DE EVALUACIÓN DE DISEÑO")
    print("="*60)
    print("\n📍 Abre en tu navegador: http://localhost:5000")
    print("\n💡 Ctrl+C para detener el servidor")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)