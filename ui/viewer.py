import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

class DroneAnimation:
    def __init__(self, grid, schedule):
        self.grid = grid
        self.schedule = schedule
        self.agent_name = list(schedule["schedule"].keys())[0]
        self.path_steps = schedule["schedule"][self.agent_name]
        
    def show(self):
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Desenhar mapa base
        rows = len(self.grid)
        cols = len(self.grid[0])
        
        for y in range(rows):
            for x in range(cols):
                cell = self.grid[y][x]
                color = 'white'
                if cell in ["X", "x"]:
                    color = 'black'
                elif cell == "A":
                    color = 'lightgray'
                elif cell == "S":
                    color = 'limegreen'
                elif cell in ["1", "2", "3", "4"]:
                    color = 'orange'
                elif cell == "*":
                    color = 'red'
                
                ax.add_patch(patches.Rectangle((x-0.5, y-0.5), 1, 1, 
                                             facecolor=color, edgecolor='black'))
                if cell not in ["", "0"]:
                    ax.text(x, y, str(cell), ha='center', va='center', 
                           fontweight='bold', color='white' if color in ['black', 'darkgray'] else 'black')
        
        # Animação do drone
        drone = patches.Circle((0, 0), 0.3, facecolor='red', zorder=10)
        ax.add_patch(drone)
        
        def animate(frame):
            if frame < len(self.path_steps):
                step = self.path_steps[frame]
                drone.center = (step["x"], step["y"])
            return drone,
        
        anim = animation.FuncAnimation(fig, animate, frames=len(self.path_steps), 
                                     interval=500, blit=True, repeat=True)
        
        ax.set_xlim(-0.5, cols-0.5)
        ax.set_ylim(-0.5, rows-0.5)
        ax.set_aspect('equal')
        ax.set_title("Animação do Drone DHL")
        plt.grid(True, alpha=0.3)
        plt.show()