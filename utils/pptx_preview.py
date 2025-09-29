import io
import os
import tempfile
import pythoncom
import win32com.client
import streamlit as st
import base64

def convert_pptx_to_pdf(pptx_data):
    """Convierte un archivo PPTX a PDF y retorna los bytes del PDF"""
    try:
        # Inicializar COM
        pythoncom.CoInitialize()
        
        # Crear archivos temporales
        temp_dir = tempfile.mkdtemp()
        pptx_path = os.path.join(temp_dir, "temp.pptx")
        pdf_path = os.path.join(temp_dir, "temp.pdf")
        
        # Guardar PPTX temporal
        with open(pptx_path, 'wb') as f:
            f.write(pptx_data)

        # Convertir a PDF usando PowerPoint
        powerpoint = win32com.client.Dispatch("Powerpoint.Application")
        presentation = powerpoint.Presentations.Open(pptx_path)
        presentation.SaveAs(pdf_path, 32)  # 32 = formato PDF
        presentation.Close()
        powerpoint.Quit()

        # Leer el PDF generado
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()

        # Limpiar archivos temporales
        os.unlink(pptx_path)
        os.unlink(pdf_path)
        os.rmdir(temp_dir)
        
        return pdf_data

    except Exception as e:
        st.error(f"Error al convertir PPTX a PDF: {str(e)}")
        return None
    finally:
        pythoncom.CoUninitialize()

def mostrar_preview_pptx(file_data):
    """Muestra el PDF en el navegador usando un iframe"""
    try:
        if isinstance(file_data, memoryview):
            file_data = file_data.tobytes()
            
        pdf_data = convert_pptx_to_pdf(file_data)
        if pdf_data:
            # Convertir PDF a base64
            b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
            
            # Crear iframe con el PDF
            pdf_display = f'''
                <iframe src="data:application/pdf;base64,{b64_pdf}" 
                        width="100%" 
                        height="800" 
                        style="border: none;">
                </iframe>
            '''
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("No se pudo convertir la presentación a PDF")
            st.info("Asegúrese de tener Microsoft PowerPoint instalado")
            
    except Exception as e:
        st.error(f"Error al mostrar la presentación: {str(e)}")
