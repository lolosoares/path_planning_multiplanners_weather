# Cenários de Teste e Resultados

Este documento descreve os 8 cenários de teste realizados para avaliar o desempenho e a viabilidade dos algoritmos A*, Custo Uniforme (UCS) e Busca em Profundidade Iterativa (IDS) no planejamento de rotas de drones de entrega. Cada cenário varia parâmetros como altura de voo, condições climáticas (vento) e o objetivo final, registrando métricas de desempenho e o status da missão.

---

## Cenário 1: Altura Baixa, Sem Vento (Sem Rota)

**Parâmetros:**
* **Destino:** 1
* **Altura de Voo:** Baixa
* **Potência:** Normal
* **Vento:** 0
* **Algoritmos Testados:** A*, UCS, IDS

**Resultados:**
* **Nós Expandidos (A*/UCS/IDS):** 0 / 0 / 0
* **Passos (A*/UCS/IDS):** 0 / 0 / 0
* **Custo (A*/UCS/IDS):** 0 / 0 / 0
* **Bateria (A*/UCS/IDS):** 0 / 0 / 0
* **Status:** Sem rota para todos os algoritmos.

**Comentários:**
Devido à natureza da região de estudo, não foi encontrado um caminho que pudesse ser usado pelo drone nessas condições (voo baixo). Isso indica que o drone precisaria planejar a rota em uma altura mais elevada para ser viável.

---

## Cenário 2: Altura Alta, Vento Moderado (Completo - A*/UCS)

**Parâmetros:**
* **Destino:** 1
* **Altura de Voo:** Alta
* **Potência:** Normal
* **Vento:** 0.98
* **Algoritmos Testados:** A*, UCS, IDS

**Resultados:**
* **A\*:**
    * **Nós Expandidos:** 18548
    * **Passos:** 70
    * **Custo:** 99
    * **Tempo (s):** 0.1301
    * **Bateria Final (%):** 50.5%
    * **Status:** Completo
* **UCS:**
    * **Nós Expandidos:** 21541
    * **Passos:** 70
    * **Custo:** 99
    * **Tempo (s):** 0.1427
    * **Bateria Final (%):** 50.5%
    * **Status:** Completo
* **IDS:**
    * **Nós Expandidos:** 450215
    * **Passos:** 0
    * **Custo:** Infinito
    * **Status:** Sem rota

**Comentários:**
Neste cenário, com voo em altura elevada e vento moderado, A* e UCS completaram a missão com sucesso, utilizando a mesma trajetória. A* demonstrou ser ligeiramente mais rápido no planejamento. O IDS, mesmo com limite de profundidade (L=30), não encontrou uma rota viável.

**Visualização da Rota:**

![Rota Cenário 2 - A_UCS](Teste_002_v.gif)

---

## Cenário 3: Altura Baixa, Sem Vento (Sem Rota)

**Parâmetros:**
* **Destino:** 2
* **Altura de Voo:** Baixa
* **Potência:** Normal
* **Vento:** 0
* **Algoritmos Testados:** A*, UCS, IDS

**Resultados:**
* **Nós Expandidos (A*/UCS/IDS):** 0 / 0 / 0
* **Passos (A*/UCS/IDS):** 0 / 0 / 0
* **Custo (A*/UCS/IDS):** 0 / 0 / 0
* **Bateria (A*/UCS/IDS):** 0 / 0 / 0
* **Status:** Sem rota para todos os algoritmos.

**Comentários:**
Similar ao Cenário 1, a natureza do terreno e a restrição de voo baixo impediram a detecção de qualquer rota pelos algoritmos, indicando a necessidade de reavaliar a altura de voo.

---

## Cenário 4: Altura Alta, Sem Vento (Completo - A*/UCS)

**Parâmetros:**
* **Destino:** 2
* **Altura de Voo:** Alta
* **Potência:** Normal
* **Vento:** 0
* **Algoritmos Testados:** A*, UCS, IDS

**Resultados:**
* **A\*:**
    * **Nós Expandidos:** 100872
    * **Passos:** 122
    * **Custo:** 171
    * **Tempo (s):** 0.9299
    * **Bateria Final (%):** 171% (indicando recarga no destino)
    * **Status:** Completo
* **UCS:**
    * **Nós Expandidos:** 118963
    * **Passos:** 122
    * **Custo:** 171
    * **Tempo (s):** 1.0241
    * **Bateria Final (%):** 171% (indicando recarga no destino)
    * **Status:** Completo
* **IDS:**
    * **Nós Expandidos:** 1450429
    * **Passos:** 0
    * **Custo:** 0
    * **Status:** Sem rota

**Comentários:**
Ambos A* e UCS concluíram a missão com sucesso em altura alta e sem vento. O A* manteve sua vantagem em termos de nós expandidos e tempo de computação. A recarga no ponto de entrega foi crucial para a viabilidade da volta à base.

**Visualização da Rota:**

![Rota Cenário 4 - A_UCS](Testee_#004-v.gif)

---

## Cenário 5: Altura Baixa, Sem Vento (Sem Rota)

**Parâmetros:**
* **Destino:** 3
* **Altura de Voo:** Baixa
* **Potência:** Normal
* **Vento:** 0
* **Algoritmos Testados:** A*, UCS, IDS

**Resultados:**
* **Nós Expandidos (A*/UCS/IDS):** 0 / 0 / 0
* **Passos (A*/UCS/IDS):** 0 / 0 / 0
* **Custo (A*/UCS/IDS):** 0 / 0 / 0
* **Bateria (A*/UCS/IDS):** 0 / 0 / 0
* **Status:** Sem rota para todos os algoritmos.

**Comentários:**
Mais uma vez, o voo baixo neste tipo de região não permitiu a identificação de uma rota viável, reforçando a necessidade de ajustar a altura de voo para estas condições.

---

## Cenário 6: Altura Alta, Sem Vento (Completo - A*/UCS)

**Parâmetros:**
* **Destino:** 3
* **Altura de Voo:** Alta
* **Potência:** Normal
* **Vento:** 0
* **Algoritmos Testados:** A*, UCS, IDS

**Resultados:**
* **A\*:**
    * **Nós Expandidos:** 126053
    * **Passos:** 134
    * **Custo:** 189
    * **Tempo (s):** 1.2809
    * **Bateria Final (%):** 189% (indicando recarga no destino)
    * **Status:** Completa
* **UCS:**
    * **Nós Expandidos:** 162897
    * **Passos:** 134
    * **Custo:** 189
    * **Tempo (s):** 1.5382
    * **Bateria Final (%):** 189% (indicando recarga no destino)
    * **Status:** Completa
* **IDS:**
    * **Nós Expandidos:** 1450429
    * **Passos:** 0
    * **Custo:** 0
    * **Status:** Sem rota

**Comentários:**
A missão foi completada com sucesso por A* e UCS. O drone chegou ao ponto de entrega com 5.5% de bateria, e a etapa de carregamento explícito no destino foi crucial para permitir o retorno seguro à base. Para trajetórias ainda mais longas, estações intermediárias de carregamento seriam essenciais.

**Visualização da Rota:**

![Rota Cenário 6 - A_UCS](Teste_#006.gif)

---

## Cenário 7: Altura Baixa, Sem Vento (Sem Rota - Tempo Infinito)

**Parâmetros:**
* **Destino:** 4
* **Altura de Voo:** Baixa
* **Potência:** Normal
* **Vento:** 0
* **Algoritmos Testados:** A*, UCS, IDS

**Resultados:**
* **Nós Expandidos (A*/UCS/IDS):** 0 / 0 / 0
* **Passos (A*/UCS/IDS):** 0 / 0 / 0
* **Custo (A*/UCS/IDS):** Infinito / Infinito / 0
* **Bateria (A*/UCS/IDS):** 0 / 0 / 0
* **Status:** Sem rota para todos os algoritmos.
* **Comentários Adicionais:** Sem mapa.

**Comentários:**
Neste cenário, a busca para o destino 4 em altura baixa resultou em tempo de computação infinito para A* e UCS (ou seja, o programa travou ao expandir um número excessivo de nós sem encontrar caminho). Isso indica que não há um caminho viável sob estas condições, mesmo sem considerar a bateria.

---

## Cenário 8: Altura Baixa, Sem Vento (Completo - A*/UCS)

**Parâmetros:**
* **Destino:** 4
* **Altura de Voo:** Baixa
* **Potência:** Normal
* **Vento:** 0
* **Algoritmos Testados:** A*, UCS, IDS

**Resultados:**
* **A\*:**
    * **Nós Expandidos:** 83127
    * **Passos:** 106
    * **Custo:** 147
    * **Tempo (s):** 0.7732
    * **Bateria Final (%):** 147% (indicando recarga no destino)
    * **Status:** Completo
* **UCS:**
    * **Nós Expandidos:** 82345
    * **Passos:** 106
    * **Custo:** 147
    * **Tempo (s):** 0.9623
    * **Bateria Final (%):** 147% (indicando recarga no destino)
    * **Status:** Completo
* **IDS:**
    * **Nós Expandidos:** 1450429
    * **Passos:** 0
    * **Custo:** 0
    * **Status:** Sem rota

**Comentários:**
Neste caso, A* e UCS completaram a missão com sucesso em altura baixa e sem vento. Curiosamente, o UCS expandiu um número ligeiramente menor de nós que o A* pela primeira vez, mas o A* ainda manteve um tempo de computação mais rápido.

**Visualização da Rota:**

![Rota Cenário 8 - A_UCS](Teste_#008-v.gif)

---