import heapq
import time

class AStar:
    def __init__(self, env):
        self.env = env
        self.agent_dict = env.agent_dict
        self.total_cost = 0.0
        self.total_nodes_explored = 0

    def search(self, agent_name):
        start_time = time.time()
        
        start = self.agent_dict[agent_name]["start"]
        initial_battery = self.agent_dict[agent_name]["battery"]
        
        print(f"🟥 A* planejando missão completa...")
        
        full_mission_path = self.plan_complete_mission(agent_name, start, initial_battery)
        
        computation_time = time.time() - start_time
        
        if full_mission_path:
            print(f"✅ A* MISSÃO CONCLUÍDA: {len(full_mission_path)} passos totais")
            print(f"   Custo Total da Missão (g(n)): {self.total_cost:.2f}")
            print(f"   Nós Explorados: {self.total_nodes_explored}")
            print(f"   Tempo de Execução (Planejamento): {computation_time:.4f}s")
            return full_mission_path
        else:
            print(f"❌ A* FALHOU: Missão não planejável")
            return []

    def plan_complete_mission(self, agent_name, start, initial_battery):
        mission_path = []
        current_position = start
        current_battery = initial_battery
        self.total_cost = 0.0
        self.total_nodes_explored = 0
        
        # FASE 1: Ida para entrega
        print("   FASE 1: Indo para entrega...")
        delivery_goal = self.agent_dict[agent_name]["goal"]
        
        # O find_path retorna (path, final_cost, nodes_explored)
        result = self.find_path(current_position, delivery_goal, current_battery, agent_name)
        
        if not result:
            # 2. A busca falhou. Tenta novamente com Bateria Infinita (ignore_battery=True)
            print("   ❌ Busca falhou com restrição de bateria. Re-testando viabilidade de caminho...")
            
            viability_result = self.find_path(current_position, delivery_goal, current_battery, agent_name, ignore_battery=True)
            
            if viability_result:
                # 3. Sucesso no modo Bateria Infinita
                print("   ⚠️ DIAGNÓSTICO: Caminho existe, mas é inviável por falta de bateria (Outbound).")
            else:
                # 4. Falha no modo Bateria Infinita
                print("   💀 DIAGNÓSTICO: Caminho está BLOQUEADO (Obstáculos ou Mapa Desconectado).")
                
            print("   ❌ Não foi possível planejar ida para entrega")
            return []
        
        outbound_path, outbound_cost, nodes_exp_out = result
        self.total_cost += outbound_cost
        self.total_nodes_explored += nodes_exp_out
        
        mission_path.extend(outbound_path[1:])
        
        # Atualizar bateria após ida
        # O último estado do caminho encontrado define a bateria e a posição
        current_position = delivery_goal
        # A bateria exata deve ser lida do estado final (último elemento do path),
        # mas como find_path retorna apenas a coordenada, mantemos o loop de recálculo (simplificado)
        current_battery -= outbound_cost # Simplificado: o custo é igual à bateria consumida
        
        delivery_time_steps = len(outbound_path) - 1 # Passos de movimento
        
        print(f"   ✅ Chegou na entrega. Bateria: {current_battery:.1f}%")
        
        # FASE 2: Entrega (pausa)
        print("   FASE 2: Realizando entrega...")
        delivery_steps = [current_position] * 3  # 3 frames de entrega
        mission_path.extend(delivery_steps)
        self.total_cost += 0.0
        delivery_time_steps += 3 # Adiciona os frames de pausa
        print(f"   Tempo de Entrega (Endereço + Pausa): {delivery_time_steps} passos")
        
        # FASE 3: Volta para base
        print("   FASE 3: Voltando para base...")
        # ⚡️ NOVO BLOCO DE CARREGAMENTO EXPLÍCITO APÓS A ENTREGA
        if current_position in self.env.charging_stations:
            # Assumimos que a taxa de carregamento é de +20 (conforme o seu código anterior),
            # mas o drone carrega durante a pausa da entrega.
            charge_amount = 100.0 
            current_battery = min(self.env.agent_dict[agent_name]["max_battery"], current_battery + charge_amount)
            
            # Atualiza o estado da bateria no dicionário do agente (importante para logs futuros)
            self.env.agent_dict[agent_name]["battery"] = current_battery 
            
            print(f"   ⚡ CARREGAMENTO NO DESTINO CONCLUÍDO. Bateria atualizada: {current_battery:.1f}%")
        # ⚡️ FIM DO NOVO BLOCO
        home_base = self.agent_dict[agent_name]["home_base"]
        result = self.find_path(current_position, home_base, current_battery, agent_name)
        
        if not result:
            print("   ❌ Não foi possível planejar volta para base")
            return []
            
        inbound_path, inbound_cost, nodes_exp_in = result
        self.total_cost += inbound_cost
        self.total_nodes_explored += nodes_exp_in
        
        mission_path.extend(inbound_path[1:])
        current_position = home_base
        
        # FASE 4: Repouso (pausa)
        print("   FASE 4: Repousando na base...")
        rest_steps = [current_position] * 5  # 5 frames de repouso
        mission_path.extend(rest_steps)
        self.total_cost += 0.0
        
        return mission_path

    def find_path(self, start, goal, initial_battery, agent_name, ignore_battery=False):
        open_set = []
        # Item: (custo_f, posição, bateria)
        heapq.heappush(open_set, (0, start, initial_battery))
        came_from = {}
        
        # Chave: (posição, bateria)
        g_score = {(start, initial_battery): 0}
        f_score = {(start, initial_battery): self.env.admissible_heuristic(start, agent_name)}
        nodes_explored = 0

        while open_set:
            current_f, current, current_battery = heapq.heappop(open_set)
            nodes_explored += 1 # Contagem de nós expandidos

            if current == goal:
                # Reconstruir caminho
                path = []
                state = (current, current_battery)
                
                # Obtém o custo real (g(n)) ao chegar ao objetivo
                final_cost = g_score.get(state, float('inf')) 
                
                while state in came_from:
                    pos, bat = state
                    path.append(pos)
                    state = came_from[state]
                path.append(start)
                path.reverse()
                
                return path, final_cost, nodes_explored # Retorna o caminho, custo final e nós explorados
            
            neighbors = self.env.get_neighbors(current, current_battery, ignore_battery)
            
            for neighbor in neighbors:
                move_cost = self.env.calculate_move_cost(current, neighbor, current_battery)
                new_battery = current_battery - move_cost
                #new_battery = 100.0
                                
                if neighbor in self.env.charging_stations:
                    #new_battery = min(100.0, new_battery + 20)
                    new_battery = 100.0 # Carrega completamente
                
                state = (neighbor, new_battery)
                
                # Tentative g_score: Custo para chegar no estado anterior + custo da transição
                tentative_g = g_score.get((current, current_battery), float('inf')) + move_cost
                
                if state not in g_score or tentative_g < g_score[state]:
                    came_from[state] = (current, current_battery)
                    g_score[state] = tentative_g
                    f_score[state] = tentative_g + self.env.admissible_heuristic(neighbor, agent_name)
                    heapq.heappush(open_set, (f_score[state], neighbor, new_battery))
        
        return None # Retorna None em caso de falha