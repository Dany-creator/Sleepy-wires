def generate_profile(frames):
    """Frame data to design"""

    if not frames:
        return None
    
    word_counts = [f['total_words'] for f in frames]
    button_counts = [f['button_count'] for f in frames]
    all_buttons = [btn for f in frames for btn in f['buttons']]

    #Button position
    button_consistency = len(set([tuple(f['buttons']) for f in frames])) == 1

    profile = {
        "step_count": len(frames),
        "avg_words_per_ñscreen": sum(word_counts) / len(word_counts),
        "word_count_range": [min(word_counts), max(word_counts)],
        "avg_buttons_per_screen": sum(button_counts) / len(button_counts),
        "button_consistency": button_consistency,
        "progress_indicators_usage": sum(1 for f in frames if f['has_progress']) / len(frames),
        "avg_input_fields": sum(f['input_fields'] for f in frames) / len(frames),
        "component_usage": dict(Counter(all_buttons))
    }

    return profile

# Usage
from extract_design import figma_file

frames = extract_design(FILE_KEY, TOKEN)
profile = generate_profile(frames)

with open('reference_profile.json', 'w') as f:
    json.dump(profile, f, indent=2, fp=f)

print(" Reference profile saved")