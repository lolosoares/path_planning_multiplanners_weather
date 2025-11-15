import heapq
import time

class UCS:
    def __init__(self, env):
        self.env = env
        self.agent_dict = env.agent_dict
    
    def search(self, agent_name):
        start_time = time.time()
        
        start = self.agent_dict[agent_name]["start"]
        initial_battery = self.agent_dict[agent_name]["battery"]
        
        print(f"🟦 UCS planejando missão completa...")
        
        # Planejar missão completa
        full_mission_path = self.plan_complete_mission(agent_name, start, initial_battery)
        
        computation_time = time.time() - start_time
        
        if full_mission_path:
            print(f"✅ UCS MISSÃO COMPLETA: {len(full_mission_path)} passos totais")
            return full_mission_path
        else:
            print(f"❌ UCS FALHOU: Missão não planejável")
            return []

    def plan_complete_mission(self, agent_name, start, initial_battery):
        """Planeja missão completa com UCS"""
        mission_path = []
        current_position = start
        current_battery = initial_battery
        
        # FASE 1: Ida para entrega
        print("   FASE 1: Indo para entrega (UCS)...")
        delivery_goal = self.agent_dict[agent_name]["goal"]
        outbound_path = self.find_path_ucs(current_position, delivery_goal, current_battery, agent_name)
        
        if not outbound_path:
            print("   ❌ UCS: Não foi possível planejar ida para entrega")
            return []
        
        mission_path.extend(outbound_path[1:])
        
        # Atualizar bateria após ida
        for i in range(1, len(outbound_path)):
            move_cost = self.env.calculate_move_cost(outbound_path[i-1], outbound_path[i], current_battery)
            current_battery -= move_cost
        current_position = delivery_goal
        
        print(f"   ✅ UCS Chegou na entrega. Bateria: {current_battery:.1f}%")
        
        # FASE 2: Entrega (pausa)
        print("   FASE 2: Realizando entrega...")
        delivery_steps = [current_position] * 3
        mission_path.extend(delivery_steps)
        
        # FASE 3: Volta para base
        print("   FASE 3: Voltando para base (UCS)...")
        home_base = self.agent_dict[agent_name]["home_base"]
        inbound_path = self.find_path_ucs(current_position, home_base, current_battery, agent_name)
        
        if not inbound_path:
            print("   ❌ UCS: Não foi possível planejar volta para base")
            return []
        
        mission_path.extend(inbound_path[1:])
        current_position = home_base
        
        # FASE 4: Repouso (pausa)
        print("   FASE 4: Repousando na base...")
        rest_steps = [current_position] * 5
        mission_path.extend(rest_steps)
        
        return mission_path

    def find_path_ucs(self, start, goal, initial_battery, agent_name):
        """Encontra caminho com UCS (Busca de Custo Uniforme)"""
        frontier = []
        heapq.heappush(frontier, (0, start, initial_battery))
        came_from = {(start, initial_battery): None}
        cost_so_far = {(start, initial_battery): 0}
        
        nodes_explored = 0
        
        while frontier:
            current_cost, current, current_battery = heapq.heappop(frontier)
            nodes_explored += 1
            
            if current == goal:
                # Reconstruir caminho
                path = []
                state = (current, current_battery)
                while state in came_from and came_from[state] is not None:
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
                    new_battery = min(100.0, new_battery + 20)
                
                new_cost = cost_so_far[(current, current_battery)] + move_cost
                new_state = (neighbor, new_battery)
                
                if new_state not in cost_so_far or new_cost < cost_so_far[new_state]:
                    cost_so_far[new_state] = new_cost
                    priority = new_cost
                    heapq.heappush(frontier, (priority, neighbor, new_battery))
                    came_from[new_state] = (current, current_battery)
        
        return []