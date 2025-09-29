import io
import os
import tempfile
from pptx import Presentation
import streamlit as st
import base64

def convert_pptx_to_pdf_bytes(pptx_data):
    """Convierte PPTX a PDF usando unoconv (LibreOffice)"""
    try:
        # Guardar PPTX temporal
        with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as tmp:
            tmp.write(pptx_data)
            pptx_path = tmp.name
        
        # Convertir a PDF usando unoconv
        pdf_path = pptx_path.replace('.pptx', '.pdf')
        os.system(f'unoconv -f pdf "{pptx_path}"')
        
        # Leer el PDF generado
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            
            # Limpiar archivos temporales
            os.unlink(pptx_path)
            os.unlink(pdf_path)
            
            return pdf_data
        else:
            raise Exception("No se pudo generar el PDF")

    except Exception as e:
        st.error(f"Error al convertir PPTX a PDF: {str(e)}")
        return None

def mostrar_preview_pptx(file_data):
    """Muestra el PDF en el navegador usando un iframe"""
    try:
        if isinstance(file_data, memoryview):
            file_data = file_data.tobytes()
            
        # Si estamos en Linux (Streamlit Cloud)
        if os.name != 'nt':
            pdf_data = convert_pptx_to_pdf_bytes(file_data)
            if pdf_data:
                b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                pdf_display = f'''
                    <iframe src="data:application/pdf;base64,{b64_pdf}" 
                            width="100%" 
                            height="800" 
                            style="border: none;">
                    </iframe>
                '''
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.error("No se pudo convertir la presentación")
                st.download_button(
                    "Descargar PPTX",
                    data=file_data,
                    file_name="presentacion.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
        else:
            # En Windows, usar el código original con PowerPoint
            # ...existing code for Windows using pywin32...
            pass
            
    except Exception as e:
        st.error(f"Error al mostrar la presentación: {str(e)}")
        st.download_button(
            "Descargar PPTX",
            data=file_data,
            file_name="presentacion.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
