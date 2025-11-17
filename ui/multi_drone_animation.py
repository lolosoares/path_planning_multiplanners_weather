import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import numpy as np

class MultiDroneAnimation:
    def __init__(self, grid, all_schedules, environment):
        self.grid = grid
        self.all_schedules = all_schedules
        self.environment = environment
        self.algorithms = list(all_schedules.keys())
        
        # 🔥 NOVO: Expandir schedules com pausas reais
        self.expanded_schedules = self.create_expanded_schedules()
        
    def create_expanded_schedules(self):
        """Cria schedules expandidos com pausas reais para entrega e repouso"""
        expanded = {}
        
        for algo in self.algorithms:
            original_schedule = self.all_schedules[algo]["schedule"]["agent0"]
            expanded_schedule = []
            delivery_completed = False
            return_completed = False
            
            for i, step in enumerate(original_schedule):
                current_pos = (step["x"], step["y"])
                expanded_schedule.append(step)  # Passo normal
                
                # 🔥 VERIFICAR SE CHEGOU NA ENTREGA PELA PRIMEIRA VEZ
                if (not delivery_completed and 
                    current_pos == tuple(self.environment.agent_dict["agent0"]["goal"])):
                    
                    # 🔥 ADICIONAR PAUSA REAL PARA ENTREGA (5 frames)
                    print(f"🚚 {algo}: Iniciando entrega em {current_pos}")
                    for j in range(5):  # 5 frames de entrega
                        expanded_schedule.append({
                            "t": step["t"] + j + 1,
                            "x": step["x"], 
                            "y": step["y"],
                            "action": "delivering",
                            "battery_saved": True  # 🔥 Não consome bateria
                        })
                    delivery_completed = True
                
                # 🔥 VERIFICAR SE CHEGOU EM CASA PELA PRIMEIRA VEZ
                elif (not return_completed and 
                      current_pos == tuple(self.environment.agent_dict["agent0"]["home_base"]) and
                      delivery_completed):
                    
                    # 🔥 ADICIONAR PAUSA REAL PARA REPOUSO (8 frames)
                    print(f"🏠 {algo}: Iniciando repouso em {current_pos}")
                    for j in range(8):  # 8 frames de repouso
                        expanded_schedule.append({
                            "t": step["t"] + j + 1,
                            "x": step["x"], 
                            "y": step["y"], 
                            "action": "resting",
                            "battery_saved": True  # 🔥 Não consome bateria
                        })
                    return_completed = True
            
            expanded[algo] = expanded_schedule
            print(f"📊 {algo}: {len(original_schedule)} → {len(expanded_schedule)} passos (com pausas)")
        
        return expanded

    def show(self):
        """Mostra a animação com pausas reais"""
        try:
            fig, (ax, ax_status) = plt.subplots(2, 1, figsize=(14, 12), 
                                               gridspec_kw={'height_ratios': [3, 1]})
            
            # Desenhar mapa base
            rows = len(self.grid)
            cols = len(self.grid[0])
            
            for y in range(rows):
                for x in range(cols):
                    cell_type = self.environment.get_cell_type((x, y))
                    color = self.get_cell_color(cell_type)
                    
                    ax.add_patch(patches.Rectangle((x-0.5, y-0.5), 1, 1, 
                                                 facecolor=color, edgecolor='black', alpha=0.8))
                    
                    if cell_type not in ["", "0"]:
                        text_color = 'white' if color in ['black', 'darkblue'] else 'black'
                        ax.text(x, y, str(cell_type), ha='center', va='center', 
                               fontweight='bold', color=text_color, fontsize=8)
            
            # Configuração dos drones
            drone_configs = {
                "A*": {"color": "red", "shape": "circle", "size": 0.4},
                "Custo Uniforme": {"color": "blue", "shape": "square", "size": 0.25},
                "Profundidade Iterativa": {"color": "green", "shape": "triangle", "size": 0.35}
            }
            
            drones = {}
            battery_levels = {algo: 100.0 for algo in self.algorithms}
            mission_states = {algo: "outbound" for algo in self.algorithms}
            action_states = {algo: "moving" for algo in self.algorithms}  # 🔥 NOVO: Estado de ação
            
            #Desenhar caminho
            for algo in self.algorithms:
                if algo in drone_configs:
                    config = drone_configs[algo]
                    schedule = self.expanded_schedules[algo]
                    
                    # DEBUG: Verificar o que temos
                    print(f"🔍 {algo}: {len(schedule)} passos no schedule expandido")
                    
                    # 🎨 DESENHAR LINHA DA TRAJETÓRIA
                    if len(schedule) > 1:
                        # Filtrar apenas posições únicas (sem repetições de pausa)
                        unique_positions = []
                        last_pos = None
                        
                        for step in schedule:
                            current_pos = (step["x"], step["y"])
                            if current_pos != last_pos:
                                unique_positions.append(current_pos)
                                last_pos = current_pos
                        
                        if len(unique_positions) > 1:
                            x_coords = [pos[0] for pos in unique_positions]
                            y_coords = [pos[1] for pos in unique_positions]
                            
                            print(f"🎨 {algo}: Desenhando linha com {len(unique_positions)} pontos")
                            
                            # Desenhar a linha da trajetória
                            line_style = 'solid' if algo == "A*" else 'dashed' if algo == "Custo Uniforme" else 'dotted'
                            line_width = 3 if algo == "A*" else 2
                            
                            ax.plot(x_coords, y_coords, 
                                linestyle=line_style,
                                linewidth=line_width,
                                alpha=0.7, 
                                color=config["color"], 
                                label=f"{algo}")
                        else:
                            print(f"⚠️ {algo}: Não há pontos suficientes para desenhar linha")
            
            # Inicializar drones
            for algo in self.algorithms:
                if algo in drone_configs:
                    schedule = self.expanded_schedules[algo]
                    
                    if schedule:
                        start_x, start_y = schedule[0]["x"], schedule[0]["y"]
                        drone = self.create_drone(drone_configs[algo], start_x, start_y)
                        ax.add_patch(drone)
                        drones[algo] = drone
            
            # Encontrar máximo de steps
            max_steps = max(len(schedule) for schedule in self.expanded_schedules.values())
            
            if max_steps == 0:
                ax.set_title("Nenhum caminho encontrado")
                plt.show()
                
                print("Animação finalizada. Pressione ENTER para fechar a janela...")
                input()
                return
            
            # Configurar painel de status
            status_elements = self.setup_status_panel(ax_status)
            
            # Animação
            anim = animation.FuncAnimation(
                fig, 
                self.create_animation_func(drones, battery_levels, mission_states, action_states, status_elements, max_steps), 
                frames=max_steps, 
                interval=600,
                blit=True, 
                repeat=True
            )
            
            ax.legend(loc='upper right', fontsize=10)
            ax.set_xlim(-0.5, cols-0.5)
            ax.set_ylim(-0.5, rows-0.5)
            ax.set_aspect('equal')
            ax.set_title("Sistema com Pausas Reais - Entrega e Repouso", fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            
        except Exception as e:
            print(f"Erro na animação: {e}")
            import traceback
            traceback.print_exc()
            plt.close(fig)
    
    def get_cell_color(self, cell_type):
        """Retorna cor baseada no tipo de célula"""
        color_map = {
            "X": 'black', "x": 'black',
            "A": 'lightgray', 
            "S": 'limegreen',
            "1": 'orange', "2": 'orange', "3": 'orange', "4": 'orange',
            "B": 'gold',
            "W": 'lightblue'
        }
        return color_map.get(cell_type, 'white')
    
    def create_drone(self, config, x, y):
        """Cria um drone baseado na configuração"""
        if config["shape"] == "circle":
            return patches.Circle((x, y), config["size"], 
                                facecolor=config["color"], edgecolor='black', zorder=20)
        elif config["shape"] == "square":
            return patches.Rectangle((x-config["size"], y-config["size"]), 
                                   config["size"]*2, config["size"]*2,
                                   facecolor=config["color"], edgecolor='black', zorder=20)
        else:  # triangle
            return patches.RegularPolygon((x, y), 3, radius=config["size"],
                                       facecolor=config["color"], edgecolor='black', zorder=20)
    
    def setup_status_panel(self, ax_status):
        """Configura o painel de status"""
        status_text = ax_status.text(0.02, 0.8, '', transform=ax_status.transAxes, 
                                   fontsize=9, fontweight='bold',
                                   bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        battery_bars = {}
        battery_texts = {}
        
        for i, algo in enumerate(self.algorithms):
            battery_bar = patches.Rectangle((0.02 + i*0.3, 0.4), 0.2, 0.3, 
                                          facecolor='lightgreen', edgecolor='black')
            ax_status.add_patch(battery_bar)
            battery_bars[algo] = battery_bar
            
            battery_text = ax_status.text(0.12 + i*0.3, 0.55, f"{algo}\n100%", 
                                        ha='center', va='center', fontsize=8, fontweight='bold')
            battery_texts[algo] = battery_text
        
        ax_status.set_xlim(0, 1)
        ax_status.set_ylim(0, 1)
        ax_status.axis('off')
        ax_status.set_title('Sistema com Pausas - Bateria Economizada', fontsize=12, fontweight='bold')
        
        return {
            'status_text': status_text,
            'battery_bars': battery_bars,
            'battery_texts': battery_texts
        }
    
    def create_animation_func(self, drones, battery_levels, mission_states, action_states, status_elements, max_steps):
        """Cria a função de animação com sistema de pausas"""
        def animate(frame):
            current_info = f"⏱️  Frame: {frame}/{max_steps}\n\n"
            elements_to_update = []
            
            for algo in self.algorithms:
                if algo in drones:
                    schedule = self.expanded_schedules[algo]
                    
                    if frame < len(schedule):
                        step = schedule[frame]
                        current_pos = (step["x"], step["y"])
                        
                        # 🔥 MOVER DRONE (sempre)
                        drones[algo].center = current_pos
                        
                        # 🔥 ATUALIZAR ESTADOS DA MISSÃO
                        mission_info, action_info = self.update_mission_states(
                            algo, current_pos, mission_states, action_states, frame, schedule, step
                        )
                        
                        # 🔥 ATUALIZAR BATERIA (SÓ SE NÃO ESTIVER EM PAUSA)
                        battery_consumed = self.update_battery_with_pauses(
                            algo, current_pos, battery_levels, frame, schedule, step, action_states[algo]
                        )
                        
                        # 🔥 EMOJIS E STATUS
                        status_display = self.get_status_display(mission_states[algo], action_states[algo], battery_consumed)
                        current_info += f"{status_display['emoji']} {algo}: {status_display['text']}\n"
                        
                    else:
                        # Missão completa
                        mission_states[algo] = "complete"
                        action_states[algo] = "finished"
                        battery_levels[algo] = 100.0  # Bateria cheia no final
                        current_info += f"✅ {algo}: MISSÃO CONCLUÍDA\n"
                    
                    # Atualizar display da bateria
                    self.update_battery_display(algo, battery_levels[algo], status_elements)
                    elements_to_update.extend([
                        drones[algo], 
                        status_elements['battery_bars'][algo], 
                        status_elements['battery_texts'][algo]
                    ])
            
            status_elements['status_text'].set_text(current_info)
            elements_to_update.append(status_elements['status_text'])
            
            return elements_to_update
        
        return animate
    
    def update_mission_states(self, algo, current_pos, mission_states, action_states, frame, schedule, step):
        """
        Atualiza estados da missão sem loops.
        Transições:
            outbound → delivering → inbound → resting → complete
        """

        goal = tuple(self.environment.agent_dict["agent0"]["goal"])
        home = tuple(self.environment.agent_dict["agent0"]["home_base"])

        # ============================================================
        # 1. PRIORIDADE MÁXIMA: AÇÕES FORÇADAS PELO SCHEDULE (delivering/resting)
        # ============================================================
        if "action" in step:
            action = step["action"]

            if action == "delivering":
                action_states[algo] = "delivering"
                mission_states[algo] = "delivering"
                return "ENTREGANDO", "paused"

            elif action == "resting":
                action_states[algo] = "resting"
                mission_states[algo] = "resting"
                return "REPOUSANDO", "paused"

        else:
            # Sem ação especial → o agente está se movendo
            action_states[algo] = "moving"

        # ============================================================
        # 2. TRANSIÇÕES BASEADAS EM POSIÇÃO
        # ============================================================

        # ---- OUTBOUND → DELIVERING ----
        if current_pos == goal and mission_states[algo] == "outbound":
            mission_states[algo] = "delivering"
            return "CHEGOU NA ENTREGA", "moving"

        # ---- INBOUND → RESTING ----
        if current_pos == home and mission_states[algo] == "inbound":
            mission_states[algo] = "resting"
            return "CHEGOU EM CASA", "moving"

        # ---- RESTING → COMPLETE ----
        if mission_states[algo] == "resting" and action_states[algo] == "moving":
            mission_states[algo] = "complete"
            return "MISSÃO CONCLUÍDA", "finished"

        # ============================================================
        # 3. SEM TRANSIÇÃO → MANTER ESTADO ATUAL
        # ============================================================

        return mission_states[algo].upper(), action_states[algo]

    def update_battery_with_pauses(self, algo, current_pos, battery_levels, frame, schedule, step, action_state):
        """Atualiza bateria considerando pausas"""
        battery_consumed = False
        
        # 🔥 SÓ CONSUME BATERIA SE ESTIVER SE MOVENDO E NÃO ESTIVER EM PAUSA
        if (action_state == "moving" and 
            frame > 0 and 
            "battery_saved" not in step):
            
            prev_step = schedule[frame-1]
            prev_pos = (prev_step["x"], prev_step["y"])
            
            # Só consome se realmente mudou de posição
            if current_pos != prev_pos:
                move_cost = self.environment.calculate_move_cost(prev_pos, current_pos, battery_levels[algo])
                battery_levels[algo] = max(0, battery_levels[algo] - move_cost)
                battery_consumed = True
                # print(f"🔋 {algo} consumiu {move_cost:.1f} de bateria")
        
        # 🔥 RECARREGAR SE ESTIVER EM BASE (mesmo em movimento)
        if self.environment.is_at_charging_station(current_pos):
            battery_levels[algo] = min(100, battery_levels[algo] + 3)
            # print(f"⚡ {algo} recarregando na base")
        
        return battery_consumed
    
    def get_status_display(self, mission_state, action_state, battery_consumed):
        """Retorna emoji e texto para display"""
        status_map = {
            "outbound": {"emoji": "🛩️", "text": "INDO PARA ENTREGA"},
            "delivering": {"emoji": "📦", "text": "FAZENDO ENTREGA" + (" ⏸️" if action_state == "paused" else "")},
            "inbound": {"emoji": "🏠", "text": "VOLTANDO PARA CASA"},
            "resting": {"emoji": "😴", "text": "REPOUSANDO" + (" ⏸️" if action_state == "paused" else "")},
            "complete": {"emoji": "✅", "text": "MISSÃO CONCLUÍDA"}
        }
        
        display = status_map.get(mission_state, {"emoji": "⚫", "text": mission_state})
        
        # 🔥 INDICAR SE ESTÁ ECONOMIZANDO BATERIA
        if action_state == "paused" and not battery_consumed:
            display["text"] += " 🔋ECONOMIA"
        
        return display
    
    def update_battery_display(self, algo, battery_level, status_elements):
        """Atualiza display da bateria"""
        battery_percentage = max(0, battery_level)
        battery_width = 0.2 * (battery_percentage / 100.0)
        
        if battery_percentage > 70: 
            bat_color = 'lightgreen'
        elif battery_percentage > 30: 
            bat_color = 'yellow'
        else: 
            bat_color = 'red'
        
        status_elements['battery_bars'][algo].set_width(battery_width)
        status_elements['battery_bars'][algo].set_facecolor(bat_color)
        status_elements['battery_texts'][algo].set_text(f"{algo}\n{int(battery_percentage)}%")