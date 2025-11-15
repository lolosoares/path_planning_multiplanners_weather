from typing import Dict, List, Tuple
import time

class StatisticsCalculator:
    @staticmethod
    def calculate_path_statistics(path: List[Tuple[int, int]], algorithm: str, 
                                 computation_time: float, nodes_explored: int = 0) -> Dict:
        """
        Calcula estatísticas completas para um caminho
        """
        if not path:
            return {
                'algorithm': algorithm,
                'path_length': 0,
                'computation_time': computation_time,
                'nodes_explored': nodes_explored,
                'status': 'no_path'
            }
        
        # Calcular várias métricas
        straight_line_distance = StatisticsCalculator.calculate_straight_line_distance(path)
        turns = StatisticsCalculator.count_turns(path)
        
        return {
            'algorithm': algorithm,
            'path_length': len(path),
            'computation_time': computation_time,
            'nodes_explored': nodes_explored,
            'straight_line_distance': straight_line_distance,
            'efficiency_ratio': straight_line_distance / len(path) if len(path) > 0 else 0,
            'turns_count': turns,
            'status': 'success'
        }
    
    @staticmethod
    def calculate_straight_line_distance(path: List[Tuple[int, int]]) -> float:
        """Calcula distância em linha reta entre start e goal"""
        if len(path) < 2:
            return 0
        start = path[0]
        goal = path[-1]
        return abs(goal[0] - start[0]) + abs(goal[1] - start[1])
    
    @staticmethod
    def count_turns(path: List[Tuple[int, int]]) -> int:
        """Conta número de mudanças de direção no caminho"""
        if len(path) < 3:
            return 0
        
        turns = 0
        for i in range(1, len(path) - 1):
            prev = path[i-1]
            curr = path[i]
            next_pos = path[i+1]
            
            # Verificar se há mudança de direção
            dx1 = curr[0] - prev[0]
            dy1 = curr[1] - prev[1]
            dx2 = next_pos[0] - curr[0]
            dy2 = next_pos[1] - curr[1]
            
            # Se a direção mudou, é uma curva
            if (dx1, dy1) != (dx2, dy2):
                turns += 1
        
        return turns
    
    @staticmethod
    def compare_algorithms_results(results: List[Dict]) -> Dict:
        """
        Compara resultados de múltiplos algoritmos
        """
        if not results:
            return {}
        
        comparison = {
            'best_by_length': None,
            'best_by_time': None,
            'best_by_efficiency': None,
            'all_results': results
        }
        
        valid_results = [r for r in results if r['status'] == 'success']
        
        if valid_results:
            comparison['best_by_length'] = min(valid_results, key=lambda x: x['path_length'])
            comparison['best_by_time'] = min(valid_results, key=lambda x: x['computation_time'])
            comparison['best_by_efficiency'] = max(valid_results, key=lambda x: x['efficiency_ratio'])
        
        return comparison
    
    @staticmethod
    def generate_report(comparison: Dict, flight_height: str, power_mode: str) -> str:
        """Gera relatório completo em formato de texto"""
        report = "📊 RELATÓRIO DE ANÁLISE DE ALGORITMOS\n\n"
        report += f"Configurações: Altura {flight_height}, Modo {power_mode}\n"
        report += f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "RESULTADOS INDIVIDUAIS:\n"
        for result in comparison.get('all_results', []):
            report += f"\n🔹 {result['algorithm']}:\n"
            if result['status'] == 'success':
                report += f"   • Comprimento: {result['path_length']} passos\n"
                report += f"   • Tempo computação: {result['computation_time']:.3f}s\n"
                report += f"   • Nós explorados: {result['nodes_explored']}\n"
                report += f"   • Curvas: {result['turns_count']}\n"
                report += f"   • Eficiência: {result['efficiency_ratio']:.2f}\n"
            else:
                report += "   • ❌ Nenhuma rota encontrada\n"
        
        # Melhores resultados
        report += "\n🏆 MELHORES RESULTADOS:\n"
        if comparison['best_by_length']:
            report += f"• Menor caminho: {comparison['best_by_length']['algorithm']} "
            report += f"({comparison['best_by_length']['path_length']} passos)\n"
        
        if comparison['best_by_time']:
            report += f"• Mais rápido: {comparison['best_by_time']['algorithm']} "
            report += f"({comparison['best_by_time']['computation_time']:.3f}s)\n"
        
        if comparison['best_by_efficiency']:
            report += f"• Mais eficiente: {comparison['best_by_efficiency']['algorithm']} "
            report += f"(ratio: {comparison['best_by_efficiency']['efficiency_ratio']:.2f})\n"
        
        return report