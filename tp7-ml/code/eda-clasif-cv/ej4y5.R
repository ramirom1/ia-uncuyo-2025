library(dplyr)
library(readr)

add_prediction_prob <- function(df) {
  df %>% mutate(prediction_prob = runif(n()))
}

random_classifier <- function(df) {
  df %>%
    mutate(prediction_class = ifelse(prediction_prob > 0.5, 1, 0))
}

biggerclass_classifier <- function(df) {
  
  # Identificar la clase mayoritaria en la columna real
  majority_class <- df %>%
    count(inclinacion_peligrosa) %>%
    arrange(desc(n)) %>%
    slice(1) %>%
    pull(inclinacion_peligrosa)
  
  # Crear prediction_class asignando siempre esa clase
  df$prediction_class <- majority_class
  
  return(df)
}

arbolado_validation <- read_csv("/home/ramiromartt/Escritorio/arbolado/arbolado-mendoza-dataset-validation.csv")

#arbolado_validation <- add_prediction_prob(arbolado_validation)

#cambiar nombre de la funcion
arbolado_validation <- biggerclass_classifier(arbolado_validation) 

# True Positive: real = 1, predicción = 1
TP <- arbolado_validation %>%
  filter(inclinacion_peligrosa == 1, prediction_class == 1) %>%
  tally()

# True Negative: real = 0, predicción = 0
TN <- arbolado_validation %>%
  filter(inclinacion_peligrosa == 0, prediction_class == 0) %>%
  tally()

# False Positive: real = 0, predicción = 1
FP <- arbolado_validation %>%
  filter(inclinacion_peligrosa == 0, prediction_class == 1) %>%
  tally()

# False Negative: real = 1, predicción = 0
FN <- arbolado_validation %>%
  filter(inclinacion_peligrosa == 1, prediction_class == 0) %>%
  tally()

accuracy <- function(TP, TN, FP, FN) {
  (TP + TN) / (TP + TN + FP + FN)
}

precision <- function(TP, FP) {
  if ((TP + FP) == 0) return(NA)  # evita división por 0
  TP / (TP + FP)
}

sensitivity <- function(TP, FN) {  # también llamada recall
  if ((TP + FN) == 0) return(NA)
  TP / (TP + FN)
}

specificity <- function(TN, FP) {
  if ((TN + FP) == 0) return(NA)
  TN / (TN + FP)
}


#Confusion matrix
confusion_matrix <- tibble(
  Actual_Pos = c(TP$n, FN$n),
  Actual_Neg = c(FP$n, TN$n)
)

confusion_matrix <- as.data.frame(confusion_matrix)
rownames(confusion_matrix) <- c("Pred_Pos", "Pred_Neg")
confusion_matrix

#Metricas
accuracy(TP, TN, FP, FN)
precision(TP, FP)
sensitivity(TP, FN)
specificity(TN, FP)


