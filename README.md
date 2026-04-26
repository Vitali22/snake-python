# Snake en Python

Version actual: `1.6.0`

Juego de Snake hecho con `tkinter`, sin instalar paquetes extra.

## Ejecutar

```bash
python snake.py
```

## Controles

- `1`, `2` o `3`: elegir nivel al iniciar
- Flechas del teclado o WASD: mover la serpiente
- Espacio: pausar o continuar
- `R`: reiniciar
- `L`: volver al menu de niveles
- `M`: silenciar o activar sonidos

## Niveles

- Nivel 1, Clasico: comida, obstaculos, bombas suaves y jefes.
- Nivel 2, Persecucion: agrega un fantasmita lento que te sigue.
- Nivel 3, Caos: agrega mas fantasmitas, bombas con menos tiempo y jefes mas tensos.

## Comida y crecimiento

- Comida roja: suma 1 punto.
- Comida dorada: aparece por tiempo limitado y suma 3 puntos.
- Mientras mas comes, mas larga se vuelve la serpiente.
- Ser mas grande tambien puede ayudarte: los fantasmitas que chocan contra el cuerpo explotan y te dan una vida.

## Vidas y escudo

- Empiezas con 3 vidas.
- Si un fantasmita choca contra el cuerpo de la serpiente, explota y ganas 1 vida.
- Si un fantasmita toca la cabeza, pierdes una vida.
- El escudo azul te protege por unos segundos de fantasmas, bombas y jefes.
- Cuando ganas una vida por un fantasmita, aparece una senal morada delante de la cabeza.

## Bombas

- Las bombas aparecen de pronto cinco casillas adelante.
- Si no cambias de camino y no tienes escudo, pierdes una vida.

## Jefes

- Los jefes aparecen en todos los niveles a los 20, 30 y 40 segundos.
- El marcador muestra cuanto falta para el proximo jefe.
- El jefe aparece rojo al principio: si lo tocas, pierdes una vida.
- Al final de su aparicion, el jefe se vuelve verde.
- Cuando el jefe esta verde, la serpiente se lo puede comer.
- Comer al jefe verde muestra una recompensa visual `+5`.
- Si te comes al jefe de los 40 segundos, ganas la partida.

## Records

- Cada nivel tiene su propio record.
- Los records se guardan en `high_score.json`.

## Creditos

- Reglas creadas por Emilio Vitali Padilla Socconini.
