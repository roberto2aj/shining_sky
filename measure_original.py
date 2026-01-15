import time
import numpy as np
from fire import atualizar_fogo_deschamps

# Configurações
LARGURA_FOGO = 100
ALTURA_FOGO = 100

fogo_grid = np.zeros((ALTURA_FOGO, LARGURA_FOGO), dtype=np.int32)
fogo_grid[-1, :] = 36

start = time.time()
for _ in range(90):
    fogo_grid = atualizar_fogo_deschamps(fogo_grid)
end = time.time()
print(f'Tempo original: {(end - start)*1000:.2f}ms')