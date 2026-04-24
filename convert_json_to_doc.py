import json
from docxtpl import DocxTemplate
from docx import Document
from docx.shared import Pt

def generate_resume_from_template(json_filepath: str, template_filepath: str, output_filepath: str):
    # 1. Load the Tailored JSON Data
    with open(json_filepath, 'r') as f:
        context = json.load(f)

    # 2. Pre-process the Technical Skills
    formatted_skills = []
    overrides = {
        'Ai Ml': 'Artificial Intelligence & Machine Learning',
        'Data Ml Engineering': 'Data & ML Engineering',
        'Web Api Development': 'Web & API Development'
    }
    
    for category, skills in context.get('technical_skills', {}).items():
        cat_name = category.replace('_', ' ').title()
        cat_name = overrides.get(cat_name, cat_name)

        formatted_skills.append({
        "skill_name": cat_name,
        "skill_text": ", ".join(skills)
        })
        
    context['formatted_skills'] = formatted_skills

    # 3. Load and Render the Template
    doc = DocxTemplate(template_filepath)
    doc.render(context)
    
    # Save a temporary version to process with standard python-docx
    temp_path = "temp_render.docx"
    doc.save(temp_path)

    # 4. POST-PROCESSING: Strip all paragraph spacing
    final_doc = Document(temp_path)
    for paragraph in final_doc.paragraphs:
        # Set spacing before and after to 0
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        # Set line spacing to strictly single (1.0)
        paragraph.paragraph_format.line_spacing = 1.0

    # 5. Save the final compact Document
    final_doc.save(output_filepath)
    print(f"Successfully created compact tailored resume: {output_filepath}")

# --- Example Usage ---
generate_resume_from_template(
    json_filepath='tailored_resume.json', 
    template_filepath='Ajay_Luhar_Demo_Resume.docx', 
    output_filepath='Ajay_Luhar_Tailored_Resume.docx'
)