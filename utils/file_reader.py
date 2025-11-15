import pandas as pd
from typing import List, Tuple, Dict, Optional

class MapReader:
    @staticmethod
    def read_excel_map(file_path: str) -> List[List[str]]:
        """
        Lê mapa de arquivo Excel e retorna como matriz
        """
        try:
            df = pd.read_excel(file_path, header=None, engine="openpyxl")
            return df.astype(str).values.tolist()
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo {file_path}: {str(e)}")
    
    @staticmethod
    def find_positions(grid: List[List[str]]) -> Dict[str, Tuple[int, int]]:
        """
        Encontra todas as posições importantes no mapa
        Retorna dicionário com: start, dest_1, dest_2, etc.
        """
        positions = {}
        
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                cell = str(cell).strip()
                
                if cell == "S":
                    positions['start'] = (x, y)
                elif cell in ["1", "2", "3", "4"]:
                    positions[f'dest_{cell}'] = (x, y)
                elif cell == "A":
                    positions.setdefault('areas_a', []).append((x, y))
                elif cell in ["X", "x"]:
                    positions.setdefault('obstacles', []).append((x, y))
        
        return positions
    
    @staticmethod
    def validate_map(grid: List[List[str]]) -> bool:
        """
        Valida se o mapa tem estrutura correta
        """
        if not grid:
            return False
        
        # Verificar se todas as linhas têm o mesmo comprimento
        col_count = len(grid[0])
        for row in grid:
            if len(row) != col_count:
                return False
        
        # Verificar se há pelo menos um start e um destino
        positions = MapReader.find_positions(grid)
        if 'start' not in positions:
            return False
        
        destinations = [k for k in positions.keys() if k.startswith('dest_')]
        if not destinations:
            return False
        
        return True
    
    @staticmethod
    def get_map_dimensions(grid: List[List[str]]) -> Tuple[int, int]:
        """Retorna dimensões do mapa (largura, altura)"""
        if not grid:
            return (0, 0)
        return (len(grid[0]), len(grid))
    
    @staticmethod
    def count_obstacles(grid: List[List[str]]) -> Dict[str, int]:
        """Conta diferentes tipos de obstáculos no mapa"""
        counts = {
            'buildings_X': 0,
            'areas_A': 0,
            'free_cells': 0
        }
        
        for row in grid:
            for cell in row:
                cell = str(cell).strip()
                if cell in ["X", "x"]:
                    counts['buildings_X'] += 1
                elif cell == "A":
                    counts['areas_A'] += 1
                elif cell in ["0", ""]:
                    counts['free_cells'] += 1
        
        return counts