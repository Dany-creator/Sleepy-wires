"""
Sistema de caché para evitar rate limits de Figma
"""
import json
import os
from datetime import datetime, timedelta

CACHE_DIR = 'cache'
CACHE_DURATION = timedelta(hours=1)

def get_cache_path(file_key):
    """Genera path del archivo de caché"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{file_key}.json")

def save_to_cache(file_key, data):
    """
    Guarda datos en caché
    
    Args:
        file_key: ID del archivo de Figma
        data: Datos a guardar (frames extraídos)
    """
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'file_key': file_key,
        'data': data
    }
    
    cache_path = get_cache_path(file_key)
    
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Guardado en caché: {file_key}")

def load_from_cache(file_key):
    """
    Carga datos desde caché si son recientes
    
    Args:
        file_key: ID del archivo de Figma
    
    Returns:
        Datos cacheados o None si no hay caché válido
    """
    cache_path = get_cache_path(file_key)
    
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Verificar si el caché es reciente
        timestamp = datetime.fromisoformat(cache_data['timestamp'])
        age = datetime.now() - timestamp
        
        if age < CACHE_DURATION:
            minutes = age.seconds // 60
            print(f"✅ Usando caché ({minutes} minutos de antigüedad)")
            return cache_data['data']
        else:
            hours = age.seconds // 3600
            print(f"⚠️  Caché expirado ({hours} horas de antigüedad)")
            return None
            
    except Exception as e:
        print(f"⚠️  Error leyendo caché: {e}")
        return None

def clear_cache(file_key=None):
    """
    Limpia el caché
    
    Args:
        file_key: Si se especifica, solo limpia ese archivo. 
                  Si es None, limpia todo el caché.
    """
    if file_key:
        cache_path = get_cache_path(file_key)
        if os.path.exists(cache_path):
            os.remove(cache_path)
            print(f"🗑️  Caché eliminado: {file_key}")
    else:
        if os.path.exists(CACHE_DIR):
            for filename in os.listdir(CACHE_DIR):
                filepath = os.path.join(CACHE_DIR, filename)
                os.remove(filepath)
            print("🗑️  Todo el caché eliminado")

if __name__ == "__main__":
    print("🧪 Cache Manager - Utilidades")
    print("\n1. Ver archivos en caché")
    print("2. Limpiar todo el caché")
    print("3. Limpiar archivo específico")
    
    choice = input("\nOpción: ").strip()
    
    if choice == "1":
        if os.path.exists(CACHE_DIR):
            files = os.listdir(CACHE_DIR)
            if files:
                print(f"\n📦 {len(files)} archivo(s) en caché:")
                for f in files:
                    print(f"  • {f}")
            else:
                print("\n📦 Caché vacío")
        else:
            print("\n📦 No existe directorio de caché")
    
    elif choice == "2":
        confirm = input("¿Seguro? (s/n): ").strip().lower()
        if confirm == 's':
            clear_cache()
    
    elif choice == "3":
        file_key = input("File Key: ").strip()
        clear_cache(file_key)