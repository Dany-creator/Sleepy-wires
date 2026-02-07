"""
Pipeline completo de evaluación
Orquesta todo el proceso de evaluación de diseño
"""
import sys
import json
from extract_design import extract_figma_structure, save_frames
from generate_profile import generate_design_profile
from compare_designs import compare_designs, calculate_score
from post_to_figma import post_evaluation_comments
from config import Config

def evaluate_design(candidate_file_key, post_comments=True, openai_key=None):
    """
    Ejecuta el pipeline completo de evaluación
    
    Args:
        candidate_file_key: File key del diseño a evaluar
        post_comments: Si debe publicar comentarios en Figma
        openai_key: (opcional) clave OpenAI proporcionada por el usuario para análisis visual
    
    Returns:
        Dict con resultados de la evaluación
    """
    print("\n" + "="*60)
    print("🎯 EVALUACIÓN DE DISEÑO")
    print("="*60)
    
    # 1. Cargar perfil de referencia
    print("\n📚 Paso 1: Cargar diseño de referencia...")
    try:
        with open(Config.REFERENCE_PROFILE_PATH, 'r', encoding='utf-8') as f:
            reference_profile = json.load(f)
        print(f"✅ Referencia cargada: {reference_profile['metadata']['total_frames']} frames")
    except FileNotFoundError:
        print("❌ Perfil de referencia no encontrado")
        print("💡 Ejecuta primero: python extract_design.py && python generate_profile.py")
        return None
    
    # 2. Extraer estructura del candidato
    print(f"\n🔍 Paso 2: Analizar diseño candidato ({candidate_file_key})...")
    candidate_frames = extract_figma_structure(
        file_key=candidate_file_key,
        figma_token=Config.FIGMA_TOKEN,
        filter_prefix=None,  # No filtrar, evaluar todo
        use_cache=True
    )
    
    if not candidate_frames:
        print("❌ No se pudieron extraer frames del diseño candidato")
        return None
    
    print(f"✅ {len(candidate_frames)} frames analizados")
    
    # 3. Generar perfil del candidato
    print("\n📊 Paso 3: Generar perfil del candidato...")
    candidate_profile = generate_design_profile(candidate_frames)
    
    if not candidate_profile:
        print("❌ Error generando perfil del candidato")
        return None
    
    print("✅ Perfil generado")
    
    # 4. Comparar con Claude
    print("\n🤖 Paso 4: Ejecutar comparación con IA...")
    comparison = compare_designs(reference_profile, candidate_profile)
    
    print(f"✅ Análisis completado")
    print(f"   Confianza: {comparison.get('comparison_confidence', 'unknown')}")
    print(f"   Desviaciones encontradas: {len(comparison.get('deviations', []))}")
    
    # 5. Calcular score
    print("\n🎯 Paso 5: Calcular puntuación...")
    score = calculate_score(
        reference_profile,
        candidate_profile,
        comparison.get('deviations', [])
    )
    print(f"✅ Score final: {score}/10")
    
    # 6. Publicar comentarios (opcional)
    if post_comments and comparison.get('deviations'):
        print("\n💬 Paso 6: Publicar comentarios en Figma...")
        comments_count = post_evaluation_comments(
            candidate_file_key,
            comparison['deviations'],
            score
        )
        print(f"✅ {comments_count} comentarios publicados")
    else:
        print("\n⏭️  Paso 6: Publicación de comentarios omitida")
    
    # Resultado final
    result = {
        "file_key": candidate_file_key,
        "score": score,
        "comparison": comparison,
        "candidate_profile": candidate_profile,
        "reference_profile": reference_profile
    }
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("📊 RESULTADOS DE LA EVALUACIÓN")
    print("="*60)
    print(f"\n🎯 Score: {score}/10")
    print(f"\n📋 Resumen: {comparison.get('overall_assessment', 'N/A')}")
    print(f"\n⚠️  Principales problemas:")
    
    for i, dev in enumerate(comparison.get('deviations', [])[:3], 1):
        print(f"\n{i}. {dev['area']} [{dev['severity']}]")
        print(f"   Referencia: {dev['reference_value']}")
        print(f"   Candidato: {dev['candidate_value']}")
        print(f"   💡 {dev['impact']}")
    
    print("\n" + "="*60)
    
    # Guardar resultados
    output_file = f"evaluation_{candidate_file_key[:8]}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, indent=2, fp=f, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    return result

if __name__ == "__main__":
    # Validar configuración
    if not Config.validate():
        exit(1)
    
    # Obtener file key del candidato
    if len(sys.argv) > 1:
        candidate_key = sys.argv[1]
    else:
        print("\n" + "="*60)
        print("🎨 EVALUADOR DE DISEÑO")
        print("="*60)
        candidate_key = input("\n📁 File Key del diseño a evaluar: ").strip()
    
    if not candidate_key:
        print("❌ File key requerido")
        print("\n💡 Uso: python evaluate.py [FILE_KEY]")
        print("   o ejecuta sin argumentos para modo interactivo")
        exit(1)
    
    # Preguntar si publicar comentarios
    post = input("\n💬 ¿Publicar comentarios en Figma? (s/n): ").strip().lower()
    post_comments = post == 's'
    
    # Ejecutar evaluación
    result = evaluate_design(candidate_key, post_comments)
    
    if result:
        print("\n✅ EVALUACIÓN COMPLETADA")
    else:
        print("\n❌ EVALUACIÓN FALLÓ")