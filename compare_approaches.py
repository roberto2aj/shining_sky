import numpy as np
import time
import imageio
from fire import atualizar_fogo_deschamps
from decay_abstraction import gerar_fogo_matriz_decaimento

# Configurações
LARGURA, ALTURA = 100, 100
TOTAL_FRAMES = 90
FPS = 30
PALETA = np.array([
    (7, 7, 7), (31, 7, 7), (47, 15, 7), (71, 15, 7), (87, 23, 7), (103, 31, 7), (119, 31, 7), (143, 39, 7),
    (159, 47, 7), (175, 63, 7), (191, 71, 7), (199, 71, 7), (223, 79, 7), (223, 87, 7), (223, 87, 7), (215, 95, 7),
    (215, 95, 7), (215, 103, 15), (207, 111, 15), (207, 119, 15), (207, 127, 15), (207, 135, 23), (199, 135, 23), (199, 143, 23),
    (199, 151, 31), (191, 159, 31), (191, 159, 31), (191, 167, 39), (191, 167, 39), (191, 175, 47), (183, 175, 47), (183, 183, 47),
    (183, 183, 55), (207, 207, 111), (223, 223, 159), (239, 239, 199), (255, 255, 255), (255, 255, 255)
], dtype=np.uint8)

def gerar_fogo_original_loop():
    fogo_grid = np.zeros((ALTURA, LARGURA), dtype=np.int32)
    fogo_grid[-1, :] = 36
    
    frames = []
    # Warmup
    for _ in range(50):
        fogo_grid = atualizar_fogo_deschamps(fogo_grid)
        
    start_time = time.time()
    for _ in range(TOTAL_FRAMES):
        fogo_grid = atualizar_fogo_deschamps(fogo_grid)
        frames.append(fogo_grid.copy())
    end_time = time.time()
    
    return np.array(frames), end_time - start_time

def main():
    print("=== Comparativo de Performance ===")
    
    # 1. Original
    print("\nExecutando Algoritmo Original (Deschamps)...")
    frames_orig, tempo_orig = gerar_fogo_original_loop()
    print(f"Tempo Original: {tempo_orig*1000:.2f}ms")
    
    # 2. Decay Matrix
    print("\nExecutando Novo Algoritmo (Decay Matrix)...")
    start_time = time.time()
    frames_new = gerar_fogo_matriz_decaimento()
    end_time = time.time()
    tempo_new = end_time - start_time
    print(f"Tempo Decay Matrix: {tempo_new*1000:.2f}ms")
    
    print(f"\nSpeedup: {tempo_orig / tempo_new:.1f}x")
    
    # 3. Gerar GIF Comparativo
    print("\nGerando GIF Comparativo...")
    combined_frames = []
    
    # Adicionar legendas (simplesmente desenhando pixels brancos na borda ou separador)
    border = np.zeros((TOTAL_FRAMES, ALTURA, 10), dtype=np.int32) # Faixa preta separadora
    
    for i in range(TOTAL_FRAMES):
        f1 = frames_orig[i]
        f2 = frames_new[i]
        
        # Concatenar lado a lado
        combined = np.hstack([f1, np.zeros((ALTURA, 10), dtype=np.int32), f2])
        
        # Colorir
        rgb = PALETA[combined]
        combined_frames.append(rgb)
        
    imageio.mimsave('comparison.gif', combined_frames, fps=FPS, loop=0)
    print("Salvo: comparison.gif")
    print("Esquerda: Original | Direita: Decay Matrix")

if __name__ == "__main__":
    main()
