import pygame
import numpy as np
import sys
import imageio

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

def gerar_fogo_vetorizado():
    # Cubo 3D: cada "camada" é um frame no tempo
    fogo_cubo = np.zeros((TOTAL_FRAMES, ALTURA, LARGURA), dtype=np.int32)
    fogo_cubo[:, -1, :] = 36  # Base sempre quente
    
    # Pré-gera todos os valores aleatórios de uma vez
    decay_tensor = np.random.randint(0, 3, (TOTAL_FRAMES, ALTURA, LARGURA))
    shifts_horizontal = np.random.randint(-1, 2, (TOTAL_FRAMES, ALTURA))
    
    for t in range(1, TOTAL_FRAMES):
        frame_anterior = fogo_cubo[t-1].copy()
        
        # Propagação vertical com decay
        calor_propagado = np.maximum(0, frame_anterior[1:, :] - decay_tensor[t, 1:, :])
        frame_anterior[:-1, :] = calor_propagado
        
        # Vento constante
        frame_anterior[:-1, :] = np.roll(frame_anterior[:-1, :], -1, axis=1)
        
        # Turbulência horizontal
        for y in range(ALTURA - 1):
            frame_anterior[y, :] = np.roll(frame_anterior[y, :], shifts_horizontal[t, y])
        
        frame_anterior[-1, :] = 36
        fogo_cubo[t] = frame_anterior
    
    return fogo_cubo

def main():
    pygame.init()
    tela = pygame.display.set_mode(TAMANHO_JANELA)
    pygame.display.set_caption("Vectorized Volumetric Fire - Elen Camila Sales")
    clock = pygame.time.Clock()
    
    print("Gerando fogo vetorizado...")
    fogo_completo = gerar_fogo_vetorizado()
    print(f"Pronto. Shape: {fogo_completo.shape}")
    
    frames_gif = []
    frame_idx = 0
    rodando = True
    
    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                frame_idx = 0
        
        fogo_grid = fogo_completo[frame_idx]
        rgb_array = PALETA[fogo_grid]
        
        if len(frames_gif) < TOTAL_FRAMES:
            frames_gif.append(rgb_array.copy())
        elif len(frames_gif) == TOTAL_FRAMES:
            print("Salvando GIF...")
            imageio.mimsave('fogo_vetorizado.gif', frames_gif, fps=FPS, loop=0)
            print("Salvo: fogo_vetorizado.gif")
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