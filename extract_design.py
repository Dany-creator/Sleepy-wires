import requests
import json
import os
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

# We estract the file of reference 
def figma_file(file_key, figma_token, filter_prefix=None):
    """Extract structural dat from the Figma"""

    headers = {'X-Figma-Token': figma_token}
    url = f'https://api.figma.com/v1/files/{file_key}'
    
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Figma API error {response.status_code}: {response.text}")

    data = response.json()

    if 'document' not in data:
        raise KeyError(f"'document' not found in response: {data}")


    frames = []

    def traverse_node(node, depth=0):
        node_type = node.get('type')
        node_name = node.get('name', '')
        
        # Solo extraer FRAMES (no componentes ni iconos)
        if node_type == 'FRAME' and depth >= 1:
            # Filtrar por prefijo si se especifica
            if filter_prefix:
                if node_name.startswith(filter_prefix):
                    frame_data = analyze_frame(node)
                    frames.append(frame_data)
                    print(f"  ✅ Extracted: {node_name}")
            else:
                # Si tiene contenido real (no es un icono vacío)
                if has_meaningful_content(node):
                    frame_data = analyze_frame(node)
                    frames.append(frame_data)
                    print(f"  ✅ Extracted: {node_name}")
        
        # Seguir recorriendo hijos
        for child in node.get('children', []):
            traverse_node(child, depth + 1)
    
    traverse_node(data['document'])
    return frames

#Now we search for the different elements in the frame, such as text, buttons, inputs and progress bars.
def has_meaningful_content(node):
    """Check if frame has actual content (not just an icon)"""
    text_count = count_text_nodes(node)
    # Un frame de onboarding debe tener al menos algo de texto
    return text_count > 0

def count_text_nodes(node, count=0):
    """Count text nodes recursively"""
    if node.get('type') == 'TEXT':
        count += 1
    for child in node.get('children', []):
        count = count_text_nodes(child, count)
    return count

def analyze_frame(frame):
    """Extract metrics from a single frame"""
    
    texts = []
    buttons = []
    inputs = 0
    has_progress = False
    
    def scan_children(node):
        nonlocal inputs, has_progress
        
        node_type = node.get('type')
        node_name = node.get('name', '').lower()
        
        # Detectar texto
        if node_type == 'TEXT':
            text_content = node.get('characters', '')
            if text_content.strip():  # Solo textos no vacíos
                texts.append(text_content)
        
        # Detectar botones
        if any(keyword in node_name for keyword in ['button', 'btn', 'cta']):
            buttons.append(node.get('name'))
        
        # Detectar inputs
        if any(keyword in node_name for keyword in ['input', 'field', 'textfield']):
            inputs += 1
        
        # Detectar indicadores de progreso
        if any(keyword in node_name for keyword in ['progress', 'stepper', 'step', 'indicator']):
            has_progress = True
        
        # Recorrer hijos
        for child in node.get('children', []):
            scan_children(child)
    
    scan_children(frame)
    
    word_count = sum(len(text.split()) for text in texts)
    
    return {
        "frame_name": frame.get('name'),
        "text_blocks": len(texts),
        "total_words": word_count,
        "buttons": buttons,
        "button_count": len(buttons),
        "has_progress": has_progress,
        "input_fields": inputs
    }

if __name__ == "__main__":
    FILE_KEY = "vv1gjwZnayFSAJ748JyR8K"
    TOKEN = os.getenv('FIGMA_TOKEN')
    
    if not TOKEN:
        print("❌ FIGMA_TOKEN not found in .env file!")
        exit(1)
    
    print("\n" + "="*60)
    print("🎨 FIGMA DESIGN EXTRACTOR")
    print("="*60)
    
    # Opción 1: Filtrar por prefijo específico
    print("\n📋 Choose extraction mode:")
    print("1. Extract only 'Finance Concept 01' screens (recommended)")
    print("2. Extract only 'App Concept 01' screens")
    print("3. Extract all screens with content")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        filter_prefix = "Finance Concept 01"
    elif choice == "2":
        filter_prefix = "App Concept 01"
    else:
        filter_prefix = None
    
    print(f"\n🔍 Extracting frames{f' starting with: {filter_prefix}' if filter_prefix else ''}...\n")
    
    frames = figma_file(FILE_KEY, TOKEN, filter_prefix)
    
    if frames:
        print(f"\n✅ Successfully extracted {len(frames)} frames!")
        print("\n" + "="*60)
        print("📊 RESULTS:")
        print("="*60 + "\n")
        print(json.dumps(frames, indent=2))
        
        # Guardar en archivo
        output_file = "extracted_frames.json"
        with open(output_file, 'w') as f:
            json.dump(frames, indent=2, fp=f)
        
        print(f"\n💾 Saved to: {output_file}")
    else:
        print("\n❌ No frames extracted")