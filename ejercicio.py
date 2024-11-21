import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Función para mostrar la información del alumno
def mostrar_informacion_alumno():
    with st.container():
        st.markdown('Legajo: 55.555')
        st.markdown('Nombre: Juan Pérez')
        st.markdown('Comisión: C1')

# Función para procesar datos y generar métricas
def procesar_datos(df, sucursal_seleccionada):
    # Validar la existencia de las columnas necesarias
    columnas_requeridas = ['Sucursal', 'Producto', 'Año', 'Mes', 'Unidades_vendidas', 'Ingreso_total', 'Costo_total']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error(f"El archivo no contiene las columnas requeridas: {', '.join(columnas_requeridas)}")
        return

    # Convertir columnas a numéricas y manejar errores
    df['Año'] = pd.to_numeric(df['Año'], errors='coerce')
    df['Mes'] = pd.to_numeric(df['Mes'], errors='coerce')
    df = df.dropna(subset=['Año', 'Mes'])

    # Filtrar por sucursal seleccionada
    if sucursal_seleccionada != "Todas":
        df = df[df['Sucursal'] == sucursal_seleccionada]

    # Calcular las métricas utilizando la función del código 2
    df = calcular_metricas(df)

    # Calcular promedios globales para referencia
    ingreso_total_global = df['Ingreso_total'].sum()
    unidades_totales_global = df['Unidades_vendidas'].sum()
    costo_total_global = df['Costo_total'].sum()

    precio_promedio_global = ingreso_total_global / unidades_totales_global if unidades_totales_global != 0 else 0
    margen_promedio_global = ((ingreso_total_global - costo_total_global) / ingreso_total_global) * 100 if ingreso_total_global != 0 else 0
    unidades_promedio_global = unidades_totales_global / len(df['Producto'].unique()) if len(df['Producto'].unique()) != 0 else 0

    # Calcular variaciones utilizando la función del código 2
    variaciones = calcular_variaciones(df)

    # Mostrar métricas y gráficos por producto
    for producto in df['Producto'].unique():
        datos_producto = df[df['Producto'] == producto]
        precio_promedio = datos_producto['Ingreso_total'].sum() / datos_producto['Unidades_vendidas'].sum()
        margen_promedio = ((datos_producto['Ingreso_total'].sum() - datos_producto['Costo_total'].sum()) / datos_producto['Ingreso_total'].sum()) * 100
        unidades_vendidas = datos_producto['Unidades_vendidas'].sum()

        # Obtener variaciones calculadas previamente
        variacion_precio = variaciones[producto]["variacion_precio_promedio"]
        variacion_margen = variaciones[producto]["variacion_margen_promedio"]
        variacion_unidades = variaciones[producto]["variacion_unidades_vendidas"]

        # Mostrar métricas y gráfico
        with st.container():
            st.markdown(f"### {producto}")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Precio Promedio", f"${precio_promedio:,.2f}", delta=f"{variacion_precio:+.2f}%")
                st.metric("Margen Promedio", f"{margen_promedio:.2f}%", delta=f"{variacion_margen:+.2f}%")
                st.metric("Unidades Vendidas", f"{int(unidades_vendidas):,}", delta=f"{variacion_unidades:+.2f}%")
            with col2:
                # Crear gráfico de evolución
                datos_producto['Fecha'] = pd.to_datetime({'year': datos_producto['Año'], 'month': datos_producto['Mes'], 'day': 1})
                datos_producto = datos_producto.sort_values('Fecha')
                if not datos_producto.empty:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.plot(datos_producto['Fecha'], datos_producto['Unidades_vendidas'], label="Unidades Vendidas", color="blue")
                    
                    # Línea de tendencia
                    fechas = (datos_producto['Fecha'] - datos_producto['Fecha'].min()).dt.days
                    z = np.polyfit(fechas, datos_producto['Unidades_vendidas'], 1)
                    p = np.poly1d(z)
                    ax.plot(datos_producto['Fecha'], p(fechas), label="Tendencia", color="red", linestyle="--")
                    
                    # Configuración del gráfico
                    ax.set_title(f"Evolución de Ventas - {producto}")
                    ax.set_xlabel("Fecha")
                    ax.set_ylabel("Unidades Vendidas")
                    ax.legend()
                    ax.grid(True)
                    st.pyplot(fig)

# Función para calcular las métricas (tomada del código 2)
def calcular_metricas(df):
    df['Precio Promedio'] = df['Ingreso_total'] / df['Unidades_vendidas']
    df['Margen'] = ((df['Ingreso_total'] - df['Costo_total']) / df['Ingreso_total']) * 100
    return df

# Función para calcular las variaciones (tomada del código 2)
def calcular_variaciones(df):
    variaciones = {}
    for producto in df['Producto'].unique():
        datos_producto = df[df['Producto'] == producto]
        precio_promedio_anual = datos_producto.groupby('Año')['Precio Promedio'].mean()
        margen_promedio_anual = datos_producto.groupby('Año')['Margen'].mean()
        unidades_vendidas_anual = datos_producto.groupby('Año')['Unidades_vendidas'].sum()

        variaciones[producto] = {
            "variacion_precio_promedio": precio_promedio_anual.pct_change().mean() * 100,
            "variacion_margen_promedio": margen_promedio_anual.pct_change().mean() * 100,
            "variacion_unidades_vendidas": unidades_vendidas_anual.pct_change().mean() * 100
        }
    return variaciones

# Configuración inicial de la aplicación
st.set_page_config(layout="wide")
st.title("Datos de Todas las Sucursales")
st.sidebar.title("Cargar archivo de datos")

# Subir archivo CSV
archivo_cargado = st.sidebar.file_uploader("Subir archivo CSV", type=["csv"])
if archivo_cargado:
    datos = pd.read_csv(archivo_cargado)
    sucursales = ["Todas"] + sorted(datos['Sucursal'].unique())
    sucursal_seleccionada = st.sidebar.selectbox("Seleccionar Sucursal", sucursales)
    procesar_datos(datos, sucursal_seleccionada)
else:
    st.sidebar.warning("Sube un archivo CSV para comenzar.")

# Mostrar información del alumno
mostrar_informacion_alumno()












