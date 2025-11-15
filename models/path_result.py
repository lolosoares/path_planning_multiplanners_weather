from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import time

@dataclass
class PathResult:
    algorithm: str
    path: List[Tuple[int, int]]
    computation_time: float
    nodes_explored: int
    total_cost: float
    battery_usage: float
    estimated_time: float
    
    def __init__(self, algorithm: str, path: List[Tuple[int, int]], 
                 computation_time: float, nodes_explored: int = 0):
        self.algorithm = algorithm
        self.path = path
        self.computation_time = computation_time
        self.nodes_explored = nodes_explored
        self.total_cost = self._calculate_total_cost()
        self.battery_usage = self._estimate_battery_usage()
        self.estimated_time = self._estimate_time()
    
    def _calculate_total_cost(self) -> float:
        """Calcula custo total baseado no comprimento do caminho"""
        if not self.path:
            return float('inf')
        return len(self.path) * 1.0  # Custo simplificado
    
    def _estimate_battery_usage(self) -> float:
        """Estima uso de bateria"""
        if not self.path:
            return float('inf')
        return len(self.path) * 2.0  # Estimativa simplificada
    
    def _estimate_time(self) -> float:
        """Estima tempo de voo"""
        if not self.path:
            return float('inf')
        return len(self.path) * 3.0  # 3 segundos por passo
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'algorithm': self.algorithm,
            'path_length': len(self.path) if self.path else 0,
            'computation_time': self.computation_time,
            'nodes_explored': self.nodes_explored,
            'total_cost': self.total_cost,
            'battery_usage': self.battery_usage,
            'estimated_time': self.estimated_time,
            'efficiency': self.total_cost / len(self.path) if self.path and len(self.path) > 0 else float('inf')
        }
    
    def is_valid(self) -> bool:
        """Verifica se o resultado é válido"""
        return self.path is not None and len(self.path) > 0
    
    def get_summary(self) -> str:
        """Retorna resumo do resultado"""
        if not self.is_valid():
            return f"{self.algorithm}: ❌ Nenhuma rota encontrada"
        
        return (f"{self.algorithm}: ✅ {len(self.path)} passos, "
                f"custo {self.total_cost:.1f}, "
                f"tempo {self.computation_time:.3f}s")