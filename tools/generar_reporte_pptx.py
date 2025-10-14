import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conexion import conn, cursor
from pptx import Presentation


# ==========================================================
#   FUNCIONES AUXILIARES
# ==========================================================
def obtener_datos_solicitud_por_proyecto(proyecto_id):
    cursor.execute('''
        SELECT nombre_proponente, duracion, modalidad, nombre_programa,
               facultad_propuesta, facultad_proponente, cargo_proponente
        FROM datos_solicitud
        WHERE proyecto_id = %s
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


def reemplazar_texto_preservando_formato(shape, nuevo_valor):
    """
    Inserta o reemplaza el texto después de ':' sin borrar formato previo.
    Si no hay texto después de los ':', simplemente agrega el nuevo valor.
    Maneja colores y formatos ausentes sin errores.
    """
    if not shape.has_text_frame:
        return

    text_frame = shape.text_frame
    texto_actual = shape.text.strip()

    if ":" not in texto_actual:
        return

    etiqueta, _, valor_existente = texto_actual.partition(":")
    etiqueta = etiqueta.strip()
    valor_existente = valor_existente.strip()
    nuevo_texto = f" {nuevo_valor}"

    reemplazado = False

    for paragraph in text_frame.paragraphs:
        if not paragraph.runs:
            continue

        for run in paragraph.runs:
            if valor_existente and valor_existente in run.text:
                run.text = run.text.replace(valor_existente, nuevo_texto)
                reemplazado = True
                break
        if reemplazado:
            break

    # Si no se reemplazó (porque no había valor existente)
    if not reemplazado:
        p = text_frame.paragraphs[-1]
        run_base = p.runs[-1] if p.runs else p.add_run()
        nuevo_run = p.add_run()

        # Copiar formato de forma segura
        nuevo_run.font.bold = getattr(run_base.font, "bold", None)
        nuevo_run.font.size = getattr(run_base.font, "size", None)
        nuevo_run.font.name = getattr(run_base.font, "name", None)
        try:
            if run_base.font.color and hasattr(run_base.font.color, "rgb"):
                nuevo_run.font.color.rgb = run_base.font.color.rgb
        except Exception:
            pass

        nuevo_run.text = nuevo_texto


# ==========================================================
#   GENERAR REPORTE DE VIABILIDAD
# ==========================================================
def generar_reporte(proyecto_id, viabilidad=None):
    datos = obtener_datos_solicitud_por_proyecto(proyecto_id)
    if not datos:
        print("No se encontraron datos para la solicitud.")
        return

    # Seleccionar plantilla según viabilidad
    if viabilidad is not None:
        if viabilidad <= 60:
            template_path = 'files/base/NoViable.pptx'
        elif viabilidad <= 70:
            template_path = 'files/base/Revision.pptx'
        else:
            template_path = 'files/base/Viable.pptx'
    else:
        template_path = 'files/base/Viable.pptx'

    prs = Presentation(template_path)
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
        try:
            shape = slide.shapes[idx]
            reemplazar_texto_preservando_formato(shape, datos[col])
        except Exception as e:
            print(f"Error procesando shape {idx}: {e}")

    # Reemplazar viabilidad en el slide 3
    if viabilidad is not None:
        try:
            slide_img = prs.slides[3]
            shape_viabilidad = slide_img.shapes[11]
            reemplazar_texto_preservando_formato(shape_viabilidad, f"{viabilidad:.1f}%")
        except Exception as e:
            print(f"No se pudo reemplazar la viabilidad en el slide 3: {e}")

    # Reemplazar imagen radar (slide 3)
    try:
        slide_img = prs.slides[3]
        for shape in slide_img.shapes:
            if shape.shape_type == 13:  # Picture
                left, top, width, height = shape.left, shape.top, shape.width, shape.height
                slide_img.shapes._spTree.remove(shape._element)
                ruta_img = f"files/imagenes/grafico_radar_{proyecto_id}.png"
                slide_img.shapes.add_picture(ruta_img, left, top, width, height)
                break
    except Exception as e:
        print(f"No se pudo reemplazar la imagen en el slide 3: {e}")

    nombre_archivo = f"{datos['nombre_programa'].replace(' ', '_')}_viabilidad.pptx"
    output_path = os.path.join('files/presentaciones', nombre_archivo)
    prs.save(output_path)
    print(f"Reporte guardado en: {output_path}")
    return output_path


# ==========================================================
#   GENERAR REPORTE DE MERCADO
# ==========================================================
def generar_reporte_mercado(proyecto_id):
    """
    Genera un reporte de investigación de mercado respetando los formatos
    y reemplazando solo el contenido después de los ':'.
    """
    datos = obtener_datos_solicitud_por_proyecto(proyecto_id)
    if not datos:
        print("No se encontraron datos para la solicitud.")
        return

    template_path = 'files/base/InvestigacionMercados.pptx'
    prs = Presentation(template_path)

    slide_index = 1
    if slide_index >= len(prs.slides):
        slide_index = len(prs.slides) - 1
    slide = prs.slides[slide_index]

    # Según tu nuevo inspect, estos son los índices correctos
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
        try:
            shape = slide.shapes[idx]
            reemplazar_texto_preservando_formato(shape, datos[col])
        except Exception as e:
            print(f"Error procesando shape {idx}: {e}")

    nombre_archivo = f"{datos['nombre_programa'].replace(' ', '_')}_mercado.pptx"
    output_path = os.path.join('files/presentaciones', nombre_archivo)
    prs.save(output_path)
    print(f"Reporte de mercado guardado en: {output_path}")
    return output_path


# ==========================================================
#   MAIN (prueba rápida)
# ==========================================================
if __name__ == "__main__":
    proyecto_id = 1  # Cambia esto según tu caso
    generar_reporte(proyecto_id)
    generar_reporte_mercado(proyecto_id)
