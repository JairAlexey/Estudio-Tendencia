def actualizar_texto_preservando_formato(shape, nuevo_texto):
    """
    Actualiza el texto de un shape preservando el formato original (fuente, tamaño, color, etc.)
    """
    if not shape.has_text_frame:
        return

    # Obtener el formato del texto existente
    text_frame = shape.text_frame
    if not text_frame.paragraphs:
        return

    # Guardar las propiedades de formato del primer párrafo y run
    formato_original = None
    for paragraph in text_frame.paragraphs:
        if paragraph.runs:
            formato_original = paragraph.runs[0].font
            break
    
    # Limpiar todo el texto existente
    for paragraph in text_frame.paragraphs[1:]:
        paragraph._p.getparent().remove(paragraph._p)
    
    # Asegurarse de que hay al menos un párrafo
    if not text_frame.paragraphs:
        text_frame.clear()
        p = text_frame.add_paragraph()
    else:
        p = text_frame.paragraphs[0]
        p.clear()

    # Agregar el nuevo texto con el formato preservado
    run = p.add_run()
    run.text = nuevo_texto

    # Si encontramos formato original, aplicarlo al nuevo texto
    if formato_original:
        try:
            # Copiar propiedades básicas de formato
            if hasattr(formato_original, 'name'):
                run.font.name = formato_original.name
            if hasattr(formato_original, 'size'):
                run.font.size = formato_original.size
            if hasattr(formato_original, 'bold'):
                run.font.bold = formato_original.bold
            if hasattr(formato_original, 'italic'):
                run.font.italic = formato_original.italic
            if hasattr(formato_original, 'underline'):
                run.font.underline = formato_original.underline
            # Copiar color si existe
            if hasattr(formato_original, 'color') and formato_original.color:
                if hasattr(formato_original.color, 'rgb'):
                    run.font.color.rgb = formato_original.color.rgb
        except Exception as e:
            print(f"Advertencia al copiar formato: {e}")
            # Continuar incluso si hay errores al copiar el formato