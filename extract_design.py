"""
Extractor de estructura de diseños de Figma
Extrae datos estructurales (no visuales) de frames
"""
import requests
import json
from config import Config
from cache_manager import save_to_cache, load_from_cache
import time

def extract_figma_structure(file_key, figma_token, filter_prefix=None, use_cache=True):
    """
    Extrae la estructura de un archivo de Figma
    
    Args:
        file_key: ID del archivo de Figma
        figma_token: Token de autenticación
        filter_prefix: Filtrar frames que empiecen con este prefijo
    
    Returns:
        Lista de frames con sus métricas
    """
    # Intentar cargar desde caché primero
    if use_cache:
        cached_frames = load_from_cache(file_key)
        if cached_frames:
            return cached_frames
            
    headers = {'X-Figma-Token': figma_token}
    url = f'{Config.FIGMA_API_BASE}/files/{file_key}'
    
    print(f"🔍 Obteniendo archivo de Figma...")
    time.sleep(2)
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None
    
    data = response.json()
    frames = []
    
    def traverse_node(node, depth=0):
        """Recorre recursivamente el árbol de nodos"""
        node_type = node.get('type')
        node_name = node.get('name', '')
        
        # Solo procesar FRAMES con contenido
        if node_type == 'FRAME' and depth >= 1:
            # Aplicar filtro si existe
            if filter_prefix:
                if node_name.startswith(filter_prefix):
                    if has_meaningful_content(node):
                        frame_data = analyze_frame(node)
                        frames.append(frame_data)
                        print(f"  ✅ {node_name}")
            else:
                if has_meaningful_content(node):
                    frame_data = analyze_frame(node)
                    frames.append(frame_data)
                    print(f"  ✅ {node_name}")
        
        # Continuar con hijos
        for child in node.get('children', []):
            traverse_node(child, depth + 1)
    
    traverse_node(data['document'])
    return frames

def has_meaningful_content(node):
    """Verifica si un frame tiene contenido real"""
    text_count = count_text_nodes(node)
    return text_count > 0

def count_text_nodes(node, count=0):
    """Cuenta nodos de texto recursivamente"""
    if node.get('type') == 'TEXT':
        chars = node.get('characters', '').strip()
        if chars:
            count += 1
    
    for child in node.get('children', []):
        count = count_text_nodes(child, count)
    
    return count

def analyze_frame(frame):
    """
    Analiza un frame individual y extrae métricas
    
    Returns:
        Dict con métricas del frame
    """
    texts = []
    buttons = []
    inputs = 0
    has_progress = False
    images = 0
    
    def scan_children(node):
        """Escanea hijos del frame"""
        nonlocal inputs, has_progress, images
        
        node_type = node.get('type')
        node_name = node.get('name', '').lower()
        
        # Texto
        if node_type == 'TEXT':
            text_content = node.get('characters', '').strip()
            if text_content:
                texts.append(text_content)
        
        # Botones (por nombre o por componente)
        if any(keyword in node_name for keyword in ['button', 'btn', 'cta']):
            buttons.append(node.get('name'))
        
        # Inputs
        if any(keyword in node_name for keyword in ['input', 'field', 'textfield', 'textbox']):
            inputs += 1
        
        # Indicadores de progreso
        if any(keyword in node_name for keyword in ['progress', 'stepper', 'step', 'indicator', 'dots']):
            has_progress = True
        
        # Imágenes/ilustraciones
        if node_type in ['RECTANGLE', 'ELLIPSE', 'VECTOR'] and 'illustration' in node_name:
            images += 1
        
        # Recursión
        for child in node.get('children', []):
            scan_children(child)
    
    scan_children(frame)
    
    # Calcular palabra total
    word_count = sum(len(text.split()) for text in texts)
    
    return {
        "frame_name": frame.get('name'),
        "text_blocks": len(texts),
        "total_words": word_count,
        "buttons": buttons,
        "button_count": len(buttons),
        "has_progress": has_progress,
        "input_fields": inputs,
        "images": images
    }

def save_frames(frames, filepath=None):
    """Guarda frames extraídos en archivo JSON"""
    if filepath is None:
        filepath = Config.EXTRACTED_FRAMES_PATH
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(frames, indent=2, fp=f, ensure_ascii=False)
    
    print(f"\n💾 Guardado en: {filepath}")

if __name__ == "__main__":
    # Validar configuración
    if not Config.validate():
        exit(1)
    
    print("\n" + "="*60)
    print("🎨 EXTRACTOR DE DISEÑO DE FIGMA")
    print("="*60)
    
    # Menú de opciones
    print("\n📋 Modo de extracción:")
    print("1. Extraer frames de referencia (configurado en .env)")
    print("2. Extraer de otro archivo (custom)")
    
    choice = input("\nElige opción (1/2): ").strip()
    
    if choice == "2":
        file_key = input("File Key de Figma: ").strip()
        prefix = input("Prefijo de frames (Enter para todos): ").strip() or None
    else:
        file_key = Config.REFERENCE_FILE_KEY
        prefix = Config.REFERENCE_PREFIX
    
    print(f"\n🔍 Extrayendo frames...")
    if prefix:
        print(f"🎯 Filtro: '{prefix}'")
    print()
    
    frames = extract_figma_structure(
        file_key=file_key,
        figma_token=Config.FIGMA_TOKEN,
        filter_prefix=prefix
    )
    
    if frames:
        print(f"\n✅ {len(frames)} frames extraídos exitosamente!")
        print("\n" + "="*60)
        print("📊 RESUMEN:")
        print("="*60)
        
        for frame in frames:
            print(f"\n📱 {frame['frame_name']}")
            print(f"   • Palabras: {frame['total_words']}")
            print(f"   • Botones: {frame['button_count']}")
            print(f"   • Inputs: {frame['input_fields']}")
            print(f"   • Progreso: {'Sí' if frame['has_progress'] else 'No'}")
        
        # Guardar
        save_frames(frames)
        
        print("\n" + "="*60)
        print("✅ SIGUIENTE PASO: python generate_profile.py")
        print("="*60)
    else:
        print("\n❌ No se extrajeron frames")
        print("💡 Verifica el File Key y el prefijo")