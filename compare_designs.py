"""
Comparador de diseños usando Claude
Compara un diseño candidato contra un diseño de referencia
"""
import anthropic
import json
from config import Config

def compare_designs(reference_profile, candidate_profile):
    """
    Usa Claude para comparar dos perfiles de diseño
    
    Args:
        reference_profile: Perfil del diseño de referencia
        candidate_profile: Perfil del diseño a evaluar
    
    Returns:
        Dict con análisis de desviaciones
    """
    client = anthropic.Anthropic(api_key=Config.ANTHROPIC_KEY)
    
    system_prompt = """Eres un asistente de comparación de diseños UX/UI.

REGLAS IMPORTANTES:
1. NO juzgues diseños de forma aislada
2. SOLO compara el diseño candidato contra el diseño de referencia
3. Cita diferencias numéricas específicas
4. Explica el impacto en la experiencia del usuario

Responde ÚNICAMENTE con JSON válido en este formato:
{
  "deviations": [
    {
      "area": "nombre específico de la métrica",
      "reference_value": "valor exacto de la referencia",
      "candidate_value": "valor exacto del candidato",
      "impact": "explicación breve del impacto en UX",
      "severity": "low|medium|high"
    }
  ],
  "overall_assessment": "evaluación en una oración",
  "comparison_confidence": "high|medium|low"
}

Si los perfiles son muy diferentes para comparar de forma significativa, usa "comparison_confidence": "low".
"""

    user_message = f"""Compara estos dos perfiles de diseño:

DISEÑO DE REFERENCIA (comprobado):
{json.dumps(reference_profile, indent=2, ensure_ascii=False)}

DISEÑO CANDIDATO (a evaluar):
{json.dumps(candidate_profile, indent=2, ensure_ascii=False)}

Identifica desviaciones significativas que podrían impactar la experiencia del usuario."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        response_text = message.content[0].text
        
        # Limpiar respuesta (remover markdown si existe)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        comparison = json.loads(response_text.strip())
        return comparison
        
    except Exception as e:
        print(f"❌ Error en comparación con Claude: {e}")
        return {
            "deviations": [],
            "overall_assessment": "Error en el análisis",
            "comparison_confidence": "low",
            "error": str(e)
        }

def calculate_score(reference_profile, candidate_profile, deviations):
    """
    Calcula un score determinístico basado en desviaciones
    
    Args:
        reference_profile: Perfil de referencia
        candidate_profile: Perfil candidato
        deviations: Lista de desviaciones encontradas por Claude
    
    Returns:
        Float entre 0-10
    """
    score = 10.0
    
    # Métricas de texto
    ref_words = reference_profile['text_metrics']['avg_words_per_screen']
    cand_words = candidate_profile['text_metrics']['avg_words_per_screen']
    
    # Penalizar exceso de texto (carga cognitiva)
    if cand_words > ref_words * 2:
        score -= 2.0
        print(f"  ⚠️  -2.0: Demasiado texto ({cand_words} vs {ref_words} palabras)")
    elif cand_words > ref_words * 1.5:
        score -= 1.0
        print(f"  ⚠️  -1.0: Texto elevado ({cand_words} vs {ref_words} palabras)")
    elif cand_words < ref_words * 0.5:
        score -= 1.5
        print(f"  ⚠️  -1.5: Muy poco texto ({cand_words} vs {ref_words} palabras)")
    
    # Penalizar falta de consistencia
    ref_consistent = reference_profile['interaction_metrics']['button_consistency']
    cand_consistent = candidate_profile['interaction_metrics']['button_consistency']
    
    if ref_consistent and not cand_consistent:
        score -= 1.5
        print(f"  ⚠️  -1.5: Botones inconsistentes")
    
    # Penalizar falta de indicadores de progreso
    ref_progress = reference_profile['interaction_metrics']['progress_indicator_usage']
    cand_progress = candidate_profile['interaction_metrics']['progress_indicator_usage']
    
    if ref_progress > 0.5 and cand_progress == 0:
        score -= 1.0
        print(f"  ⚠️  -1.0: Sin indicadores de progreso")
    
    # Penalizaciones basadas en severidad de Claude
    for dev in deviations:
        severity = dev.get('severity', 'low')
        if severity == 'high':
            score -= 1.0
            print(f"  ⚠️  -1.0: {dev['area']} (severidad alta)")
        elif severity == 'medium':
            score -= 0.5
            print(f"  ⚠️  -0.5: {dev['area']} (severidad media)")
    
    # Limitar entre 0 y 10
    final_score = max(0, min(10, score))
    
    return round(final_score, 1)

if __name__ == "__main__":
    # Test de comparación
    print("\n🧪 Modo de prueba - Comparador de Diseños")
    print("="*60)
    
    # Cargar perfil de referencia
    try:
        with open(Config.REFERENCE_PROFILE_PATH, 'r') as f:
            ref_profile = json.load(f)
        print("✅ Perfil de referencia cargado")
    except FileNotFoundError:
        print("❌ Perfil de referencia no encontrado")
        print("💡 Ejecuta: python generate_profile.py")
        exit(1)
    
    print("\n📊 Perfil de referencia:")
    print(f"  • Palabras promedio: {ref_profile['text_metrics']['avg_words_per_screen']}")
    print(f"  • Frames: {ref_profile['metadata']['total_frames']}")
    print(f"  • Consistencia: {ref_profile['interaction_metrics']['button_consistency']}")