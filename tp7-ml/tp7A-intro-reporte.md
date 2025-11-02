# Trabajo Práctico 7A: Introducción a ML

## 1. En cada uno de los siguientes ejercicios, indique si en general se espera que un método de aprendizaje de máquinas flexible se comporte mejor o peor que uno inflexible. Justifique su respuesta.

### a) El tamaño de la muestra n es extremadamente grande, y el número de predictores p es pequeño.

Se espera que un método flexible se comporte mejor que un inflexible, dado que al tener un número grande de observaciones se puede estimar sin sobreajustar 

### b) El número de predictores p es extremadamente grande, y el número de observaciones n es pequeño.

A contrario del item a), se espera que un método inflexible tenga mejor rendimiento, dado que al tener pocas observaciones con muchos predictores corremos riesgo de 
sobreajustar si se usa un modelo flexible, perdiendo la generalización.

### c) La relación entre los predictores y la variable dependiente es altamente no lineal.

En este caso un método flexible se espera que se comporte mejor, debido a que es capaz de captar relaciones complejas, mientras que el inflexible impone un modelo rigido,
donde es más dificil que capte comportamientos diversos

###  ) La varianza de los términos de error, σ2 = Var(ϵ), es extremadamente alta.

Un método inflexible deberia tener un mejor rendimiento, ya que no depende tanto del conjunto de observaciones, donde un método flexible podria ajustarse bien a 
ciertos conjuntos, pero para otros actuaria de manera muy distinta. 

## 2. Explique si cada escenario representa un problema de clasificación o de regresión, e indique si el interes principal es inferir o predecir. Especifique n (cantidad de observaciones) y p (cantidad de predictores) en cada caso.

### a) Se recopila un conjunto de datos sobre las 500 empresas más importantes de Estados Unidos. Para cada una de las empresas se registran las ganancias, el número de empleados, la industria y el salario del director ejecutivo. Se tiene interés en comprender qué factores afectan el salario de los directores ejecutivos.

- Problema: Regresión
- Interés: Inferir
- n = 500, p = 4

### b) Se está considerando lanzar un nuevo producto y se desea saber si será un éxito o un fracaso. Se recolectan datos de 20 productos similares que fueron lanzados previamente. Para cada producto se ha registrado si fue un éxito o un fracaso, el precio cobrado por el producto, el presupuesto de marketing, el precio de la competencia, y otras diez variables.

- Problema: Clasificación
- Interés: Predecir
- n = 20, p = 14 

### c) Se tiene interes en predecir el % de cambio en el tipo de cambio USD/Euro en relación a los cambios semanales en los mercados de valores mundiales. Para eso se recolectan datos semanalmente durante todo el 2021. Para cada semana se registran el % de cambio de USD/Euro, el % de cambio en el mercado estadounidense, el % de cambio en el mercado británico, y el % de cambio en el mercado alemán.

- Problema: Regresión
- Interés: Predecir
- n = 48, p = 4 

## 3. ¿Cuáles son las ventajas y desventajas de un enfoque muy flexible (versus uno menos flexible) para la regresión o clasificación? ¿Bajo qué circunstancias podría preferirse un enfoque más flexible a uno menos flexible? ¿Cuándo podría preferirse un enfoque menos flexible?

Un enfoque muy flexible para regresión o clasificación tiene la ventaja de poder capturar relaciones complejas y no lineales entre las variables, lo que puede mejorar el desempeño predictivo cuando el verdadero patrón en los datos es complejo y se dispone de una gran cantidad de observaciones.
Sin embargo, los modelos flexibles son más propensos al sobreajuste (overfitting), especialmente cuando los datos son escasos o ruidosos, lo que puede llevar a peor capacidad de generalización. Además, suelen ser menos interpretables.

Se prefiere un enfoque flexible cuando se sospechan relaciones no lineales y se cuenta con suficiente cantidad de datos para evitar el sobreajuste.
Por el contrario, se prefiere un enfoque menos flexible cuando el conjunto de datos es pequeño, el ruido es alto, el fenómeno es simple o cuando se requiere interpretabilidad. Los modelos menos flexibles tienden a tener mayor sesgo pero menor varianza, lo cual puede resultar en mejor desempeño en estos casos.

## 4. Describa las diferencias entre un enfoque paramétrico y uno no paramétrico. ¿Cuáles son las ventajas y desventajas de un enfoque paramétrico para regresión o clasificación, a diferencia de un enfoque no paramétrico?

La ventaja de un enfoque paramétrico respecto a uno no paramétrico es: reduce un problema difícil a uno más sencillo, ya que encontrar los valores de los párametros a partir de los datos es más simple que adivinar la forma completa de una función arbitraria. Como desventaja tenemos que el enfoque paramétrico no suele adaptarse perfectamente a las funciones, por lo que si la función real se encuentra muy lejos de nuestra estimación, esta no será de gran ayuda. 

En cuanto al enfoque no paramétrico, tenemos como ventaja que se adaptará de una mejor forma al comportamiento real de la función y podrá adaptarse a una variedad amplia de funciones, pero esto requiere una cantidad muy grande de observaciones para obtener una aproximación precisa de la función. 

## 5. La siguiente tabla muestra un conjunto de entrenamiento que consta de seis observaciones, tres predictores, y una variable dependiente cualitativa. Suponga que se quiere usar este dataset para predecir Y cuando X1 = X2 = X3 = 0 usando K vecinos más cercanos.

### a) Calcule la distancia Euclidiana entre cada observación y el punto de prueba X1 = X2 = X3 = 0.

- d1 = √((0−0)² + (3−0)² + (0−0)²) = √(0 + 9 + 0) = √9 = 3.0000

- d2 = √((2−0)² + (0−0)² + (0−0)²) = √(4 + 0 + 0) = √4 = 2.0000

- d3 = √((0−0)² + (1−0)² + (3−0)²) = √(0 + 1 + 9) = √10 ≈ 3.1623

- d4 = √((0−0)² + (1−0)² + (2−0)²) = √(0 + 1 + 4) = √5 ≈ 2.2361

- d5 = √((−1−0)² + (0−0)² + (1−0)²) = √(1 + 0 + 1) = √2 ≈ 1.4142

- d6 = √((1−0)² + (1−0)² + (1−0)²) = √(1 + 1 + 1) = √3 ≈ 1.7321

### b) ¿Cuál es la predicción con K = 1? Justifique.

Para K = 1 tenemos que N0 = {Obs5}, por lo que al tener solamente un elemnto tendremos que: 

- Pr(Y = Verde | X = x0 ) = 1/1 * I(verde = verde) = 1. 

Por lo tanto, con K = 1 tenemos que Y0 = verde

### c) ¿Cuál es la predicción con K = 3? Justifique.

Para K = 3 tenemos que N0 = {Obs2, Obs5, Obs6} Entonces:

- Pr(Y = Verde | X = x0 ) = 1/3 * ( I(rojo = verde) + I(verde = verde) + I(rojo = verde) ) = 1/3. 

- Pr(Y = Rojo | X = x0 ) = 1/3 * ( I(rojo = rojo) + I(verde = rojo) + I(rojo = rojo) ) = 2/3. 

Por lo tanto, con K = 3 tenemos que Y0 = rojo

### d ) Si el límite de decisión de Bayes en este problema es altamente no lineal, ¿se espera que el mejor valor para K sea grande o pequeño? ¿Por qué?

Se espera que el mejor valor para K sea pequño, porque le permite al clasificador ser más flexible y capturar fronteras complejas, si K es grande 
el modelo toma en cuenta muchos vecinos generalizando demasiado, perdiendo el comportamiento real del limite no lineal. 