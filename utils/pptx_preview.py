import streamlit.components.v1 as components
import streamlit as st
import tempfile
import os
import base64

def mostrar_preview_pptx(file_data):
    """Muestra el PPTX usando Google Docs Viewer"""
    try:
        if isinstance(file_data, memoryview):
            file_data = file_data.tobytes()
            
        # Convertir a base64
        b64 = base64.b64encode(file_data).decode()
        
        # Crear el iframe con Google Docs Viewer
        iframe = f"""
            <iframe
                src="https://view.officeapps.live.com/op/embed.aspx?src=data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{b64}"
                width="100%"
                height="600px"
                frameborder="0">
            </iframe>
        """
        
        st.components.v1.html(iframe, height=600, scrolling=True)
        
    except Exception as e:
        st.error(f"Error al mostrar la presentación: {str(e)}")
        st.download_button(
            "Descargar presentación",
            data=file_data,
            file_name="presentacion.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
