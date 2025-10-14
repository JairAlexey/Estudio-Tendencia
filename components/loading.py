import streamlit as st
import time

def show_loading_spinner(message="Cargando...", success_message=None, delay=0.1):
    """
    Show a loading spinner with customizable message
    
    Parameters:
    - message: The message to show during loading
    - success_message: Optional message to show upon completion
    - delay: Delay in seconds to keep the success message visible
    
    Returns:
    - spinner: The spinner placeholder
    """
    spinner = st.empty()
    
    with spinner.container():
        st.markdown("""
            <div style="
                background-color: #f0f2f6;
                border-radius: 0.5rem;
                padding: 1rem;
                margin: 1rem 0;
                display: flex;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="
                    border: 4px solid #e6e6e6;
                    border-top: 4px solid #FF0000;
                    border-radius: 50%;
                    width: 1.5rem;
                    height: 1.5rem;
                    margin-right: 1rem;
                    animation: spin 1s linear infinite;
                "></div>
                <div style="font-size: 1rem;">""" + message + """</div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        """, unsafe_allow_html=True)
    
    return spinner

def loading_complete(spinner, success_message="¡Operación completada!", delay=1.5):
    """
    Show a success message after loading is complete
    
    Parameters:
    - spinner: The spinner placeholder returned by show_loading_spinner
    - success_message: Message to show upon completion
    - delay: Delay in seconds to keep the success message visible
    """
    with spinner.container():
        st.markdown("""
            <div style="
                background-color: #d4edda;
                border-radius: 0.5rem;
                padding: 1rem;
                margin: 1rem 0;
                display: flex;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 4px solid #28a745;
            ">
                <div style="
                    color: #28a745;
                    font-size: 1.5rem;
                    margin-right: 1rem;
                ">✓</div>
                <div style="font-size: 1rem; color: #155724;">""" + success_message + """</div>
            </div>
        """, unsafe_allow_html=True)
    
    time.sleep(delay)
    spinner.empty()
