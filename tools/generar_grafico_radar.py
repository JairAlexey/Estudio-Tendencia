import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conexion import conn, cursor


def generar_grafico_radar_desde_bd(proyecto_id, ruta_salida):
    cursor.execute('''
        SELECT valor_busqueda, valor_competencia, valor_linkedin, valor_mercado
        FROM grafico_radar_datos
        WHERE proyecto_id = ?
    ''', (proyecto_id,))
    row = cursor.fetchone()
    print(f"[DEBUG] Datos obtenidos de grafico_radar_datos para proyecto_id={proyecto_id}: {row}")
    if not row:
        print(f"No hay datos de gráfico radar para proyecto_id={proyecto_id}")
        return
    # Reemplazar None por 0 para evitar errores
    valores = [v if v is not None else 0 for v in row]
    # Normalizar valores al rango [0, 1] usando máximo fijo (100)
    maximos = [100, 100, 100, 100]  # Puedes ajustar estos valores según tus necesidades
    valores_normalizados = [min(v / m, 1.0) for v, m in zip(valores, maximos)]
    print(f"[DEBUG] Valores normalizados para gráfico radar: {valores_normalizados}")
    labels = ["Busqueda", "Competencia", "LinkedIn", "Mercado"]
    m = len(labels)
    r = np.array(valores_normalizados, dtype=float)
    theta = np.linspace(0, 2*np.pi, m, endpoint=False)
    delta = 2*np.pi/m
    slopes = np.array([(r[(k+1)%m] - r[(k-1)%m]) / (2*delta) for k in range(m)])
    theta_dense = []
    r_dense = []
    for k in range(m):
        th0 = theta[k]
        th1 = (theta[(k+1)%m] if k < m-1 else 2*np.pi)
        r0, r1 = r[k], r[(k+1)%m]
        s0, s1 = slopes[k], slopes[(k+1)%m]
        dth = (th1 - th0) if k < m-1 else (2*np.pi - th0)
        t = np.linspace(0, 1, 80, endpoint=False)
        h00 = 2*t**3 - 3*t**2 + 1
        h10 = t**3 - 2*t**2 + t
        h01 = -2*t**3 + 3*t**2
        h11 = t**3 - t**2
        theta_dense.append(th0 + t*dth)
        r_dense.append(h00*r0 + h10*dth*s0 + h01*r1 + h11*dth*s1)
    theta_dense = np.concatenate(theta_dense + [np.array([2*np.pi])])
    r_dense = np.concatenate(r_dense + [np.array([r[0]])])

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi/4)
    ax.set_theta_direction(-1)
    color_vino = "#800020"
    ax.plot(theta_dense, r_dense, linewidth=2, color=color_vino)
    ax.fill(theta_dense, r_dense, color=color_vino, alpha=0.10)
    ax.plot(theta, r, 'o', color=color_vino)
    ax.set_xticks(theta)
    ax.set_xticklabels(['']*len(labels))
    # Líneas radiales internas como puntitos
    for angle in theta:
        ax.plot([angle, angle], [0, 1.0], linestyle=':', color='gray', linewidth=1)
    for angle, label in zip(theta, labels):
        if label in ["Busqueda", "LinkedIn"]:
            rot = 315
        elif label in ["Mercado", "Competencia"]:
            rot = 405
        else:
            rot = 0
        ax.text(angle, 1.08, label, rotation=rot, ha='center', va='center', fontsize=12, rotation_mode='anchor')
    ax.set_ylim(0, 1.0)
    yticks = [0.0, 0.20, 0.40, 0.60, 0.80, 1.0]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{int(y*100)}%" for y in yticks])
    plt.savefig(ruta_salida.replace('.jpg', '.png'), format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)

# Ejemplo de uso:
if __name__ == "__main__":
    proyecto_id = 1  # Cambia por el id de tu proyecto
    ruta_salida = "../db/imagenes/grafico_radar.jpg"
    generar_grafico_radar_desde_bd(proyecto_id, ruta_salida)