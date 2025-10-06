from pptx import Presentation

# Ruta de la plantilla
TEMPLATE_PATH = '../files/base/Viable.pptx'

# Cargar la presentación
prs = Presentation(TEMPLATE_PATH)

# Acceder a la diapositiva 3 (índice 3)
slide = prs.slides[3]

print('Textos de cada shape en la diapositiva 3:')
for i, shape in enumerate(slide.shapes):
    if shape.has_text_frame:
        print(f"Shape {i}: {shape.text}")
    elif shape.shape_type == 13:  # 13 es MSO_SHAPE_TYPE.PICTURE
        print(f"Shape {i}: [Imagen] - Tamaño: {shape.width}x{shape.height}, Posición: ({shape.left},{shape.top})")
