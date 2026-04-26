# Snake en Python

Version actual: `1.2.0`

Un juego de Snake hecho con `tkinter`, sin instalar paquetes extra.

## Como jugar

Ejecuta:

```bash
python snake.py
```

Controles:

- 1, 2 o 3: elegir nivel al iniciar
- Flechas del teclado o WASD: mover la serpiente
- Espacio: pausar o continuar
- R: reiniciar
- L: volver al menu de niveles

## Cosas interesantes

- Nivel 1, Clasico: comida, obstaculos y bombas suaves
- Nivel 2, Persecucion: un fantasmita lento te sigue
- Nivel 3, Caos: dos fantasmitas mas activos y bombas con menos tiempo
- Comida roja: suma 1 punto
- Comida dorada: aparece por tiempo limitado y suma 3 puntos
- Obstaculos: van apareciendo conforme subes tu puntuacion
- Bombitas: aparecen de pronto cinco casillas adelante; cambia de camino o explotas
- Niveles: la velocidad sube cada pocos puntos
- Record: se guarda en `high_score.json`

Come, esquiva los obstaculos y busca superar tu record.

## GitHub

Para guardar cambios en Git:

```bash
git add snake.py README.md CHANGELOG.md .gitignore
git commit -m "Agregar niveles y fantasmitas"
```

Para subirlos a GitHub:

```bash
git push
```
