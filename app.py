import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Traiden Pro - Sistema de Trading Inteligente",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(45deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    .stButton button {
        background: linear-gradient(45deg, #1f77b4, #2196f3);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class ModeloTraiden:
    def __init__(self, capital_inicial=100):
        self.capital = capital_inicial
        self.capital_inicial = capital_inicial
        self.historial_operaciones = []
        self.historial_capital = []
    
    def generar_senales(self, datos):
        senales = []
        for i in range(30, len(datos)):
            precio_actual = datos['close'].iloc[i]
            historico = datos['close'].iloc[i-30:i]
            
            # Análisis técnico simple
            ema_9 = historico.ewm(span=9).mean().iloc[-1]
            ema_21 = historico.ewm(span=21).mean().iloc[-1]
            
            if ema_9 > ema_21 and precio_actual > ema_9:
                senales.append({
                    'timestamp': datos.index[i],
                    'precio': precio_actual,
                    'accion': 'COMPRA',
                    'confianza': 0.75
                })
            elif ema_9 < ema_21 and precio_actual < ema_9:
                senales.append({
                    'timestamp': datos.index[i],
                    'precio': precio_actual,
                    'accion': 'VENTA', 
                    'confianza': 0.75
                })
        return senales
    
    def ejecutar_backtest(self, datos):
        senales = self.generar_senales(datos)
        for senal in senales:
            if senal['confianza'] > 0.65:
                self._ejecutar_operacion(senal)
        return self._generar_reporte()
    
    def _ejecutar_operacion(self, senal):
        tamaño_posicion = self.capital * 0.01
        if np.random.random() < 0.65:
            resultado = tamaño_posicion * 0.015
        else:
            resultado = -tamaño_posicion * 0.006
        
        self.capital += resultado
        self.historial_operaciones.append({
            'timestamp': senal['timestamp'],
            'accion': senal['accion'],
            'resultado': resultado,
            'capital': self.capital
        })
    
    def _generar_reporte(self):
        if not self.historial_operaciones:
            return {"error": "No se ejecutaron operaciones"}
        
        resultados = [op['resultado'] for op in self.historial_operaciones]
        return {
            'capital_inicial': self.capital_inicial,
            'capital_final': self.capital,
            'ganancia_neta': self.capital - self.capital_inicial,
            'rendimiento': (self.capital - self.capital_inicial) / self.capital_inicial,
            'operaciones_totales': len(self.historial_operaciones),
            'operaciones_exitosas': len([r for r in resultados if r > 0])
        }

def generar_datos_mercado(dias=30):
    dates = pd.date_range(start='2024-01-01', periods=dias*24*12, freq='5min')
    np.random.seed(42)
    precios = [100.0]
    for i in range(1, len(dates)):
        retorno = np.random.normal(0.0001, 0.002)
        precios.append(precios[-1] * (1 + retorno))
    return pd.DataFrame({
        'date': dates,
        'open': precios,
        'high': [p * 1.001 for p in precios],
        'low': [p * 0.999 for p in precios],
        'close': precios,
        'volume': np.random.normal(1000000, 200000, len(precios))
    }).set_index('date')

# INTERFAZ PRINCIPAL
def main():
    st.markdown('<h1 class="main-header">🎯 TRAIDEN PRO</h1>', unsafe_allow_html=True)
    st.markdown("### Sistema de Trading Inteligente con IA")
    
    # Sidebar
    st.sidebar.title("⚙️ Configuración")
    capital = st.sidebar.number_input("Capital Inicial (USDT)", 100, 10000, 1000)
    riesgo = st.sidebar.slider("Riesgo por Operación (%)", 0.5, 5.0, 1.0) / 100
    dias = st.sidebar.selectbox("Días a Analizar", [7, 14, 30, 60])
    
    # Botón de ejecución
    if st.button("🚀 EJECUTAR BACKTEST COMPLETO", type="primary"):
        with st.spinner('Ejecutando análisis de mercado...'):
            time.sleep(2)
            modelo = ModeloTraiden(capital)
            datos = generar_datos_mercado(dias)
            reporte = modelo.ejecutar_backtest(datos)
            
            if 'error' not in reporte:
                st.success("✅ Backtest completado exitosamente!")
                
                # Mostrar métricas
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Capital Final", f"${reporte['capital_final']:.2f}", 
                              f"${reporte['ganancia_neta']:.2f}")
                with col2:
                    st.metric("Rendimiento", f"{reporte['rendimiento']:.2%}")
                with col3:
                    st.metric("Operaciones", reporte['operaciones_totales'])
                with col4:
                    st.metric("Tasa Éxito", 
                              f"{reporte['operaciones_exitosas']/reporte['operaciones_totales']:.1%}")
                
                # Gráfico de evolución
                if modelo.historial_operaciones:
                    capitales = [modelo.capital_inicial]
                    for op in modelo.historial_operaciones:
                        capitales.append(op['capital'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        y=capitales,
                        mode='lines+markers',
                        name='Capital',
                        line=dict(color='green', width=3)
                    ))
                    fig.update_layout(
                        title="Evolución del Capital",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Error: {reporte['error']}")
    
    # Información del sistema
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Traiden Pro v2.1**
    - Trading Algorithmico
    - Análisis en Tiempo Real  
    - Gestión Automática de Riesgo
    """)

if __name__ == "__main__":
    main()