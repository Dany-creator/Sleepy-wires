"""
Generador de perfiles de diseño
Agrega métricas de frames en un perfil unificado
"""
import json
from statistics import mean, median, stdev
from collections import Counter
from config import Config

def generate_design_profile(frames):
    """
    Genera un perfil agregado a partir de frames individuales
    
    Args:
        frames: Lista de frames analizados
    
    Returns:
        Dict con perfil del diseño
    """
    if not frames or len(frames) == 0:
        print("❌ No hay frames para analizar")
        return None
    
    # Extraer métricas
    word_counts = [f['total_words'] for f in frames]
    button_counts = [f['button_count'] for f in frames]
    input_counts = [f['input_fields'] for f in frames]
    progress_counts = [1 if f['has_progress'] else 0 for f in frames]
    
    # Agregar todos los botones
    all_buttons = []
    for f in frames:
        all_buttons.extend(f['buttons'])
    
    # Consistencia de botones (mismo patrón en todos los frames)
    button_patterns = [tuple(sorted(f['buttons'])) for f in frames]
    button_consistency = len(set(button_patterns)) <= 2  # Máximo 2 patrones diferentes
    
    # Crear perfil
    profile = {
        "metadata": {
            "total_frames": len(frames),
            "frame_names": [f['frame_name'] for f in frames]
        },
        "text_metrics": {
            "avg_words_per_screen": round(mean(word_counts), 1),
            "median_words": median(word_counts),
            "word_range": [min(word_counts), max(word_counts)],
            "word_std_dev": round(stdev(word_counts), 1) if len(word_counts) > 1 else 0
        },
        "interaction_metrics": {
            "avg_buttons_per_screen": round(mean(button_counts), 1),
            "button_consistency": button_consistency,
            "button_usage": dict(Counter(all_buttons)),
            "avg_input_fields": round(mean(input_counts), 1),
            "progress_indicator_usage": round(sum(progress_counts) / len(frames), 2)
        },
        "ux_patterns": {
            "has_consistent_cta": button_consistency,
            "uses_progress_indicators": any(progress_counts),
            "avg_cognitive_load": categorize_cognitive_load(mean(word_counts))
        }
    }
    
    return profile

def categorize_cognitive_load(avg_words):
    """Categoriza la carga cognitiva basada en palabras promedio"""
    if avg_words < 30:
        return "low"
    elif avg_words < 60:
        return "medium"
    else:
        return "high"

def save_profile(profile, filepath=None):
    """Guarda el perfil en archivo JSON"""
    if filepath is None:
        filepath = Config.REFERENCE_PROFILE_PATH
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(profile, indent=2, fp=f, ensure_ascii=False)
    
    print(f"💾 Perfil guardado en: {filepath}")

def load_frames(filepath=None):
    """Carga frames desde archivo JSON"""
    if filepath is None:
        filepath = Config.EXTRACTED_FRAMES_PATH
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {filepath}")
        print("💡 Ejecuta primero: python extract_design.py")
        return None

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📊 GENERADOR DE PERFIL DE DISEÑO")
    print("="*60)
    
    # Cargar frames
    print(f"\n🔍 Cargando frames desde {Config.EXTRACTED_FRAMES_PATH}...")
    frames = load_frames()
    
    if not frames:
        exit(1)
    
    print(f"✅ {len(frames)} frames cargados")
    
    # Generar perfil
    print("\n🧠 Generando perfil de diseño...")
    profile = generate_design_profile(frames)
    
    if profile:
        print("\n" + "="*60)
        print("📊 PERFIL GENERADO:")
        print("="*60)
        print(json.dumps(profile, indent=2, ensure_ascii=False))
        
        # Guardar
        save_profile(profile)
        
        print("\n" + "="*60)
        print("✅ PERFIL DE REFERENCIA CREADO")
        print("="*60)
        print("\n💡 Este es tu 'gold standard'")
        print("✅ SIGUIENTE PASO: python evaluate.py [FILE_KEY]")
        print("="*60)
    else:
        print("❌ Error generando perfil")