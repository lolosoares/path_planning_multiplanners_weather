import time
import sys

class IDS:
    def __init__(self, env):
        self.env = env
        self.agent_dict = env.agent_dict
        self.max_depth_map = {
            (10, 10): 100,
            (20, 20): 50,
            (50, 50): 30,
            (100, 100): 20
        }
    
    def search(self, agent_name):
        print(f"🟩 IDS iniciando busca...")
        start_time = time.time()
        
        start = self.agent_dict[agent_name]["start"]
        goal = self.agent_dict[agent_name]["goal"]
        
        rows, cols = self.env.rows, self.env.cols
        max_depth = 30
        
        for (max_rows, max_cols), depth in self.max_depth_map.items():
            if rows <= max_rows and cols <= max_cols:
                max_depth = depth
                break
        
        print(f"   Mapa: {rows}x{cols}, Limite IDS: {max_depth}")
        
        depth = 0
        nodes_explored = 0
        
        while depth < max_depth:
            # IDS busca SOMENTE ida para entrega (sem bateria/custo)
            result, nodes = self.depth_limited_search(start, goal, depth, agent_name, [], set(), 0)
            nodes_explored += nodes
            
            if result is not None:
                # O IDS retorna apenas o caminho de ida (Path Finding Simples)
                computation_time = time.time() - start_time
                print(f"✅ IDS SUCESSO: Caminho de ida encontrado em {len(result)} passos")
                print(f"   Nós Explorados: {nodes_explored}")
                print(f"   Tempo de Execução (Planejamento): {computation_time:.4f}s")
                
                # Para uma missão COMPLETA, o código externo deve planejar a volta.
                # Retornamos o caminho de ida, que é o máximo que o IDS simples pode fazer.
                return result 
            
            depth += 1
            if depth % 5 == 0:
                print(f"   IDS: Profundidade {depth}, {nodes_explored} nós explorados...")
                
            if time.time() - start_time > 30:
                print(f"❌ IDS: TIMEOUT após 30 segundos")
                return []
        
        computation_time = time.time() - start_time
        print(f"❌ IDS: Limite de profundidade {max_depth} atingido")
        print(f"   Nós Explorados: {nodes_explored}")
        return []
    
    def depth_limited_search(self, current, goal, depth, agent_name, path, visited, nodes_count):
        nodes_count += 1
        
        if nodes_count > 100000:
            return None, nodes_count
            
        if current == goal:
            return path + [current], nodes_count
        
        if depth <= 0:
            return None, nodes_count
        
        visited.add(current)
        
        # O IDS simples ignora a bateria, assume 100%
        neighbors = self.env.get_neighbors(current, 100.0) 
        
        for neighbor in neighbors:
            if neighbor not in visited:
                result, nodes_count = self.depth_limited_search(
                    neighbor, goal, depth-1, agent_name, path + [current], visited.copy(), nodes_count
                )
                if result is not None:
                    return result, nodes_count
        
        return None, nodes_count