# Doom Fire (Pygame)

<p align="center">
  <img src="fogo_doom_real.gif" alt="Doom fire demo" width="700">
</p>

Este repositorio é um estudo do efeito de fogo estilo Doom usando uma tabela de cores (paleta) e uma simulacao discreta de calor. A implementacao foi feita como exercicio de aprendizagem: primeiro entendendo a "fisica" simplificada do fogo, depois adicionando dissipacao e, por fim, o vento.

## Como rodar

Requisitos:
- Python 3
- pygame
- numpy

Execucao:
```
python fire.py
```

## Controles

- Fechar a janela: encerra o programa
- Tecla R: limpa o fogo (reinicia a tela)

## Estrutura do projeto

| Arquivo | Funcao |
| --- | --- |
| `fire.py` | Implementa o grid de calor, paleta e renderizacao |
| `vectorizedvolumetricfire.py` | Versão vetorizada usando broadcasting NumPy avançado |
| `TECHNICAL_DEEP_DIVE.md` | Análise técnica detalhada sobre vetorização e otimização |

## Como funciona: A Lógica Matricial

O segredo deste algoritmo é que não existe uma simulação física de partículas ou fluidos complexos. O "fogo" é apenas uma visualização gráfica de uma matriz de números inteiros sendo atualizada constantemente.

### 1. A Paleta (Termodinâmica dos Índices)

Imagine o fogo como uma planilha onde cada célula possui um valor entre **0 e 36**. Este valor representa a temperatura, que é mapeada para uma cor específica no momento da renderização:

| Índice (Temperatura) | Cor Visual (RGB Aproximado) | Estado Simulado |
| :---: | :--- | :--- |
| **36** | Branco `(255, 255, 255)` | Fonte de calor infinita (Base) |
| **20 a 35** | Amarelo / Laranja | Combustão ativa (Corpo da chama) |
| **1 a 19** | Vermelho / Marrom | Resfriamento e dissipação |
| **0** | Preto `(0, 0, 0)` | Frio / Vazio (Topo da tela) |

### 2. A Matemática da Propagação

A cada quadro (frame), o algoritmo percorre a matriz e define o valor de um pixel baseado no pixel **diretamente abaixo dele**. A lógica de propagação segue a fórmula:

`Pixel_Atual = Pixel_Abaixo - Decaimento_Aleatório`

Isso garante que o calor suba, mas perca intensidade (esfrie) aleatoriamente conforme ganha altura.

| Posição (Origem) | Valor Original | Fator Aleatório (Decay) | Cálculo | Novo Valor (Destino) |
| :---: | :---: | :---: | :--- | :---: |
| Abaixo | 36 (Branco) | 0 | `36 - 0` | **36** (Mantém calor) |
| Abaixo | 36 (Branco) | 2 | `36 - 2` | **34** (Esfria levemente) |
| Abaixo | 20 (Laranja) | 3 | `20 - 3` | **17** (Esfria rápido) |
| Abaixo | 2 (Vermelho) | 2 | `2 - 2` | **0** (Apaga) |

### 3. Vento e Turbulência

O efeito de vento não é físico, mas uma manipulação de matriz. Após calcular a temperatura, o código desloca horizontalmente os valores da matriz.

* **Vento Constante:** Desloca toda a matriz para a esquerda (`np.roll` com valor -1).
* **Turbulência:** Aplica deslocamentos aleatórios em linhas específicas para criar a sensação de caos e movimento orgânico.

### 4. Ajuste de Parâmetros

O comportamento visual do fogo é controlado por constantes no código:

| Variável | Efeito ao aumentar | Efeito ao diminuir |
| --- | --- | --- |
| **LARGURA_FOGO** | Maior resolução horizontal (fogo HD). | Visual mais pixelado ("blocadão"/retrô). |
| **ALTURA_FOGO** | Permite que a chama suba mais antes de ser cortada. | O fogo é cortado abruptamente no topo. |
| **Fator de Decay** | O fogo fica baixo e apaga rápido. | O fogo sobe até o topo da tela (efeito pilar). |

### Etapa 1: grade e fonte

| Conceito | Implementacao |
| --- | --- |
| Grid | Matriz `ALTURA_FOGO x LARGURA_FOGO` |
| Fonte | Ultima linha recebe o valor maximo da paleta |

### Etapa 2: decaimento (resfriamento)

| Conceito | Implementacao |
| --- | --- |
| Decaimento | Valor aleatorio de 0 a 2 por celula |
| Efeito | Reduz o calor enquanto ele sobe |

O decaimento pequeno ja e suficiente para criar movimento, porque o ruido muda a cada frame.

### Etapa 3: vento

O vento e apenas um deslocamento horizontal do grid. Isso puxa as chamas para um lado e cria uma direcao perceptivel.

| Tipo | Implementacao |
| --- | --- |
| Vento constante | `np.roll(..., -1, axis=1)` |
| Turbulencia | Deslocamento aleatorio por linha |

## Fluxo do frame (resumo)

| Passo | O que acontece |
| --- | --- |
| 1 | Gera decaimento aleatorio |
| 2 | Calcula novo calor a partir da linha de baixo |
| 3 | Aplica vento constante e turbulencia |
| 4 | Converte indices em RGB com a paleta |
| 5 | Escala e desenha na janela |

## Observacoes

- A paleta define o "estilo" do fogo; trocar a paleta muda a aparencia inteira.
- O tamanho do grid define o detalhe. O tamanho da janela apenas escala o resultado.

---

## 📚 Deep Dive Técnico: Vetorização com NumPy

Após a publicação inicial deste projeto, recebi uma pergunta técnica do engenheiro [@victorvalentee](https://github.com/victorvalentee) durante uma discussão sobre otimização:

> **"Como simular os 3 segundos de fogo sem usar loops?"**

Essa pergunta me levou a um estudo aprofundado sobre **broadcasting multidimensional**, **álgebra vetorial** e **trade-offs entre paralelização espacial vs. temporal** em algoritmos com dependência causal.

### Resultado do Estudo

Criei uma implementação vetorizada (`vectorizedvolumetricfire.py`) que:

- **Elimina loops espaciais** (100×100 pixels) usando operações vetoriais NumPy
- **Reduz complexidade** de O(T×H×W) loops Python para O(T) iterações com operações vetorizadas em C
- **Ganho de performance**: ~100× mais rápido na geração dos frames
- **Limitação identificada**: O loop temporal permanece devido à natureza de recorrência da propagação de calor

### Documentação Técnica Completa

Para detalhes sobre a implementação, conceitos de broadcasting avançado, benchmarks e discussão sobre limitações teóricas, veja:

**📖 [TECHNICAL_DEEP_DIVE.md](TECHNICAL_DEEP_DIVE.md)**

Este documento inclui:
- Análise matemática da vetorização (Big-O)
- Comparação entre abordagens (loops vs. broadcasting)
- Conceitos avançados de NumPy demonstrados
- Trade-offs arquiteturais (memória vs. computação)
- Discussão sobre paralelização em GPU
- Por que o loop temporal é inevitável (dependência causal)
