library(dplyr)
library(rpart)
library(readr)

# --- Métricas (con guardas ante división por cero) ---
accuracy    <- function(TP, TN, FP, FN) (TP + TN) / (TP + TN + FP + FN)
precision   <- function(TP, FP) if ((TP + FP) == 0) NA_real_ else TP / (TP + FP)
sensitivity <- function(TP, FN) if ((TP + FN) == 0) NA_real_ else TP / (TP + FN)  # recall
specificity <- function(TN, FP) if ((TN + FP) == 0) NA_real_ else TN / (TN + FP)

arbolado <- read_csv("/home/ramiromartt/Escritorio/arbolado/arbolado-mendoza-dataset-train.csv")


 create_folds <- function(df, k) {
   n <- nrow(df)
   idx <- sample(n)
   parts <- split(idx, cut(seq_along(idx), breaks = k, labels = FALSE))
   names(parts) <- paste0("Fold", seq_len(k))
   parts
 }

 cross_validation <- function(df, k = 5) {
   # 1) Asegurar tipos: target como factor 0/1; caracteres -> factor
   df <- df %>%
     mutate(
       inclinacion_peligrosa = factor(inclinacion_peligrosa, levels = c(0, 1))
     ) %>%
     mutate(across(where(is.character), ~ factor(.)))  # convierte strings a factor
   
   # 2) Guardar niveles GLOBALES de todos los factores (para fijarlos en train/val)
   fac_cols <- names(Filter(is.factor, df))
   lvl_map <- lapply(df[fac_cols], levels)  # lista: nombre -> niveles globales
   
   # 3) Fijar niveles globales en todo el df (y no dropear luego)
   for (col in fac_cols) {
     df[[col]] <- factor(df[[col]], levels = lvl_map[[col]])
   }
   
   # 4) Fórmula (usá la tuya; acá un ejemplo)
   train_formula <- inclinacion_peligrosa ~ altura + circ_tronco_cm + lat + long + seccion + especie
   
   # 5) Folds
   folds <- create_folds(df, k)
   
   per_fold <- lapply(seq_along(folds), function(i) {
     val_idx <- folds[[i]]
     train_df <- df[-val_idx, , drop = FALSE]
     val_df   <- df[ val_idx, , drop = FALSE]
     
     # 6) Reaplicar niveles globales en ambos subconjuntos (por si acaso)
     for (col in fac_cols) {
       train_df[[col]] <- factor(train_df[[col]], levels = lvl_map[[col]])
       val_df[[col]]   <- factor(val_df[[col]],   levels = lvl_map[[col]])
     }
     
     # 7) Entrenar y predecir
     tree_model <- rpart(train_formula, data = train_df)
     p_class <- predict(tree_model, newdata = val_df, type = "class")
     p_class <- factor(p_class, levels = levels(df$inclinacion_peligrosa))
     
     # 8) Métricas
     TP <- sum(val_df$inclinacion_peligrosa == 1 & p_class == 1, na.rm = TRUE)
     TN <- sum(val_df$inclinacion_peligrosa == 0 & p_class == 0, na.rm = TRUE)
     FP <- sum(val_df$inclinacion_peligrosa == 0 & p_class == 1, na.rm = TRUE)
     FN <- sum(val_df$inclinacion_peligrosa == 1 & p_class == 0, na.rm = TRUE)
     
     tibble(
       Fold = names(folds)[i],
       TP = TP, TN = TN, FP = FP, FN = FN,
       Accuracy = accuracy(TP, TN, FP, FN),
       Precision = precision(TP, FP),
       Sensitivity = sensitivity(TP, FN),
       Specificity = specificity(TN, FP)
     )
   }) %>% bind_rows()
   
   summary <- per_fold %>%
     summarise(
       Accuracy_mean    = mean(Accuracy, na.rm = TRUE),
       Accuracy_sd      = sd(Accuracy, na.rm = TRUE),
       Precision_mean   = mean(Precision, na.rm = TRUE),
       Precision_sd     = sd(Precision, na.rm = TRUE),
       Sensitivity_mean = mean(Sensitivity, na.rm = TRUE),
       Sensitivity_sd   = sd(Sensitivity, na.rm = TRUE),
       Specificity_mean = mean(Specificity, na.rm = TRUE),
       Specificity_sd   = sd(Specificity, na.rm = TRUE)
     )
   
   list(per_fold = per_fold, summary = summary)
   as.data.frame(summary)
 }

cross_validation(arbolado, 10)