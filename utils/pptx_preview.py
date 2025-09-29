import streamlit as st

def mostrar_preview_pptx(file_data):
    """Muestra el botón de descarga para la presentación"""
    try:
        if isinstance(file_data, memoryview):
            file_data = file_data.tobytes()
            
        st.info("💡 Para ver la presentación, descargue el archivo y ábralo con Microsoft PowerPoint")
        st.download_button(
            "📥 Descargar presentación",
            data=file_data,
            file_name="presentacion.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            help="Descargar para ver en PowerPoint"
        )
            
    except Exception as e:
        st.error(f"Error al procesar la presentación: {str(e)}")
