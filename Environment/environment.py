import random
from typing import List, Tuple, Dict

class Environment:
    def __init__(self, grid, start, goal, flight_height="low", power_mode="normal", weather_conditions=None):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.flight_height = flight_height
        self.power_mode = power_mode
        self.original_grid = [row.copy() for row in grid]
        
        # Condições climáticas
        self.weather_conditions = weather_conditions or {}
        self.grid_with_weather = self.apply_weather_conditions()
        
        # Pontos importantes
        self.charging_stations = self.find_charging_stations()
        self.delivery_points = self.find_delivery_points()
        self.charging_stations.update({
            pos:{"type":"delivery_and_charge", "charge_rate":100.0}
            for pos in self.delivery_points.keys()
        })
        print(f"🔋 Bases de carregamento (Incluindo Entregas): {list(self.charging_stations.keys())}")
        
        self.home_base = tuple(start)  # Base inicial
        
        self.agent_dict = {
            "agent0": {
                "start": tuple(start),
                "goal": tuple(goal),
                "home_base": tuple(start),
                "battery": 100.0,
                "max_battery": 100.0,
                "mission": "outbound",  # outbound, delivering, inbound, resting
                "delivery_time": 0,
                "resting_time": 0,
                "mission_complete": False
            }
        }

    def apply_weather_conditions(self):
        """Aplica condições climáticas dinâmicas"""
        grid_copy = [row.copy() for row in self.original_grid]
        
        print("🌤️  Aplicando condições climáticas...")
        
        potential_wind_areas = []
        for y in range(self.rows):
            for x in range(self.cols):
                cell = self.original_grid[y][x]
                if cell in ["0", "", "P"]:
                    potential_wind_areas.append((x, y))
        
        wind_intensity = self.weather_conditions.get('wind_intensity', 0)
        print(f"   Intensidade do vento: {wind_intensity:.2f}")
        
        if wind_intensity > 0.3:
            num_wind_areas = max(1, int(len(potential_wind_areas) * wind_intensity * 0.4))
            wind_cells = random.sample(potential_wind_areas, num_wind_areas)
            for x, y in wind_cells:
                grid_copy[y][x] = "W"
                print(f"    Adicionado W em ({x}, {y})")
        
        return grid_copy

    def find_charging_stations(self):
        """Encontra bases de carregamento"""
        stations = {}
        for y in range(self.rows):
            for x in range(self.cols):
                if self.original_grid[y][x] == "B":
                    stations[(x, y)] = {"type": "charging_station", "charge_rate": 15.0}
        print(f"🔋 Bases de carregamento: {list(stations.keys())}")
        return stations

    def find_delivery_points(self):
        """Encontra pontos de entrega"""
        points = {}
        for y in range(self.rows):
            for x in range(self.cols):
                if self.original_grid[y][x] in ["1", "2", "3", "4"]:
                    points[(x, y)] = {"type": "delivery_point", "delivery_time": 3}
        print(f"📦 Pontos de entrega: {list(points.keys())}")
        return points

    def admissible_heuristic(self, state, agent_name):
        """Heurística baseada na missão atual"""
        current_mission = self.agent_dict[agent_name]["mission"]
        
        if current_mission == "outbound":
            # Indo para entrega
            goal = self.agent_dict[agent_name]["goal"]
        elif current_mission == "inbound":
            # Voltando para base
            goal = self.agent_dict[agent_name]["home_base"]
        else:
            goal = self.agent_dict[agent_name]["goal"]
            
        return abs(goal[0] - state[0]) + abs(goal[1] - state[1])

    def is_mission_complete(self, state, agent_name):
        """Verifica se a missão completa foi concluída"""
        return self.agent_dict[agent_name]["mission_complete"]

    def is_at_goal(self, state, agent_name):
        """Verifica se chegou no objetivo atual da missão"""
        current_mission = self.agent_dict[agent_name]["mission"]
        
        if current_mission == "outbound":
            return state == tuple(self.agent_dict[agent_name]["goal"])
        elif current_mission == "inbound":
            return state == tuple(self.agent_dict[agent_name]["home_base"])
        else:
            return state == tuple(self.agent_dict[agent_name]["goal"])

    def update_mission_status(self, state, agent_name):
        """Atualiza status da missão baseado na posição atual"""
        current_mission = self.agent_dict[agent_name]["mission"]
        
        if current_mission == "outbound" and state == tuple(self.agent_dict[agent_name]["goal"]):
            # Chegou no destino - iniciar entrega
            self.agent_dict[agent_name]["mission"] = "delivering"
            self.agent_dict[agent_name]["delivery_time"] = 3
            print("🎯 Iniciando entrega...")
            return True
            
        elif current_mission == "delivering":
            # Atualizar tempo de entrega
            self.agent_dict[agent_name]["delivery_time"] -= 1
            if self.agent_dict[agent_name]["delivery_time"] <= 0:
                # Entrega concluída - voltar para base
                self.agent_dict[agent_name]["mission"] = "inbound"
                print("📦 Entrega concluída! Voltando para base...")
            return True
            
        elif current_mission == "inbound" and state == tuple(self.agent_dict[agent_name]["home_base"]):
            # Chegou em casa - iniciar repouso
            self.agent_dict[agent_name]["mission"] = "resting"
            self.agent_dict[agent_name]["resting_time"] = 5
            print("🏠 Chegou em casa! Repousando...")
            return True
            
        elif current_mission == "resting":
            # Atualizar tempo de repouso
            self.agent_dict[agent_name]["resting_time"] -= 1
            if self.agent_dict[agent_name]["resting_time"] <= 0:
                # Repouso concluído - missão completa
                self.agent_dict[agent_name]["mission_complete"] = True
                self.agent_dict[agent_name]["battery"] = 100.0  # Bateria cheia
                print("✅ MISSÃO COMPLETA! Drone repousado e carregado.")
            return True
            
        return False

    def is_at_delivery_point(self, state):
        return state in self.delivery_points

    def is_at_charging_station(self, state):
        return state in self.charging_stations

    def is_at_home_base(self, state):
        return state == self.home_base

    def get_neighbors(self, state, current_battery=100.0, ignore_battery=False):
        """Vizinhos considerando bateria"""
        (x, y) = state
        moves = [(1,0), (-1,0), (0,1), (0,-1)]
        neighbors = []

        for dx, dy in moves:
            nx, ny = x + dx, y + dy

            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                cell = self.grid_with_weather[ny][nx]

                if cell in ["X", "x"]:
                    continue
                
                if cell == "A":
                    if self.flight_height == "low" or self.power_mode == "battery_saver":
                        continue
                
                move_cost = self.calculate_move_cost(state, (nx, ny), current_battery)
                if ignore_battery or move_cost <= current_battery:
                    neighbors.append((nx, ny))
                
        return neighbors

    def calculate_move_cost(self, from_pos, to_pos, current_battery):
        """Custo de movimento"""
        base_cost = 1.0
        
        if self.flight_height == "high":
            base_cost *= 1.5
        else:
            base_cost *= 0.8

        tx, ty = to_pos
        if self.grid_with_weather[ty][tx] == "W":
            base_cost *= 2.0

        if self.power_mode == "battery_saver":
            base_cost *= 0.7

        return base_cost

    def get_cell_type(self, position):
        x, y = position
        return self.grid_with_weather[y][x]

    def get_current_goal(self, agent_name):
        """Retorna o objetivo atual baseado na missão"""
        mission = self.agent_dict[agent_name]["mission"]
        if mission == "outbound":
            return self.agent_dict[agent_name]["goal"]
        elif mission == "inbound":
            return self.agent_dict[agent_name]["home_base"]
        else:
            return self.agent_dict[agent_name]["goal"]