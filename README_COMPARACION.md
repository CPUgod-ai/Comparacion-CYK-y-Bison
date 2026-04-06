# Taller — Comparativa de Rendimiento: Bison LALR vs CYK

## Introduccion

En este taller se comparan dos algoritmos de analisis sintactico: **Bison LALR** y **CYK**. El objetivo es demostrar de forma practica y visual la diferencia de rendimiento entre un parser eficiente O(n) y uno general O(n³), usando expresiones aritmeticas de longitud creciente como entrada.

Para esto se usa un parser construido con **Bison + Flex** compilado en C, y una implementacion del algoritmo **CYK** escrita en Python. Un script comparador mide el tiempo de ejecucion de ambos y genera graficas automaticamente.

---

## Estructura del proyecto

Todos los archivos tienen que estar en la misma carpeta. Si no estan juntos el programa no va a encontrar el ejecutable `bison_parser` y va a fallar.

```
COMPARACION/
├── lexer.l              <- reglas del lexer escrito en Flex
├── parser.y             <- gramatica y parser escrito en Bison
├── lex.yy.c             <- generado automaticamente por Flex, no se edita
├── parser.tab.c         <- generado automaticamente por Bison, no se edita
├── parser.tab.h         <- generado automaticamente por Bison, no se edita
├── bison_parser         <- ejecutable compilado con gcc, lo crea el paso 4
├── comparador.py        <- script principal que mide tiempos y genera graficas
├── input.txt            <- expresiones de prueba generadas automaticamente
├── grafica_rendimiento.png   <- grafica de tiempo generada al correr comparador.py
├── comparativa_memoria.png   <- grafica de memoria generada al correr comparador.py
└── grafica_final.png         <- grafica combinada generada al correr comparador.py
```

> `comparador.py` llama a `./bison_parser` con `subprocess`, por eso el ejecutable tiene que estar en la misma carpeta. Si se mueve o no se compila primero, va a aparecer un error de archivo no encontrado.

---

## Requisitos

Abrir la terminal y instalar todo lo necesario:

```bash
sudo apt install -y flex bison gcc
pip3 install matplotlib psutil
```

---

## Como ejecutarlo

### Paso 1 — Ir a la carpeta del proyecto

```bash
cd ~/Documents/COMPARACION
```

### Paso 2 — Generar los archivos de Bison y Flex

```bash
bison -d parser.y
flex lexer.l
```

Esto genera `lex.yy.c`, `parser.tab.c` y `parser.tab.h` automaticamente.

### Paso 3 — Compilar el ejecutable

```bash
gcc lex.yy.c parser.tab.c -o bison_parser
```

Verificar que se creo:

```bash
ls
```

Tiene que aparecer `bison_parser` en la lista.

### Paso 4 — Correr el comparador

```bash
python3 comparador.py
```

> **Advertencia:** CYK es O(n³). Con los tamaños grandes el programa puede tardar varios minutos. Si se quiere cancelar se usa `Ctrl + C`.

---

## Que hace cada archivo

### `lexer.l`
Define las reglas del analizador lexico usando Flex. Reconoce numeros, operadores `+ - * /` y parentesis, e ignora los espacios. Flex lo compila automaticamente a `lex.yy.c`.

### `parser.y`
Define la gramatica de expresiones aritmeticas usando Bison con las reglas `E`, `T` y `F`. Ademas contiene el `main()` que mide el tiempo con `clock_gettime` e imprime el resultado en milisegundos. Bison lo compila a `parser.tab.c`.

### `bison_parser`
Ejecutable compilado en C. Recibe una expresion por `stdin`, la analiza con el parser LALR e imprime el tiempo que tardo en milisegundos. `comparador.py` lo llama con `subprocess` por cada expresion de prueba.

### `comparador.py`
Script principal del taller. Construye expresiones de longitud creciente, llama a `bison_parser` para medirlo, corre el algoritmo CYK en Python para medirlo, imprime dos tablas en consola y genera las 3 graficas PNG.

---

## Gramatica utilizada

La misma gramatica del taller anterior escrita en BNF:

```
E  →  E opsuma T  |  T
T  →  T opmul F   |  F
F  →  num  |  ( E )

opsuma  →  +  |  -
opmul   →  *  |  /
```

Para CYK la gramatica se convirtio a **Forma Normal de Chomsky (CNF)** porque CYK solo acepta reglas binarias:

```
E  →  E P  |  num
P  →  A E
A  →  +
```

---

## Salida en consola

Al correr `comparador.py` aparecen dos tablas:

```
LONGITUD        BISON (ms)      CYK (ms)
---------------------------------------------
77              0.0458          38.1749
397             0.1012          5387.1158
1197            0.1190          153724.3285

TOKENS          BISON (ms)      RAM B (MB)   CYK (ms)      RAM C (MB)
---------------------------------------------------------------
77              0.0458          0.00         38.8456        0.00
397             0.1012          0.00         5510.3618      0.00
1197            0.1190          0.00         166213.4151    1.84
```

---

## Resultados visuales

### Grafica de rendimiento

Muestra la diferencia de tiempo en escala logaritmica. La curva roja de CYK sube disparada mientras la azul de Bison se mantiene casi plana.

*(insertar grafica_rendimiento.png aqui)*

---

### Grafica de memoria

Muestra el uso de RAM de cada algoritmo segun la cantidad de tokens.

*(insertar comparativa_memoria.png aqui)*

---

### Grafica final combinada

Las dos metricas juntas en un solo panel — tiempo a la izquierda y memoria a la derecha.

*(insertar grafica_final.png aqui)*

---

## Analisis

Los resultados confirman la diferencia teorica entre los dos algoritmos. Bison con LALR procesa cada token exactamente una vez de izquierda a derecha, lo que lo mantiene en O(n) sin importar que tan larga sea la expresion. Con 1197 tokens tardo apenas 0.11ms.

CYK en cambio usa una tabla de programacion dinamica con tres loops anidados. Cada vez que los tokens se triplican, el tiempo se multiplica por 27 (que es 3³). Con 77 tokens tardo 38ms, con 397 tardo 5 segundos, y con 1197 tardo casi 2.5 minutos — exactamente la curva cubica que predice la teoria.

La diferencia no es de implementacion sino de complejidad algoritmica. Bison esta disenado especificamente para gramaticas libres de contexto deterministas y por eso es tan eficiente. CYK es un algoritmo general que acepta cualquier gramatica libre de contexto pero paga ese precio en rendimiento.

**Sobre la medicion de memoria RAM:**

La tabla muestra 0.00 MB en la mayoria de casos porque `psutil` mide la **diferencia** de RAM antes y despues de cada operacion, no la RAM total. Bison corre como proceso externo en C y Python no tiene acceso directo a su memoria desde `subprocess`. CYK corre dentro del mismo proceso de Python, pero Python reserva memoria por bloques grandes desde el inicio y la reutiliza internamente, entonces la diferencia que detecta `psutil` es cero. Solo cuando la tabla de CYK es tan grande que Python necesita pedirle memoria nueva al sistema operativo aparece un valor distinto de cero, como el 1.84 MB del ultimo caso con 1197 tokens.

Para ver la RAM real que consume el programa mientras corre se puede abrir `htop` en otra terminal con:

```bash
htop
```

Ahi se puede ver el proceso `python3 comparador.py` usando hasta el **100% de un nucleo** y varios cientos de MB de RAM real mientras CYK esta procesando. Esa es la memoria verdadera que `psutil` no logra capturar porque lo mide de forma indirecta.

---

## Conclusion

Este taller demostro de forma practica por que los compiladores reales usan parsers LALR y no algoritmos generales como CYK. La diferencia entre O(n) y O(n³) no es solo teorica — con entradas medianas ya se vuelve inutilizable en tiempo real.

Lo mas interesante es que ambos analizan exactamente la misma gramatica y llegan al mismo resultado, pero la forma en que lo hacen internamente produce una diferencia de rendimiento de varios ordenes de magnitud.

---

## Librerias y herramientas usadas

- [`flex`](https://github.com/westes/flex) — generador de lexers
- [`bison`](https://www.gnu.org/software/bison/) — generador de parsers LALR
- [`gcc`](https://gcc.gnu.org/) — compilador de C
- [`matplotlib`](https://matplotlib.org/) — graficas
- [`psutil`](https://psutil.readthedocs.io/) — medicion de memoria
