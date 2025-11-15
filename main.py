import pandas as pd
from ui.drone_ui import DroneControlUI

def main():
    # Carregar mapa
    df = pd.read_excel("./pal/mapa.xlsx", header=None, engine="openpyxl")
    grid = df.astype(str).values.tolist()
    
    # Iniciar interface
    ui = DroneControlUI(grid)
    ui.run()

if __name__ == "__main__":
    main()