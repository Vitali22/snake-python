# Snake en Python

Version actual: `1.1.0`

Un juego de Snake hecho con `tkinter`, sin instalar paquetes extra.

## Como jugar

Ejecuta:

```bash
python snake.py
```

Controles:

- Flechas del teclado o WASD: mover la serpiente
- Espacio: pausar o continuar
- R: reiniciar

## Cosas interesantes

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
git commit -m "Agregar bombas y version del juego"
```

Para subirlos a GitHub:

```bash
git push
```
