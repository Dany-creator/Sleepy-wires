"""
Evaluador de diseño basado en análisis visual
Usa OpenAI Vision (GPT-4o) para analizar screenshots de diseños
"""

import json
import base64
import os
from pathlib import Path
from config import Config
from openai import OpenAI


def get_openai_client(api_key=None):
    """Return an OpenAI client using passed api_key or default from Config."""
    key = api_key or Config.OPENAI_API_KEY
    if not key:
        raise RuntimeError("OpenAI API key not provided")
    return OpenAI(api_key=key, project=getattr(Config, 'OPENAI_PROJECT_ID', None))


def encode_image(image_path):
    """Codifica imagen a base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyze_design_screenshot(image_path, is_reference=False, api_key=None):
    """
    Analiza un screenshot de diseño usando OpenAI Vision
    """
    image_base64 = encode_image(image_path)

    system_prompt = (
        "Eres un experto en UX/UI. Analiza esta pantalla de diseño y extrae métricas "
        "estructurales con precisión. Responde SOLO con JSON válido."
    )

    user_prompt = (
        "Este es un diseño de REFERENCIA (buen diseño)."
        if is_reference
        else "Este es un diseño CANDIDATO a evaluar."
    )

    try:
        client = get_openai_client(api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            },
                        },
                    ],
                },
            ],
            max_tokens=1500,
        )

        content = response.choices[0].message.content.strip()

        # Limpieza por si viene envuelto en ```json
        if "```" in content:
            content = content.split("```")[1]

        return json.loads(content)

    except Exception as e:
        print(f"❌ Error analizando imagen: {e}")
        return None


def compare_designs_visual(reference_analysis, candidate_analysis):
    """
    Compara dos diseños basándose en análisis visual
    """

    system_prompt = (
        "Eres un experto en UX/UI. Compara un diseño candidato contra uno de referencia "
        "y detecta diferencias relevantes. Responde SOLO con JSON válido."
    )

    user_prompt = f"""
DISEÑO DE REFERENCIA:
{json.dumps(reference_analysis, indent=2, ensure_ascii=False)}

DISEÑO CANDIDATO:
{json.dumps(candidate_analysis, indent=2, ensure_ascii=False)}
"""

    try:
        client = get_openai_client(api_key=None)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1500,
        )

        content = response.choices[0].message.content.strip()

        if "```" in content:
            content = content.split("```")[1]

        return json.loads(content)

    except Exception as e:
        print(f"❌ Error en comparación: {e}")
        return None


def calculate_visual_score(reference_analysis, candidate_analysis, comparison):
    """Calcula score basado en análisis visual"""

    score = 10.0

    # Carga cognitiva
    ref_load = reference_analysis["text_metrics"]["cognitive_load"]
    cand_load = candidate_analysis["text_metrics"]["cognitive_load"]

    load_scores = {"low": 0, "medium": 1, "high": 2}
    if load_scores.get(cand_load, 1) > load_scores.get(ref_load, 1) + 1:
        score -= 2.0

    # Jerarquía visual
    if candidate_analysis["visual_hierarchy"]["visual_balance"] == "poor":
        score -= 1.5

    # Consistencia
    if candidate_analysis["visual_hierarchy"]["spacing_consistency"] == "poor":
        score -= 1.0

    # Indicador de progreso
    if (
        reference_analysis["interaction_elements"]["has_progress_indicator"]
        and not candidate_analysis["interaction_elements"]["has_progress_indicator"]
    ):
        score -= 1.0

    # Penalizaciones por severidad
    for dev in comparison.get("deviations", []):
        severity = dev.get("severity", "low")
        if severity == "high":
            score -= 1.0
        elif severity == "medium":
            score -= 0.5

    return max(0, min(10, round(score, 1)))


def evaluate_design_from_images(reference_image_path, candidate_image_path, api_key=None):
    """
    Pipeline completo de evaluación basado en imágenes
    """

    print("\n🎨 EVALUACIÓN VISUAL DE DISEÑO")

    print("\n📚 Paso 1: Analizar diseño de referencia...")
    reference_analysis = analyze_design_screenshot(
        reference_image_path, is_reference=True, api_key=api_key
    )
    if not reference_analysis:
        return None

    print("✅ Referencia analizada")

    print("\n🔍 Paso 2: Analizar diseño candidato...")
    candidate_analysis = analyze_design_screenshot(
        candidate_image_path, is_reference=False, api_key=api_key
    )
    if not candidate_analysis:
        return None

    print("✅ Candidato analizado")

    print("\n🤖 Paso 3: Comparar diseños...")
    comparison = compare_designs_visual(reference_analysis, candidate_analysis)
    if not comparison:
        return None

    print("✅ Comparación completada")

    print("\n🎯 Paso 4: Calcular puntuación...")
    score = calculate_visual_score(
        reference_analysis, candidate_analysis, comparison
    )

    result = {
        "reference_image": reference_image_path,
        "candidate_image": candidate_image_path,
        "score": score,
        "comparison": comparison,
        "candidate_analysis": candidate_analysis,
        "reference_analysis": reference_analysis,
    }

    return result
