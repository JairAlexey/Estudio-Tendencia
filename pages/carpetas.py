import streamlit as st
from conexion import get_connection
from scrapers.carpetas_linkedin import scraper_carpetas

def mostrar_pagina_carpetas():
    st.title("Gestión de Carpetas LinkedIn")
    
    # Agregar el mismo estilo de la barra de búsqueda que en index.py
    st.markdown("""
        <style>
        div[data-testid="stTextInputRootElement"] {
            border:2px solid #ff0000 !important;
            border-radius:10px !important;
            padding:0.75rem 1rem !important;
            margin-bottom:1rem !important;
            background:#f8f9fa !important;
            box-shadow:2px 2px 6px rgba(0,0,0,0.08) !important;
            display:flex !important;
            align-items:center !important;
            position:relative !important;
        }
        div[data-testid="stTextInputRootElement"]::before {
            content: '';
            display: block;
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' fill='%23ff0000' class='bi bi-search' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85zm-5.442 1.398a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-size: 20px 20px;
            pointer-events: none;
        }
        div[data-testid="stTextInputRootElement"] input {
            border:none !important;
            background:transparent !important;
            font-size:1rem !important;
            color:#222 !important;
            box-shadow:none !important;
            padding-left:2.2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Botón para actualizar proyectos
    col1, col2 = st.columns([3,1])
    with col2:
        if st.button("Actualizar Proyectos", type="primary"):
            with st.spinner("Actualizando proyectos desde LinkedIn..."):
                if scraper_carpetas():
                    st.success("Proyectos actualizados correctamente")
                else:
                    st.error("Error al actualizar proyectos")
                st.rerun()

    # Select box para elegir el tipo de carpeta
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT tipo_carpeta FROM carpetas ORDER BY tipo_carpeta")
    tipos_carpeta = [row[0] for row in cur.fetchall()]
    
    if not tipos_carpeta:
        st.info("No hay carpetas registradas. Haz clic en 'Actualizar Proyectos' para cargar los datos desde LinkedIn.")
        return

    tipo_seleccionado = st.selectbox(
        "Selecciona el tipo de carpeta:",
        tipos_carpeta
    )

    # Barra de búsqueda
    search_query = st.text_input(
        "Buscar proyecto",
        key="search_carpetas",
        label_visibility="collapsed"
    )

    # Consulta SQL base
    query = """
        SELECT id, nombre_proyecto, created_at
        FROM carpetas
        WHERE tipo_carpeta = %s
    """
    params = [tipo_seleccionado]

    # Agregar filtro de búsqueda si existe
    if search_query:
        query += " AND nombre_proyecto ILIKE %s"
        params.append(f"%{search_query}%")

    query += " ORDER BY created_at DESC"

    # Ejecutar consulta
    cur.execute(query, params)
    proyectos = cur.fetchall()
    
    if not proyectos:
        if search_query:
            st.info(f"No se encontraron proyectos que coincidan con '{search_query}'")
        else:
            st.info(f"No hay proyectos en la carpeta {tipo_seleccionado}")
        return

    # Mostrar proyectos
    st.subheader(f"Proyectos en {tipo_seleccionado}")
    for proyecto in proyectos:
        st.markdown(f"""
            <div style='
                border:1px solid #ddd;
                border-radius:10px;
                padding:1rem;
                margin-bottom:0.5rem;
                background:#f8f9fa;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
            '>
                <h4 style='margin:0'>{proyecto[1]}</h4>
                <p style='margin:0; color:#666; font-size:0.8em'>
                    Agregado: {proyecto[2].strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        """, unsafe_allow_html=True)
