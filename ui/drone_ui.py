import random
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches

from algorithms.astar import AStar
from algorithms.ucs import UCS
from algorithms.ids import IDS
from Environment.environment import Environment
from models.drone import Drone, DroneConfig
from ui.multi_drone_animation import MultiDroneAnimation
from utils.statistics import StatisticsCalculator

class DroneControlUI:
    def __init__(self, grid):
        self.grid = grid
        self.start = None
        self.destinations = {}
        self.current_height = "low"
        self.power_mode = "normal"
        self.find_positions()
        
    def find_positions(self):
        """Encontra start e destinos no mapa"""
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == "S":
                    self.start = [x, y]
                elif cell in ["1", "2", "3", "4"]:
                    self.destinations[cell] = [x, y]
    
    def create_ui(self):
        """Cria a interface gráfica"""
        self.root = tk.Tk()
        self.root.title("DHL Drone Path Planning - Multi-Algorithm")
        self.root.geometry("1200x800")
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controle (lado esquerdo)
        control_frame = ttk.LabelFrame(main_frame, text="Configurações do Drone", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Frame do mapa (lado direito)
        map_frame = ttk.LabelFrame(main_frame, text="Mapa da Cidade", padding=10)
        map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Controles de altura
        height_frame = ttk.LabelFrame(control_frame, text="Altura de Voo", padding=5)
        height_frame.pack(fill=tk.X, pady=5)
        
        self.height_var = tk.StringVar(value="low")
        
        ttk.Radiobutton(height_frame, text="Baixa (20m) - Economia de Bateria", 
                       variable=self.height_var, value="low",
                       command=self.on_height_change).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(height_frame, text="Alta (50m) - Velocidade", 
                       variable=self.height_var, value="high",
                       command=self.on_height_change).pack(anchor=tk.W, pady=2)
        
        # Modo de potência
        power_frame = ttk.LabelFrame(control_frame, text="Modo de Potência", padding=5)
        power_frame.pack(fill=tk.X, pady=5)
        
        self.power_var = tk.StringVar(value="normal")
        
        ttk.Radiobutton(power_frame, text="Normal - Performance", 
                       variable=self.power_var, value="normal",
                       command=self.on_power_change).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(power_frame, text="Economia de Bateria", 
                       variable=self.power_var, value="battery_saver",
                       command=self.on_power_change).pack(anchor=tk.W, pady=2)
        
        # Seleção de destino
        dest_frame = ttk.LabelFrame(control_frame, text="Destino da Entrega", padding=5)
        dest_frame.pack(fill=tk.X, pady=5)
        
        self.dest_var = tk.StringVar(value="1")
        for dest in sorted(self.destinations.keys()):
            ttk.Radiobutton(dest_frame, text=f"Ponto de Entrega {dest}", 
                           variable=self.dest_var, value=dest).pack(anchor=tk.W, pady=2)
        
        # Botões de ação
        button_frame = ttk.LabelFrame(control_frame, text="Ações", padding=5)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Calcular Rota (A*)", 
                  command=self.calculate_astar_route).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Comparar Todos Algoritmos", 
                  command=self.calculate_all_routes).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Animação 3 Drones", 
                  command=self.show_multi_animation).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Estatísticas Detalhadas", 
                  command=self.show_detailed_stats).pack(fill=tk.X, pady=2)
        
        # Informações
        info_frame = ttk.LabelFrame(control_frame, text="Informações do Sistema", padding=5)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = tk.Text(info_frame, height=12, width=35, font=("Arial", 9))
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mapa
        self.setup_map_display(map_frame)
        
        self.update_info()
    
    def setup_map_display(self, parent):
        """Configura a exibição do mapa"""
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.draw_map()
    
    def draw_map(self):
        """Desenha o mapa atualizado"""
        self.ax.clear()
        
        rows = len(self.grid)
        cols = len(self.grid[0])
        
        # Definir cores baseado nas configurações
        for y in range(rows):
            for x in range(cols):
                cell = self.grid[y][x]
                color = 'white'
                
                if cell == "S":
                    color = 'limegreen'
                elif cell in ["1", "2", "3", "4"]:
                    color = 'orange'
                elif cell in ["X", "x"]:
                    color = 'black'
                elif cell == "A":
                    if self.current_height == "low" or self.power_mode == "battery_saver":
                        color = 'darkgray'
                    else:
                        color = 'lightblue'
                
                self.ax.add_patch(plt.Rectangle((x-0.5, y-0.5), 1, 1, 
                                              facecolor=color, edgecolor='black', linewidth=0.5))
                
                if cell not in ["", "0"]:
                    text_color = 'white' if color in ['black', 'darkgray'] else 'black'
                    self.ax.text(x, y, str(cell), ha='center', va='center', 
                               fontweight='bold', color=text_color, fontsize=8)
        
        self.ax.set_xlim(-0.5, cols-0.5)
        self.ax.set_ylim(-0.5, rows-0.5)
        self.ax.set_aspect('equal')
        self.ax.set_title(f"Mapa DHL - Altura: {'20m' if self.current_height == 'low' else '50m'} | "
                         f"Modo: {'Eco' if self.power_mode == 'battery_saver' else 'Normal'}", 
                         fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.2)
        
        self.canvas.draw()
    
    def on_height_change(self):
        """Callback quando a altura muda"""
        self.current_height = self.height_var.get()
        if self.power_mode == "battery_saver" and self.current_height == "high":
            messagebox.showwarning("Configuração Inconsistente", 
                                 "Modo economia de bateria força voo baixo (20m)!")
            self.current_height = "low"
            self.height_var.set("low")
        
        self.draw_map()
        self.update_info()
    
    def on_power_change(self):
        """Callback quando o modo de potência muda"""
        self.power_mode = self.power_var.get()
        if self.power_mode == "battery_saver":
            self.current_height = "low"
            self.height_var.set("low")
        
        self.draw_map()
        self.update_info()
    
    def update_info(self):
        """Atualiza informações exibidas"""
        a_status = "OBSTÁCULO" if self.current_height == "low" or self.power_mode == "battery_saver" else "SOBREVOÁVEL"
        
        info = f"""CONFIGURAÇÕES ATUAIS:

🏗️  Altura: {'20m (Baixa)' if self.current_height == 'low' else '50m (Alta)'}
⚡ Modo: {'Economia de Bateria' if self.power_mode == 'battery_saver' else 'Normal'}
🎯 Destino: {self.dest_var.get()}

CARACTERÍSTICAS:
• Voo baixo (20m): +Economia de bateria
• Voo alto (50m): +Velocidade, pode sobrevoar 'A'
• Modo economia: Força voo baixo

ESTADO DOS OBSTÁCULOS:
• Prédios 'A': {a_status}
• Prédios 'X': SEMPRE OBSTÁCULOS

ALGORITMOS DISPONÍVEIS:
• A*: Caminho mais curto (heurística)
• Custo Uniforme: Menor consumo
• Prof. Iterativa: Busca progressiva"""
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
    
    def calculate_astar_route(self):
        """Calcula rota apenas com A*"""
        try:
            selected_dest = self.dest_var.get()
            goal = self.destinations[selected_dest]
            
            env = Environment(self.grid, self.start, goal, 
                            flight_height=self.current_height,
                            power_mode=self.power_mode)
            
            planner = AStar(env)
            path = planner.search("agent0")
            
            if path:
                self.current_path = path
                self.draw_single_path(path, "A*", "red")
                messagebox.showinfo("Sucesso", 
                                  f"A*: Rota para destino {selected_dest}!\n"
                                  f"Distância: {len(path)} passos")
            else:
                messagebox.showerror("Erro", "A*: Não foi possível encontrar uma rota!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no A*: {str(e)}")
    
    def calculate_all_routes(self):
        """Calcula rotas com todos os algoritmos simultaneamente"""
        try:
            selected_dest = self.dest_var.get()
            goal = self.destinations[selected_dest]
            
            # Condições climáticas
            weather_conditions = {
                'wind_intensity': random.uniform(0, 1.0),
                'temperature': random.uniform(15, 35)
            }
            
            print(f"🌤️  Condições: Vento {weather_conditions['wind_intensity']:.1f}")
            
            env = Environment(self.grid, self.start, goal, 
                            flight_height=self.current_height,
                            power_mode=self.power_mode,
                            weather_conditions=weather_conditions)
            
            # Executar TODOS os algoritmos
            algorithms = {
                "A*": AStar(env),
                "Custo Uniforme": UCS(env), 
                "Profundidade Iterativa": IDS(env)
            }
            
            self.all_paths = {}
            self.all_schedules = {}
            
            print("=== EXECUTANDO TODOS OS ALGORITMOS ===")
            for algo_name, planner in algorithms.items():
                print(f"\n🎯 Executando {algo_name}...")
                path = planner.search("agent0")
                self.all_paths[algo_name] = path
                self.all_schedules[algo_name] = self.path_to_schedule(path)
                
                if path:
                    print(f"✅ {algo_name}: {len(path)} passos na missão completa")
                else:
                    print(f"❌ {algo_name}: Falhou na missão")
            
            # 🔥 CORREÇÃO: Mostrar animação diretamente após cálculo
            self.draw_all_paths()
            self.show_comparison_stats()
            
            # Mostrar animação automaticamente
            self.show_advanced_animation()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular rotas: {str(e)}")
            import traceback
            traceback.print_exc()
        
    def show_advanced_animation(self):
        """Mostra animação com sistema de bateria - CORRIGIDO"""
        if hasattr(self, 'all_schedules'):
            try:
                # Criar environment para a animação (mesmo usado nos cálculos)
                selected_dest = self.dest_var.get()
                goal = self.destinations[selected_dest]
                
                weather_conditions = {
                    'wind_intensity': random.uniform(0, 1.0),
                    'temperature': random.uniform(15, 35)
                }
                
                env = Environment(self.grid, self.start, goal, 
                                flight_height=self.current_height,
                                power_mode=self.power_mode,
                                weather_conditions=weather_conditions)
                
                # 🔥 CORREÇÃO: Passar apenas os argumentos necessários
                anim = MultiDroneAnimation(
                    grid=self.grid,
                    all_schedules=self.all_schedules,
                    environment=env  # ✅ Agora passando o environment
                )
                anim.show()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro na animação: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            messagebox.showwarning("Aviso", "Calcule as rotas com 'Comparar Todos Algoritmos' primeiro!")
            
    def draw_single_path(self, path, algo_name, color):
        """Desenha um único caminho no mapa"""
        self.draw_map()
        
        if len(path) > 1:
            x_coords = [pos[0] for pos in path]
            y_coords = [pos[1] for pos in path]
            
            self.ax.plot(x_coords, y_coords, '-', linewidth=3, 
                        alpha=0.8, color=color, label=algo_name)
            self.ax.scatter(x_coords, y_coords, c=color, s=50, zorder=5)
        
        self.ax.legend()
        self.canvas.draw()
    
    def draw_all_paths(self):
        """Desenha todos os caminhos no mapa com cores diferentes"""
        self.draw_map()
        
        colors = {
            "A*": "red",
            "Custo Uniforme": "blue", 
            "Profundidade Iterativa": "green"
        }
        
        for algo_name, path in self.all_paths.items():
            if path and len(path) > 1:
                x_coords = [pos[0] for pos in path]
                y_coords = [pos[1] for pos in path]  # CORREÇÃO: era 'yords'
            
                self.ax.plot(x_coords, y_coords, '-', linewidth=2, 
                            alpha=0.7, color=colors[algo_name], label=algo_name)
                self.ax.scatter(x_coords, y_coords, c=colors[algo_name], 
                            s=30, zorder=5, alpha=0.8)
    
        self.ax.legend(loc='upper right')
        self.canvas.draw()
    
    def path_to_schedule(self, path):
        """Converte path para formato de schedule"""
        schedule = {"schedule": {"agent0": []}}
        t = 0
        for (x, y) in path:
            schedule["schedule"]["agent0"].append({"t": t, "x": x, "y": y})
            t += 1
        return schedule
    
    def show_multi_animation(self):
        """Mostra animação com 3 drones"""
        if hasattr(self, 'all_schedules'):
            try:
                # Verificar se há caminhos válidos
                valid_schedules = {k: v for k, v in self.all_schedules.items() 
                                if v and v["schedule"]["agent0"]}
                if not valid_schedules:
                    messagebox.showwarning("Aviso", "Nenhum algoritmo encontrou uma rota válida!")
                    return
                
                anim = MultiDroneAnimation(self.grid, self.all_schedules)
                anim.show()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro na animação: {str(e)}")
        else:
            messagebox.showwarning("Aviso", "Calcule as rotas com 'Comparar Todos Algoritmos' primeiro!")
    
    def show_comparison_stats(self):
        """Mostra estatísticas comparativas dos 3 algoritmos"""
        if not hasattr(self, 'all_paths'):
            return
        
        stats_text = "📊 COMPARAÇÃO DE ALGORITMOS\n\n"
        stats_text += f"Destino: {self.dest_var.get()}\n"
        stats_text += f"Altura: {'20m' if self.current_height == 'low' else '50m'}\n"
        stats_text += f"Modo: {'Eco' if self.power_mode == 'battery_saver' else 'Normal'}\n\n"
        
        for algo_name, path in self.all_paths.items():
            length = len(path) if path else 0
            
            # Cálculo de custo simplificado
            if algo_name == "Custo Uniforme":
                cost = length * (0.8 if self.current_height == "low" else 1.0)
            elif algo_name == "A*":
                cost = length * (1.0 if self.current_height == "low" else 1.5)
            else:  # IDS
                cost = length * (1.0 if self.current_height == "low" else 1.5)
            
            status = "✅ Rota encontrada" if path else "❌ Sem rota"
            
            stats_text += f"🔹 {algo_name}:\n"
            stats_text += f"   • Passos: {length}\n"
            stats_text += f"   • Custo: {cost:.1f}\n"
            stats_text += f"   • Tempo: {length * 2}s\n"
            stats_text += f"   • Status: {status}\n\n"
        
        # Encontrar melhores
        valid_paths = {algo: path for algo, path in self.all_paths.items() if path}
        if valid_paths:
            best_length_algo = min(valid_paths.keys(), key=lambda x: len(valid_paths[x]))
            stats_text += f"🏆 Melhor desempenho: {best_length_algo}\n"
            stats_text += f"📏 Menor caminho: {best_length_algo}"
        
        messagebox.showinfo("Comparação de Algoritmos", stats_text)
    
    def show_detailed_stats(self):
        """Mostra estatísticas detalhadas"""
        if hasattr(self, 'all_paths'):
            comparator = StatisticsCalculator(self.all_paths, self.current_height, self.power_mode)
            detailed_stats = comparator.get_detailed_comparison()
            messagebox.showinfo("Estatísticas Detalhadas", detailed_stats)
        else:
            messagebox.showwarning("Aviso", "Calcule as rotas primeiro!")
    
    def run(self):
        """Executa a aplicação"""
        self.create_ui()
        self.root.mainloop()