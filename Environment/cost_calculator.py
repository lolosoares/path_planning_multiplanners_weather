class CostCalculator:
    @staticmethod
    def calculate_movement_cost(start_pos, end_pos, flight_height, power_mode, grid):
        """
        Calcula o custo de movimento entre duas posições
        Considera altura do voo, modo de potência e tipo de terreno
        """
        base_cost = 1.0
        
        # Custo por altura
        if flight_height == "high":
            base_cost *= 1.5  # +50% de consumo em voo alto
        else:
            base_cost *= 0.8  # -20% de consumo em voo baixo
        
        # Custo por terreno (verifica célula de destino)
        dest_x, dest_y = end_pos
        cell = grid[dest_y][dest_x]
        if cell == "A" and flight_height == "high":
            base_cost *= 1.2  # +20% para sobrevoar áreas A
        
        # Modo economia de bateria
        if power_mode == "battery_saver":
            base_cost *= 0.7  # -30% de consumo
        
        return base_cost
    
    @staticmethod
    def estimate_battery_usage(path_length, flight_height, power_mode):
        """Estima uso de bateria baseado no comprimento do caminho e configurações"""
        base_usage = path_length * 2.0  # 2 unidades por passo base
        
        if flight_height == "high":
            base_usage *= 1.6  # +60% em voo alto
        else:
            base_usage *= 0.7  # -30% em voo baixo
        
        if power_mode == "battery_saver":
            base_usage *= 0.6  # -40% adicional em modo economia
        
        return base_usage
    
    @staticmethod
    def estimate_time(path_length, flight_height):
        """Estima tempo de voo baseado no comprimento do caminho e altura"""
        base_time = path_length * 3.0  # 3 segundos por passo base
        
        if flight_height == "high":
            base_time *= 0.7  # -30% de tempo em voo alto (mais rápido)
        else:
            base_time *= 1.2  # +20% de tempo em voo baixo (mais lento)
        
        return base_time
    
    @staticmethod
    def calculate_total_cost(path, flight_height, power_mode, grid):
        """Calcula custo total de um caminho completo"""
        if not path or len(path) < 2:
            return 0
        
        total_cost = 0
        for i in range(len(path) - 1):
            cost = CostCalculator.calculate_movement_cost(
                path[i], path[i + 1], flight_height, power_mode, grid
            )
            total_cost += cost
        
        return total_cost