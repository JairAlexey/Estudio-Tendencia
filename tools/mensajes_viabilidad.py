MENSAJES_VIABILIDAD = [
    {
        "Nivel": "Alto",
        "Búsqueda Web": "La búsqueda en los términos asociados al programa es alta, lo que muestra un gran interés en el programa buscado bajo ese nombre.",
        "LinkedIn": "Se identifica alta presencia de profesionales en el área, lo que nos muestra gran interés por parte del mercado laboral en la contratación de estos perfiles tanto a nivel nacional, como a nivel regional.",
        "Competencia Académica": "El porcentaje de competencia es alto ya que existen pocos programas similares, lo que refleja interés no aprovechado en el programa.",
        "Sectores económicos (CIIU)": "El programa se vincula con sectores estratégicos, lo que muestra alta alineación con las demandas del mercado y una inserción laboral especializada."
    },
    {
        "Nivel": "Medio",
        "Búsqueda Web": "La búsqueda en los términos asociados al programa es media, lo que muestra moderado interés en el programa, lo que significa que se debe buscar variables más llamativas para la propuesta.",
        "LinkedIn": "Se identifica presencia moderada de profesionales, muestra un interés medio en la industria lo que representa que se debe potenciar las habilidades y aptitudes de los graduados.",
        "Competencia Académica": "El porcentaje de competencia es medio ya que, a pesar de que tiene alto interés, muestra alta competencia con otras universidades.",
        "Sectores económicos (CIIU)": "-"
    },
    {
        "Nivel": "Bajo",
        "Búsqueda Web": "La búsqueda en los términos asociados a la propuesta es baja, lo que muestra un poco interés en el programa buscado bajo ese nombre.",
        "LinkedIn": "Se identifica baja presencia de profesionales en el área, lo que nos muestra poco interés por parte del mercado laboral en la contratación de estos perfiles tanto a nivel nacional, como a nivel regional.",
        "Competencia Académica": "El porcentaje de competencia es bajo ya que existen muchos programas similares, lo que significa saturación del programa.",
        "Sectores económicos (CIIU)": "El programa no se vincula con sectores estratégicos, lo que muestra baja alineación con las demandas del mercado y una inserción laboral especializada."
    }
]

def get_nivel(porcentaje):
    if porcentaje >= 71:
        return "Alto"
    elif porcentaje >= 61:
        return "Medio"
    else:
        return "Bajo"

def get_mensaje(campo, porcentaje):
    nivel = get_nivel(porcentaje)
    for mensaje in MENSAJES_VIABILIDAD:
        if mensaje["Nivel"] == nivel:
            return mensaje.get(campo, "-")
    return "-"