from dataclasses import dataclass
from typing import Tuple, List, Optional

@dataclass
class DroneConfig:
    flight_height: str
    power_mode: str
    max_battery: float = 100.0
    battery_consumption_base: float = 1.0

class Drone:
    def __init__(self, name: str, config: DroneConfig, start_position: Tuple[int, int]):
        self.name = name
        self.config = config
        self.position: Tuple[int, int] = start_position
        self.battery = config.max_battery
        self.distance_traveled: float = 0.0
        self.path_history: List[Tuple[int, int]] = [start_position]
        self.status: str = "active"  # active, charging, out_of_battery, completed
        self.charging_time: int = 0

    def move_to(self, new_position: Tuple[int, int], environment) -> bool:
        """Move o drone para nova posição, retorna False se sem bateria"""
        if self.status == "out_of_battery":
            return False
        
        # Calcular consumo de bateria
        battery_used = environment.calculate_move_cost(self.position, new_position, self.battery)
        
        if battery_used > self.battery:
            self.status = "out_of_battery"
            return False
        
        # Atualizar posição e bateria
        old_position = self.position
        self.position = new_position
        self.battery -= battery_used
        self.distance_traveled += 1
        self.path_history.append(new_position)
        
        # Verificar se chegou em base de carregamento
        cell_type = environment.get_cell_type(new_position)
        if cell_type == "B":
            self.status = "charging"
            self.charging_time = 0
        
        return True

    def charge(self, environment, time_steps: int = 1) -> bool:
        """Recarrega bateria na base"""
        if self.status != "charging":
            return False
        
        charged, new_battery = environment.charge_battery(self.position, self.name, time_steps)
        
        if charged:
            self.battery = new_battery
            self.charging_time += time_steps
            
            # Verificar se terminou de carregar
            if self.battery >= self.config.max_battery * 0.95:  # 95% carregado
                self.status = "active"
                self.charging_time = 0
                return True
            
        return False

    def can_reach(self, distance: float, environment) -> bool:
        """Verifica se pode alcançar uma distância considerando condições"""
        estimated_cost = distance * self.config.battery_consumption_base
        return self.battery >= estimated_cost

    def get_status_info(self) -> dict:
        """Retorna informações de status do drone"""
        return {
            'name': self.name,
            'position': self.position,
            'battery': self.battery,
            'status': self.status,
            'charging_time': self.charging_time,
            'distance_traveled': self.distance_traveled
        }

    def reset(self, start_position: Tuple[int, int]):
        """Reseta o drone para posição inicial"""
        self.position = start_position
        self.battery = self.config.max_battery
        self.distance_traveled = 0.0
        self.path_history = [start_position]
        self.status = "active"
        self.charging_time = 0