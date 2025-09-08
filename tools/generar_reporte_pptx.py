import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conexion import conn, cursor
from pptx import Presentation

TEMPLATE_PATH = 'db/Viable.pptx'

def obtener_datos_solicitud_por_proyecto(proyecto_id):
    cursor.execute('''
        SELECT nombre_proponente, duracion, modalidad, nombre_programa, facultad_propuesta, facultad_proponente, cargo_proponente
        FROM datos_solicitud
        WHERE proyecto_id = ?
    ''', (proyecto_id,))
    row = cursor.fetchone()
    if row:
        return {
            "nombre_proponente": row[0],
            "duracion": row[1],
            "modalidad": row[2],
            "nombre_programa": row[3],
            "facultad_propuesta": row[4],
            "facultad_proponente": row[5],
            "cargo_proponente": row[6]
        }
    else:
        return None

def generar_reporte(proyecto_id):
    datos = obtener_datos_solicitud_por_proyecto(proyecto_id)
    if not datos:
        print("No se encontraron datos para la solicitud.")
        return
    prs = Presentation(TEMPLATE_PATH)
    slide = prs.slides[1]
    shape_map = {
        1: "nombre_proponente",
        3: "duracion",
        4: "modalidad",
        5: "nombre_programa",
        10: "facultad_propuesta",
        11: "facultad_proponente",
        14: "cargo_proponente"
    }
    for idx, col in shape_map.items():
        shape = slide.shapes[idx]
        if shape.has_text_frame:
            partes = shape.text.split(":", 1)
            if len(partes) == 2:
                texto_actual = partes[1].strip()
                nuevo_texto = f" {datos[col]}"
                reemplazado = False
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if texto_actual in run.text:
                            run.text = run.text.replace(texto_actual, nuevo_texto)
                            reemplazado = True
                # Si no se encontró el texto en los runs, como fallback modifica el texto completo (no recomendado, pero evita que quede vacío)
                if not reemplazado:
                    shape.text = f"{partes[0]}:{nuevo_texto}"
                    
    # Reemplazar imagen en el slide 3 (índice 3)
    try:
        slide_img = prs.slides[3]
        # Encuentra el primer shape que sea imagen
        for shape in slide_img.shapes:
            if shape.shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
                left = shape.left
                top = shape.top
                width = shape.width
                height = shape.height
                # Elimina la imagen actual
                sp = slide_img.shapes._spTree
                sp.remove(shape._element)
                # Inserta la nueva imagen
                ruta_img = f"db/imagenes/grafico_radar_{proyecto_id}.png"
                slide_img.shapes.add_picture(ruta_img, left, top, width, height)
                break
    except Exception as e:
        print(f"No se pudo reemplazar la imagen en el slide 3: {e}")
    nombre_archivo = f"{datos['nombre_programa'].replace(' ', '_')}.pptx"
    output_path = os.path.join('db', nombre_archivo)
    prs.save(output_path)
    print(f"Reporte guardado en: {output_path}")

if __name__ == "__main__":
    proyecto_id = 1  # Cambia esto por el id de tu proyecto
    generar_reporte(proyecto_id)
