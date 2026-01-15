import sys
import pygame
import imageio
import numpy as np

# Configurações
LARGURA, ALTURA = 100, 100
TAMANHO_JANELA = (800, 600)
FPS = 30
TOTAL_FRAMES = 90

# Paleta do Doom
CORES = [
    (7, 7, 7), (31, 7, 7), (47, 15, 7), (71, 15, 7), (87, 23, 7), (103, 31, 7), (119, 31, 7), (143, 39, 7),
    (159, 47, 7), (175, 63, 7), (191, 71, 7), (199, 71, 7), (223, 79, 7), (223, 87, 7), (223, 87, 7), (215, 95, 7),
    (215, 95, 7), (215, 103, 15), (207, 111, 15), (207, 119, 15), (207, 127, 15), (207, 135, 23), (199, 135, 23), (199, 143, 23),
    (199, 151, 31), (191, 159, 31), (191, 159, 31), (191, 167, 39), (191, 167, 39), (191, 175, 47), (183, 175, 47), (183, 183, 47),
    (183, 183, 55), (207, 207, 111), (223, 223, 159), (239, 239, 199), (255, 255, 255)
]
PALETA = np.array(CORES + [(255, 255, 255)], dtype=np.uint8)

def gerar_fogo_matriz_decaimento():
    """
    Gera o fogo usando a técnica de Matriz de Decaimento (Decay Matrix).
    Não há loops temporais explícitos simulando propagação frame-a-frame.
    Em vez disso, calculamos a 'história de vida' de todas as partículas possíveis
    e as mapeamos para o espaço-tempo (T, Y, X).
    """
    
    # Parâmetros
    BASE_HEAT = 36
    
    # Precisamos de 'partículas' suficientes para cobrir o tempo de warmup + animação
    # Uma partícula nascida em T precisa viver ALTURA frames.
    # Precisamos de streams nascendo desde T = -ALTURA até T = TOTAL_FRAMES
    NUM_STREAMS = TOTAL_FRAMES + ALTURA + 10 # +10 margem
    
    # 1. Gerar Matriz de Decaimento Global (Streams de Vida)
    # Shape: (Num_Streams, Max_Age, Largura)
    # Cada coluna representa a vida de uma partícula se movendo para cima
    decay_raw = np.random.randint(0, 3, (NUM_STREAMS, ALTURA, LARGURA))
    
    # 2. Calcular Integral de Decaimento (Cumulative Sum)
    # Heat(age) = Base - Sum(decays_until_age)
    decay_cum = np.cumsum(decay_raw, axis=1)
    
    # Streams pré-calculados de calor. 
    # streams[u, age, x] é o calor da partícula nascida no tempo u, na idade age, coluna x
    streams = np.maximum(0, BASE_HEAT - decay_cum)
    
    # 3. Mapear Streams para o Cubo (T, Y, X) usando broadcasting
    
    # Criar grid de coordenadas para o Cubo Final (TOTAL_FRAMES, ALTURA, LARGURA)
    # T: 0..89
    # Y: 0..99 (Onde 0 é topo, 99 é base)
    # X: 0..99
    
    # Definindo a relação: 
    # Uma célula em (t, y) contém a partícula que tem Age = (ALTURA - 1 - y)
    # E que nasceu em u = t - Age + (offset de warmup)
    
    t_indices = np.arange(TOTAL_FRAMES).reshape(-1, 1, 1) # (T, 1, 1)
    y_indices = np.arange(ALTURA).reshape(1, -1, 1)      # (1, H, 1)
    x_indices = np.arange(LARGURA).reshape(1, 1, -1)     # (1, 1, W)
    
    # Calcular a idade da partícula em cada posição Y
    # Na base (y=99), age=0. No topo (y=0), age=99.
    age_grid = (ALTURA - 1) - y_indices
    
    # Calcular qual stream usar
    # Para movimento para CIMA: stream_idx deve ser constante ao longo de y = -t + c
    # Ou seja, S(t, y) == S(t+1, y-1).
    # (t) + (y) = (t+1) + (y-1).
    stream_idx_grid = t_indices + y_indices 
    
    # Garantir limites
    stream_idx_grid = np.clip(stream_idx_grid, 0, NUM_STREAMS - 1)
    
    # Sampling vetorizado direto dos streams!
    # O broadcasting do numpy faz a mágica aqui.
    # streams[ (T,H,1), (1,H,1), (1,1,W) ] -> Result (T, H, W)
    # Nota: Precisamos expandir x_indices para bater com as dimensões se quisermos variar por X
    # streams tem shape (S, H, W). Queremos indexar S e H, mantendo W alinhado ou indexado.
    # O jeito mais fácil é deixar o numpy fazer o broadcast do X automaticamente se as primeiras dims baterem.
    # Mas stream_idx_grid é (T, H, 1). age_grid é (1, H, 1).
    # Vamos usar take_along_axis ou indexação direta.
    
    # Indexação direta:
    # streams[S_idx, A_idx, :]
    # S_idx é (T, H). A_idx é (H).
    # Queremos output (T, H, W).
    
    # Expandindo indices para (T, H)
    # Removemos a dimensão extra (W=1) para ter matrizes (T, H)
    S = stream_idx_grid.squeeze(axis=-1)
    A = age_grid.squeeze(axis=-1)
    
    # A indexação streams[S, A] retorna (T, H, W)
    fogo_cubo = streams[S, A]
    
    # 4. Aplicar Vento
    # O vento faz as linhas de cima se moverem para a esquerda em relação às de baixo.
    # Shift cumulativo: shift(y) = k * age
    # Usaremos broadcasting para "rolar" cada linha independentemente
    
    rows, cols = np.ogrid[:ALTURA, :LARGURA]
    # Shift aumenta com a altura (quanto menor o y, maior o shift)
    # y=99 (base) -> shift 0. y=0 (topo) -> shift ~30?
    wind_strength = 0.5
    shifts = ((ALTURA - 1 - rows) * wind_strength).astype(int)
    
    # Aplicar shift para todas as colunas
    # Somando o shift para mover para a esquerda (agora que o movimento vertical é para cima)
    # Movimento UP + Shape '\' (gerado por +shift) = Movimento UP-LEFT
    new_cols = (cols + shifts) % LARGURA
    
    # Aplicar essa transformação de coordenadas para todos os frames
    # Como o shift é estático (apenas função de Y), podemos aplicar no cubo todo
    # fogo_cubo é (T, Y, X). Queremos reordenar o eixo X baseando-se em Y.
    
    # Precisamos broadcast dos índices para (T, Y, X)
    final_cols = np.broadcast_to(new_cols, (TOTAL_FRAMES, ALTURA, LARGURA))
    
    # Usar np.take_along_axis é uma opção, ou fancy indexing
    # Para fancy indexing em 3D: cube[t, y, new_cols]
    # Precisamos que t e y sejam broadcasts compatíveis
    T_idx = np.arange(TOTAL_FRAMES).reshape(-1, 1, 1)
    Y_idx = np.arange(ALTURA).reshape(1, -1, 1)
    
    fogo_com_vento = fogo_cubo[T_idx, Y_idx, final_cols]
    
    return fogo_com_vento

def main():
    pygame.init()
    tela = pygame.display.set_mode(TAMANHO_JANELA)
    pygame.display.set_caption("Modelo de Fogo (Matriz Decaimento) - Victor Valente")
    clock = pygame.time.Clock()
    
    # Geração
    import time
    start = time.time()
    fogo_completo = gerar_fogo_matriz_decaimento()
    end = time.time()
    print(f"Tempo de Geração (Decay Matrix): {(end-start)*1000:.2f}ms")
    print(f"Shape: {fogo_completo.shape}")
    
    # Loop de visualização
    frames_gif = []
    frame_idx = 0
    rodando = True
    
    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
        
        fogo_grid = fogo_completo[frame_idx]
        rgb_array = PALETA[fogo_grid]
        
        if len(frames_gif) < TOTAL_FRAMES:
            frames_gif.append(rgb_array.copy())
        elif len(frames_gif) == TOTAL_FRAMES:
            print("Salvando GIF...")
            imageio.mimsave('fogo_decay_matrix.gif', frames_gif, fps=FPS, loop=0)
            print("Salvo: fogo_decay_matrix.gif")
            frames_gif.append(None)
        
        surface_array = np.swapaxes(rgb_array, 0, 1)
        surf = pygame.surfarray.make_surface(surface_array)
        pygame.transform.scale(surf, TAMANHO_JANELA, tela)
        
        pygame.display.flip()
        frame_idx = (frame_idx + 1) % TOTAL_FRAMES
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
