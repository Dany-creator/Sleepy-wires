"""
Configuración centralizada del proyecto
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_PROJECT_ID = os.getenv("OPENAI_PROJECT_ID")
    
        # API Endpoints
    FIGMA_API_BASE = 'https://api.figma.com/v1'
    
    # Files
    REFERENCE_PROFILE_PATH = 'reference_profile.json'
    EXTRACTED_FRAMES_PATH = 'extracted_frames.json'
    
    @classmethod
    def validate(cls):
        """Valida que las configuraciones necesarias estén presentes"""

        
        # Para versión visual, solo necesitamos Anthropic Key
        if not Config.OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY no configurada")
            return False
        
        if not Config.OPENAI_PROJECT_ID:
            print("❌ OPENAI_PROJECT_ID no configurado")
            return False
        return True

if __name__ == "__main__":
    if Config.validate():
        print("✅ Configuración válida")
        print(f"🤖 Anthropic Key: {Config.ANTHROPIC_KEY[:20]}...")
        if Config.FIGMA_TOKEN:
            print(f"🎨 Figma Token: {Config.FIGMA_TOKEN[:20]}...")
    else:
        print("\n💡 Crea un archivo .env con tus credenciales")
        print("\nMínimo requerido para evaluación visual:")
        print("ANTHROPIC_KEY=tu_key_aqui")
