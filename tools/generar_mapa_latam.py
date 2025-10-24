import os
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shapereader

# Agregar el path raíz del proyecto para importar conexion correctamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conexion import conn, cursor

# Mapeo de ubicaciones a países
def mapear_a_pais(ubicacion):
    ubicacion = ubicacion.lower()
    if "brasil" in ubicacion or "são paulo" in ubicacion:
        return "Brazil"
    if "argentina" in ubicacion or "buenos aires" in ubicacion:
        return "Argentina"
    if "méxico" in ubicacion or "ciudad de méxico" in ubicacion:
        return "Mexico"
    if "chile" in ubicacion or "santiago" in ubicacion:
        return "Chile"
    if "colombia" in ubicacion or "bogotá" in ubicacion:
        return "Colombia"
    if "ecuador" in ubicacion or "quito" in ubicacion or "guayaquil" in ubicacion:
        return "Ecuador"
    if "perú" in ubicacion or "lima" in ubicacion:
        return "Peru"
    if "uruguay" in ubicacion or "montevideo" in ubicacion:
        return "Uruguay"
    if "venezuela" in ubicacion or "caracas" in ubicacion:
        return "Venezuela"
    if "paraguay" in ubicacion or "asunción" in ubicacion:
        return "Paraguay"
    if "bolivia" in ubicacion or "la paz" in ubicacion:
        return "Bolivia"
    # Otros países de Latam pueden agregarse aquí
    return None

def generar_mapa_latam(proyecto_id=3, ruta_salida="mapa_latam.png"):
    # Leer ubicaciones desde la base de datos
    cursor.execute("""
        SELECT nombre, cantidad
        FROM linkedin_ubicaciones
        WHERE proyecto_id = %s
    """, (proyecto_id,))
    rows = cursor.fetchall()
    print("=== Datos originales de linkedin_ubicaciones ===")
    for ubicacion, cantidad in rows:
        print(f"Ubicacion: {ubicacion} | Cantidad: {cantidad}")
    # Agrupar por país
    paises = {}
    for ubicacion, cantidad in rows:
        pais = mapear_a_pais(str(ubicacion))
        if pais:
            paises[pais] = paises.get(pais, 0) + (cantidad or 0)
    print("\n=== Agrupación por país ===")
    for pais, total in paises.items():
        print(f"{pais}: {total}")
    # Top 5 países
    top_paises = sorted(paises.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\n=== Top 5 países ===")
    for i, (pais, total) in enumerate(top_paises, 1):
        print(f"{i}. {pais}: {total}")
    top_pais_nombres = [p[0] for p in top_paises]
    # Colores escala de grises + vino
    color_vino = "#800020"
    escala_grises = ["#888888", "#aaaaaa", "#cccccc", "#dddddd"]  # de más fuerte a más suave
    color_gris_claro = "#eeeeee"
    # Mapeo de colores por país
    pais_color = {}
    if top_pais_nombres:
        pais_color[top_pais_nombres[0]] = color_vino
        for idx, p in enumerate(top_pais_nombres[1:]):
            pais_color[p] = escala_grises[idx] if idx < len(escala_grises) else color_gris_claro
    # El resto en gris claro
    # Lista de países de Latam
    latam_countries = [
        "Brazil", "Argentina", "Mexico", "Chile", "Colombia", "Ecuador", "Peru",
        "Uruguay", "Venezuela", "Paraguay", "Bolivia", "Guyana", "Suriname", "French Guiana"
    ]
    fig = plt.figure(figsize=(7, 9))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-120, -30, -60, 35], crs=ccrs.PlateCarree())
    # No agregar LAND ni OCEAN para fondo transparente
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='white')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='white')
    # Quitar el marco (spines) del gráfico
    for spine in ax.spines.values():
        spine.set_visible(False)
    # Dibujar países de Latam usando shapereader
    shpfilename = shapereader.natural_earth(resolution='110m', category='cultural', name='admin_0_countries')
    reader = shapereader.Reader(shpfilename)
    for record in reader.records():
        name = record.attributes.get('NAME_LONG') or record.attributes.get('NAME')
        if name in latam_countries:
            color = pais_color.get(name, color_gris_claro)
            ax.add_geometries([record.geometry], ccrs.PlateCarree(),
                              facecolor=color, edgecolor='white', linewidth=0.8)
    plt.tight_layout()
    plt.savefig(ruta_salida, bbox_inches='tight', dpi=300, transparent=True)
    plt.close(fig)
    print(f"Mapa generado y guardado en {ruta_salida}")

if __name__ == "__main__":
    generar_mapa_latam()