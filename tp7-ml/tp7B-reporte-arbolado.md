## Preprocesamiento 

### 1. Conversión de Variables Numéricas en Formato Texto

En el conjunto de datos se identificaron columnas con valores numéricos almacenados como texto, tales como altura y diametro_tronco. Estas variables contenían valores inconsistentes, con el uso de comas como separador decimal, rangos expresados mediante guiones (por ejemplo, “10-12”) y descripciones textuales (“Aprox. 8 m”).

Para homogeneizar estos datos, se aplicó un proceso de normalización que incluyó la sustitución de comas por puntos, la conversión de rangos en su valor promedio y la extracción del primer número en los casos donde el valor se encontraba acompañado por texto. El resultado fue la creación de nuevas columnas numéricas limpias (altura_num y diametro_tronco_num) que representaron de forma coherente estas magnitudes físicas.

### 2. Procesamiento de Fechas

La variable ultima_modificacion, que registraba la fecha de la última actualización del árbol, fue transformada al tipo de dato Date para permitir su manipulación temporal. A partir de esta columna se derivó una nueva variable denominada um_recency_days, calculada como la diferencia en días entre la fecha más reciente registrada y la fecha de modificación de cada árbol. Esta variable proporciona información temporal relativa que puede ser útil para captar patrones de actualización o mantenimiento en el arbolado urbano.

### 3. Creación de Interacciones Numéricas

Con el objetivo de enriquecer la representación del conjunto de datos, se generó una variable de interacción denominada alt_x_circ, resultante del producto entre la altura y la circunferencia del tronco (altura_num * circ_tronco_cm). Esta característica refleja una relación morfométrica relevante entre la dimensión vertical y el grosor del árbol, pudiendo ayudar al modelo a captar relaciones no lineales entre ambas medidas.

### 4. Codificación de Variables Categóricas

Las variables categóricas del conjunto de datos —principalmente especie, nombre_seccion y seccion— fueron convertidas a factores para permitir su uso por el algoritmo de LightGBM. Posteriormente, se codificaron como valores enteros consecutivos (0 a K-1), garantizando la coherencia entre los conjuntos de entrenamiento y prueba. Este proceso permitió que el modelo tratara las variables categóricas como tales, preservando la naturaleza discreta de cada categoría sin necesidad de aplicar codificaciones más costosas como one-hot encoding.

### 5. Manejo del Desbalance de Clases

El conjunto de entrenamiento presentaba un desbalance notable entre las clases objetivo, con una proporción aproximada de 7.94 árboles sin inclinación peligrosa por cada árbol con inclinación peligrosa. Para mitigar este efecto, se utilizó el parámetro scale_pos_weight del algoritmo LightGBM, ajustado al cociente entre las clases negativas y positivas. Este procedimiento otorgó un mayor peso a la clase minoritaria durante el entrenamiento, equilibrando su influencia en la función de pérdida y mejorando la capacidad del modelo para identificar árboles con inclinación peligrosa.

## Resultados obtenidos sobre el conjunto de validación

Cuando se testeo sobre el conjunto de validación, se obtuvo un resultado del 0.77981

## Resultados obtenidos en Kaggle 

Al momento de realizar la predicción en el desafio en Kaggle, se llegó a un resultado de 0.69605, habiéndonos encontrado con una merma del rendimiento, lo cual puede deberse a que el conjunto utilizado por la competencia es un poco distinto que con el que se entrenó.

## Descripción del algoritmo 

Para conseguir el objetivo se optó por utilizar el algoritmo LightGBM, el cuál es un algoritmo de aprendizaje automático basado en árboles de decisión, diseñado para predecir resultados a partir de datos tabulares (como los registros del arbolado urbano). Su principal objetivo es combinar muchos árboles simples para formar un modelo potente y preciso, capaz de reconocer patrones complejos en los datos.

El modelo no se entrena de una sola vez, sino que se construye en etapas.
En cada etapa, el algoritmo crea un árbol de decisión nuevo que trata de corregir los errores de los árboles anteriores. A medida que se agregan más árboles, el modelo mejora su capacidad para distinguir entre los casos correctos e incorrectos.

Cada árbol por sí solo es un modelo sencillo, pero la combinación de muchos árboles —cada uno aprendiendo de los errores del anterior— da lugar a un modelo final muy preciso.
