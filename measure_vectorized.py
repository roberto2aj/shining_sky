import time
from vectorizedvolumetricfire import gerar_fogo_vetorizado

start = time.time()
fogo = gerar_fogo_vetorizado()
end = time.time()
print(f'Tempo vetorizado: {(end - start)*1000:.2f}ms')