import time

class IDS:
    def __init__(self, env):
        self.env = env
        self.agent_dict = env.agent_dict
    
    def search(self, agent_name):
        start_time = time.time()
        
        start = self.agent_dict[agent_name]["start"]
        initial_battery = self.agent_dict[agent_name]["battery"]
        
        print(f"🟩 IDS planejando missão completa...")
        
        # Planejar missão completa
        full_mission_path = self.plan_complete_mission(agent_name, start, initial_battery)
        
        computation_time = time.time() - start_time
        
        if full_mission_path:
            print(f"✅ IDS MISSÃO COMPLETA: {len(full_mission_path)} passos totais")
            return full_mission_path
        else:
            print(f"❌ IDS FALHOU: Missão não planejável")
            return []

    def plan_complete_mission(self, agent_name, start, initial_battery):
        """Planeja missão completa com IDS"""
        mission_path = []
        current_position = start
        current_battery = initial_battery
        
        # FASE 1: Ida para entrega
        print("   FASE 1: Indo para entrega (IDS)...")
        delivery_goal = self.agent_dict[agent_name]["goal"]
        outbound_path = self.find_path_ids(current_position, delivery_goal, agent_name)
        
        if not outbound_path:
            print("   ❌ IDS: Não foi possível planejar ida para entrega")
            return []
        
        mission_path.extend(outbound_path[1:])
        
        # Atualizar bateria estimada após ida
        current_battery -= len(outbound_path) * 0.8  # Estimativa simplificada
        current_position = delivery_goal
        
        print(f"   ✅ IDS Chegou na entrega. Bateria estimada: {current_battery:.1f}%")
        
        # FASE 2: Entrega (pausa)
        print("   FASE 2: Realizando entrega...")
        delivery_steps = [current_position] * 3
        mission_path.extend(delivery_steps)
        
        # FASE 3: Volta para base
        print("   FASE 3: Voltando para base (IDS)...")
        home_base = self.agent_dict[agent_name]["home_base"]
        inbound_path = self.find_path_ids(current_position, home_base, agent_name)
        
        if not inbound_path:
            print("   ❌ IDS: Não foi possível planejar volta para base")
            return []
        
        mission_path.extend(inbound_path[1:])
        current_position = home_base
        
        # FASE 4: Repouso (pausa)
        print("   FASE 4: Repousando na base...")
        rest_steps = [current_position] * 5
        mission_path.extend(rest_steps)
        
        return mission_path

    def find_path_ids(self, start, goal, agent_name):
        """Encontra caminho com IDS (Profundidade Iterativa)"""
        depth = 0
        max_depth = 200  # Aumentado para missões mais longas
        
        while depth < max_depth:
            result = self.depth_limited_search(start, goal, depth, agent_name, [], set())
            if result is not None:
                return result
            depth += 1
        
        return []

    def depth_limited_search(self, current, goal, depth, agent_name, path, visited):
        if current == goal:
            return path + [current]
        
        if depth <= 0:
            return None
        
        visited.add(current)
        
        # IDS usa bateria máxima para simplificar
        neighbors = self.env.get_neighbors(current, 100.0)
        
        for neighbor in neighbors:
            if neighbor not in visited:
                result = self.depth_limited_search(neighbor, goal, depth-1, agent_name, path + [current], visited.copy())
                if result is not None:
                    return result
        
        return None