import traceback
import pandas as pd
from ui.drone_ui import DroneControlUI
#import sys

def main():
    try:
        # Força a codificação UTF-8 para a saída do console (Windows) #descomente a linha asseguir no windows
        #sys.stdout.reconfigure(encoding='utf-8')
        
        # Carregar mapa
        df = pd.read_excel("./pal/maputo-map.xlsx", header=None, engine="openpyxl")
        grid = df.astype(str).values.tolist()
        
        # Iniciar interface
        ui = DroneControlUI(grid)
        ui.run()
    except Exception as e:
        print(f"💥 ERRO CRÍTICO: {e}")
        traceback.print_exc()
        input("Pressione Enter para sair...")  # Para não fechar abruptamente

if __name__ == "__main__":
    main()