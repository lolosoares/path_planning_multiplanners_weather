import heapq
import time

class AStar:
    def __init__(self, env):
        self.env = env
        self.agent_dict = env.agent_dict

    def search(self, agent_name):
        start_time = time.time()
        
        start = self.agent_dict[agent_name]["start"]
        initial_battery = self.agent_dict[agent_name]["battery"]
        
        print(f"🟥 A* planejando missão completa...")
        
        # Planejar missão completa: ida → entrega → volta
        full_mission_path = self.plan_complete_mission(agent_name, start, initial_battery)
        
        computation_time = time.time() - start_time
        
        if full_mission_path:
            print(f"✅ A* MISSÃO COMPLETA: {len(full_mission_path)} passos totais")
            return full_mission_path
        else:
            print(f"❌ A* FALHOU: Missão não planejável")
            return []

    def plan_complete_mission(self, agent_name, start, initial_battery):
        """Planeja missão completa: ida → entrega → volta"""
        mission_path = []
        current_position = start
        current_battery = initial_battery
        
        # FASE 1: Ida para entrega
        print("   FASE 1: Indo para entrega...")
        delivery_goal = self.agent_dict[agent_name]["goal"]
        outbound_path = self.find_path(current_position, delivery_goal, current_battery, agent_name)
        
        if not outbound_path:
            print("   ❌ Não foi possível planejar ida para entrega")
            return []
        
        # Adicionar caminho de ida (excluindo start que já está em current_position)
        mission_path.extend(outbound_path[1:])
        
        # Atualizar bateria após ida
        for i in range(1, len(outbound_path)):
            move_cost = self.env.calculate_move_cost(outbound_path[i-1], outbound_path[i], current_battery)
            current_battery -= move_cost
        current_position = delivery_goal
        
        print(f"   ✅ Chegou na entrega. Bateria: {current_battery:.1f}%")
        
        # FASE 2: Entrega (pausa)
        print("   FASE 2: Realizando entrega...")
        delivery_steps = [current_position] * 3  # 3 frames de entrega
        mission_path.extend(delivery_steps)
        
        # FASE 3: Volta para base
        print("   FASE 3: Voltando para base...")
        home_base = self.agent_dict[agent_name]["home_base"]
        inbound_path = self.find_path(current_position, home_base, current_battery, agent_name)
        
        if not inbound_path:
            print("   ❌ Não foi possível planejar volta para base")
            return []
        
        # Adicionar caminho de volta (excluindo posição atual)
        mission_path.extend(inbound_path[1:])
        current_position = home_base
        
        # FASE 4: Repouso (pausa)
        print("   FASE 4: Repousando na base...")
        rest_steps = [current_position] * 5  # 5 frames de repouso
        mission_path.extend(rest_steps)
        
        return mission_path

    def find_path(self, start, goal, initial_battery, agent_name):
        """Encontra caminho entre dois pontos"""
        open_set = []
        heapq.heappush(open_set, (0, start, initial_battery))
        came_from = {}
        
        g_score = {(start, initial_battery): 0}
        f_score = {(start, initial_battery): self.env.admissible_heuristic(start, agent_name)}
        
        while open_set:
            current_f, current, current_battery = heapq.heappop(open_set)
            
            if current == goal:
                # Reconstruir caminho
                path = []
                state = (current, current_battery)
                while state in came_from:
                    pos, bat = state
                    path.append(pos)
                    state = came_from[state]
                path.append(start)
                path.reverse()
                return path
            
            neighbors = self.env.get_neighbors(current, current_battery)
            
            for neighbor in neighbors:
                move_cost = self.env.calculate_move_cost(current, neighbor, current_battery)
                new_battery = current_battery - move_cost
                
                # Recarregar se passar por base
                if neighbor in self.env.charging_stations:
                    new_battery = min(100.0, new_battery + 20)  # Carregamento rápido
                
                state = (neighbor, new_battery)
                tentative_g = g_score.get((current, current_battery), float('inf')) + move_cost
                
                if state not in g_score or tentative_g < g_score[state]:
                    came_from[state] = (current, current_battery)
                    g_score[state] = tentative_g
                    f_score[state] = tentative_g + self.env.admissible_heuristic(neighbor, agent_name)
                    heapq.heappush(open_set, (f_score[state], neighbor, new_battery))
        
        return []