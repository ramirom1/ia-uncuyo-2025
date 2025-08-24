## 2.10 Consider a modified version of the vacuum environment in Exercise 2.8, in which the agent is penalized one point for each movement.

**a. Can a simple reflex agent be perfectly rational for this environment? Explain.**

No, un agente reflexivo simple no puede ser perfectamente racional en ese ambiente debido a que al no tener memoria no puede actuar en base a la información previamente obtenida, por lo que no podrá ser eficiente.

**b. What about a reflex agent with state? Design such an agent.**

Si el agente reflexivo tuviera estados, cambiaría su comportamiento, haciendo que se convierta en racional al no tener que volver a pasar por posiciones ya recorridas, lo que no le restaría tantos puntos como si no los pudiese recordar.

**c. How do your answers to a and b change if the agent’s percepts give it the clean/dirty status of every square in the environment?**

Si la percepción del agente le diera el conocimiento sobre el estado de limpieza de cada casilla, ambos agentes serían racionales debido a que cuentan con información que les permite moverse con un sentido, sin tener que recorrer por recorrer. 

---

## 2.11 Consider a modified version of the vacuum environment in Exercise 2.8, in which the geography of the environment—its extent, boundaries, and obstacles—is unknown, as is the initial dirt configuration. (The agent can go Up and Down as well as Left and Right.)

**a. Can a simple reflex agent be perfectly rational for this environment? Explain.**

No, no podría ser perfectamente racional, bajo la misma premisa que en 2.10) a), el agente no tiene memoria lo que no le permite seguir un algoritmo de búsqueda. Al igual que en el caso anterior el agente tampoco tiene información acerca del ambiente, por lo que en cada paso se encuentra en un nuevo punto desconocido. 


**b. Can a simple reflex agent with a randomized agent function outperform a simple reflex agent?**

Si, un agente reflexivo random podría obtener mejores resultados que un agente reflexivo simple, aunque depende de cómo están posicionados los objetivos. Además, la tasa de veces que es mejor que el reflexivo simple es muy baja.

**c. Can you design an environment in which your randomized agent will perform poorly? Show your results.**

Un ambiente en el que el agente random tenga malos resultados la diseñaria ubicando la suciedad en cierto patrón repetitivo y donde entre suciedades haya cierta distancia, para que el agente no aproveche bancos grandes de suciedad. 

**d. Can a reflex agent with state outperform a simple reflex agent? Can you design a rational agent of this type?**

Sí, un agente reflexivo con memoria debería tener mejor rendimiento que uno sin memoria, debido a que esta le permite recordar casillas donde no hay basura y por lo tanto no repetirá dichos lugares, necesitando menos movimientos. Lo mismo con obstáculos y límites.