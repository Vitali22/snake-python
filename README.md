# Snake en Python

Version actual: `1.4.0`

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
- Nivel 3, Caos: dos fantasmitas, bombas con menos tiempo y jefes a los 20, 30 y 40 segundos
- Si sobrevives al jefe de los 40 segundos en nivel 3, ganas
- Escudo azul: te protege por unos segundos de bombas, fantasmas y jefes
- Los fantasmitas explotan si chocan contra el cuerpo de la serpiente, te dan una vida, pero te atrapan si llegan a la cabeza
- Comida roja: suma 1 punto
- Comida dorada: aparece por tiempo limitado y suma 3 puntos
- Obstaculos: van apareciendo conforme subes tu puntuacion
- Bombitas: aparecen de pronto cinco casillas adelante; cambia de camino o explotas
- Vidas: empiezas con 3 y puedes ganar mas
- Records por nivel: se guardan en `high_score.json`

Come, esquiva los obstaculos y busca superar tu record.

## GitHub

Para guardar cambios en Git:

```bash
git add snake.py README.md CHANGELOG.md .gitignore
git commit -m "Agregar escudo vidas sonidos y jefe"
```

Para subirlos a GitHub:

```bash
git push
```
