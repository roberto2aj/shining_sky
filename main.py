import pygame
import numpy as np
import sys

# Configuracoes
TAMANHO_JANELA = (800, 600)
FPS = 30
QUANTIDADE_ESTRELAS = 100

def inicializar_estrelas():
    estrelas = []
    for _ in range(QUANTIDADE_ESTRELAS):
        x = np.random.randint(0, TAMANHO_JANELA[0])
        y = np.random.randint(0, TAMANHO_JANELA[1])
        estrelas.append((x, y))
    return estrelas

def atualizar_uma_estrela_aleatoria(estrelas):
    index = np.random.randint(0, QUANTIDADE_ESTRELAS-1)
    x = np.random.randint(0, TAMANHO_JANELA[0]-1)
    y = np.random.randint(0, TAMANHO_JANELA[1]-1)
    estrelas[index] = (x, y)

def main():
    pygame.init()
    tela = pygame.display.set_mode(TAMANHO_JANELA)
    pygame.display.set_caption("Shining Sky")
    clock = pygame.time.Clock()

    estrelas = inicializar_estrelas()
    rodando = True
    x = 0
    while rodando:
        x = (x + 1) % 4
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        tela.fill((0, 0, 0))
        if x == 0:
            atualizar_uma_estrela_aleatoria(estrelas)

        for estrela in estrelas:
            pygame.draw.circle(tela, (255, 255, 255), estrela, 1)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()