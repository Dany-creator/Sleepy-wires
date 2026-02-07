"""
Publicador de comentarios en Figma
Publica feedback basado en comparaciones
"""
import requests
from config import Config

def post_figma_comment(file_key, message, node_id=None, x=0, y=0):
    """
    Publica un comentario en un archivo de Figma
    
    Args:
        file_key: ID del archivo
        message: Texto del comentario
        node_id: ID del nodo específico (opcional)
        x, y: Coordenadas del comentario
    
    Returns:
        bool: True si fue exitoso
    """
    headers = {
        'X-Figma-Token': Config.FIGMA_TOKEN,
        'Content-Type': 'application/json'
    }
    
    url = f'{Config.FIGMA_API_BASE}/files/{file_key}/comments'
    
    payload = {
        "message": message
    }
    
    # Agregar posición si se especifica un nodo
    if node_id:
        payload["client_meta"] = {
            "node_id": node_id,
            "x": x,
            "y": y
        }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return True
        else:
            print(f"⚠️  Error posting comment: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def post_evaluation_comments(file_key, deviations, score):
    """
    Publica comentarios de evaluación en Figma
    
    Args:
        file_key: ID del archivo a comentar
        deviations: Lista de desviaciones encontradas
        score: Score de la evaluación
    
    Returns:
        int: Número de comentarios publicados
    """
    comments_posted = 0
    
    # Comentario de resumen
    summary = f"""🎯 Evaluación de Diseño - Score: {score}/10

Este diseño fue comparado contra patrones de onboarding comprobados.

Principales hallazgos:
"""
    
    for i, dev in enumerate(deviations[:3], 1):  # Top 3
        summary += f"\n{i}. {dev['area']}: {dev['impact']}"
    
    if post_figma_comment(file_key, summary):
        comments_posted += 1
        print(f"  ✅ Comentario de resumen publicado")
    
    # Comentarios individuales por desviación
    for dev in deviations[:3]:
        detail_comment = f"""📊 Comparación: {dev['area']}

Referencia: {dev['reference_value']}
Este diseño: {dev['candidate_value']}

💡 Impacto: {dev['impact']}
⚠️  Severidad: {dev['severity']}
"""
        
        if post_figma_comment(file_key, detail_comment):
            comments_posted += 1
            print(f"  ✅ '{dev['area']}' publicado")
    
    return comments_posted

if __name__ == "__main__":
    print("\n🧪 Test de publicación en Figma")
    
    test_file = input("File Key para probar: ").strip()
    test_message = "🤖 Test de comentario automático desde Design Evaluator"
    
    if post_figma_comment(test_file, test_message):
        print("✅ Comentario de prueba publicado exitosamente")
    else:
        print("❌ Error publicando comentario")