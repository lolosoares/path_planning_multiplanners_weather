from typing import Dict, List

class PathComparator:
    def __init__(self, all_paths: Dict, flight_height: str, power_mode: str):
        self.all_paths = all_paths
        self.flight_height = flight_height
        self.power_mode = power_mode
    
    def compare_mission_results(self):
        """Compara resultados das missões completas"""
        comparison = "🚁 COMPARAÇÃO DE MISSÕES COMPLETAS\n\n"
        comparison += f"Altura: {self.flight_height} | Modo: {self.power_mode}\n\n"
        
        for algo_name, path in self.all_paths.items():
            if path:
                total_steps = len(path)
                
                # Calcular fases aproximadas
                delivery_index = self.find_delivery_start(path)
                return_index = self.find_return_start(path)
                
                if delivery_index and return_index:
                    outbound_steps = delivery_index
                    delivery_steps = 3  # Fixo
                    inbound_steps = return_index - delivery_index - 3
                    rest_steps = total_steps - return_index - 1
                    
                    comparison += f"🔹 {algo_name}:\n"
                    comparison += f"   • Passos totais: {total_steps}\n"
                    comparison += f"   • Ida: {outbound_steps} passos\n"
                    comparison += f"   • Entrega: {delivery_steps} passos\n"
                    comparison += f"   • Volta: {inbound_steps} passos\n"
                    comparison += f"   • Repouso: {rest_steps} passos\n\n"
                else:
                    comparison += f"🔹 {algo_name}: {total_steps} passos (análise incompleta)\n\n"
            else:
                comparison += f"🔹 {algo_name}: ❌ MISSÃO FALHOU\n\n"
        
        return comparison
    
    def find_delivery_start(self, path):
        """Encontra onde começa a entrega"""
        goal = None
        # Encontrar primeiro goal no path
        for i, pos in enumerate(path):
            if goal is None:
                # Primeira ocorrência é o goal de entrega
                goal = pos
            elif pos == goal and i > 10:  # Evitar detecção prematura
                return i
        return None
    
    def find_return_start(self, path):
        """Encontra onde começa o retorno"""
        if len(path) < 10:
            return None
        
        # Procurar por sequência de pausa (mesma posição múltiplas vezes)
        for i in range(len(path) - 5):
            if (path[i] == path[i+1] == path[i+2] and 
                path[i] != path[i-1] and i > 5):
                return i + 3  # Após a entrega
        
        return None