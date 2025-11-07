
suppressPackageStartupMessages({
  library(data.table)
  library(lubridate)
  library(lightgbm)
})

# ---------------------------
# Rutas
# ---------------------------
train_path <- "/home/ramiromartt/Escritorio/arbolado/arbolado-mendoza-dataset-train.csv"
test_path  <- "/home/ramiromartt/Escritorio/arbolado/arbolado-mza-dataset-test.csv"

train <- fread(train_path)
test  <- fread(test_path)
setnames(train, tolower(names(train)))
setnames(test,  tolower(names(test)))

# ---------------------------
# Helpers
# ---------------------------
num_from_str <- function(x) {
  if (is.numeric(x)) return(x)
  x <- as.character(x)
  x <- trimws(x)
  x <- gsub(",", ".", x)
  x <- gsub("–", "-", x)
  is_range <- grepl("^[0-9.]+-[0-9.]+$", x)
  out <- suppressWarnings(as.numeric(x))
  if (any(is_range)) {
    parts <- strsplit(x[is_range], "-")
    rng <- sapply(parts, function(v) mean(as.numeric(v), na.rm = TRUE))
    out[is_range] <- rng
  }
  if (any(is.na(out))) {
    m <- regmatches(x, gregexpr("[0-9]+\\.?[0-9]*", x))
    idx <- which(is.na(out))
    out[idx] <- suppressWarnings(as.numeric(sapply(m[idx], function(v) if (length(v)) v[1] else NA)))
  }
  out
}

# ---------------------------
# Feature engineering mínima
# ---------------------------
if ("altura" %in% names(train)) {
  train[, altura_num := num_from_str(altura)]
  test[,  altura_num := num_from_str(altura)]
}
if ("diametro_tronco" %in% names(train)) {
  train[, diametro_tronco_num := num_from_str(diametro_tronco)]
  test[,  diametro_tronco_num := num_from_str(diametro_tronco)]
}
if ("ultima_modificacion" %in% names(train)) {
  train[, ultima_modificacion := as.Date(ultima_modificacion)]
  test[,  ultima_modificacion := as.Date(ultima_modificacion)]
  max_date <- max(train$ultima_modificacion, na.rm = TRUE)
  train[, um_recency_days := as.integer(max_date - ultima_modificacion)]
  test[,  um_recency_days := as.integer(max_date - ultima_modificacion)]
}
if (all(c("altura_num", "circ_tronco_cm") %in% names(train))) {
  train[, alt_x_circ := altura_num * circ_tronco_cm]
  test[,  alt_x_circ := altura_num * circ_tronco_cm]
}

# ---------------------------
# Preparar features y target
# ---------------------------
stopifnot("inclinacion_peligrosa" %in% names(train))
label <- as.integer(train$inclinacion_peligrosa)

feature_cols <- setdiff(intersect(names(train), names(test)), c("inclinacion_peligrosa", "id", "ultima_modificacion", "altura", "diametro_tronco"))
X_train <- as.data.frame(train[, ..feature_cols])
X_test  <- as.data.frame(test[,  ..feature_cols])

# Detectar categóricas (explícitas + las que están como character)
cat_cols <- intersect(c("especie","nombre_seccion","seccion"), names(X_train))
char_cols <- names(which(sapply(X_train, is.character)))
cat_cols_final <- unique(c(cat_cols, char_cols))

# Alinear y codificar categóricas a 0..K-1
for (cc in cat_cols_final) {
  if (!is.factor(X_train[[cc]])) X_train[[cc]] <- as.factor(X_train[[cc]])
  X_test[[cc]] <- factor(X_test[[cc]], levels = levels(X_train[[cc]]))
  X_train[[cc]] <- as.integer(X_train[[cc]]) - 1L
  X_test[[cc]]  <- as.integer(X_test[[cc]]) - 1L
}
cat_idx <- match(cat_cols_final, names(X_train))
cat_idx <- cat_idx[!is.na(cat_idx)]

# Confirmar que no quedan character
# stopifnot(!any(sapply(X_train, is.character)))

# ---------------------------
# Desbalance (clase 1 escasa): scale_pos_weight
# ---------------------------
neg <- sum(label == 0, na.rm = TRUE)
pos <- sum(label == 1, na.rm = TRUE)
scale_pos_weight <- ifelse(pos > 0, neg/pos, 1)  # ~ 22673/2857 ≈ 7.94 en tu caso
cat(sprintf("Desbalance -> neg=%d, pos=%d, scale_pos_weight=%.2f\n", neg, pos, scale_pos_weight))

lgb_train <- lgb.Dataset(
  data = as.matrix(X_train),
  label = label,
  categorical_feature = cat_idx
)

params <- list(
  objective = "binary",
  metric = "auc",
  boosting = "gbdt",
  learning_rate = 0.05,
  num_leaves = 63,
  feature_fraction = 0.9,
  bagging_fraction = 0.8,
  bagging_freq = 1,
  max_depth = -1,
  min_data_in_leaf = 20,
  lambda_l2 = 1.0,
  verbosity = -1,
  scale_pos_weight = scale_pos_weight
)

# ---------------------------
# CV (AUC) para best_iter
# ---------------------------
set.seed(123)
cv <- lgb.cv(
  params = params,
  data = lgb_train,
  nrounds = 3000,
  nfold = 5,
  stratified = TRUE,
  early_stopping_rounds = 100,
  verbose = 1
)

best_iter <- cv$best_iter
best_auc  <- cv$best_score
cat(sprintf("\n[CV] Mejor AUC: %.5f en %d rondas\n", best_auc, best_iter))

# ---------------------------
# Holdout 80/20 para elegir UMBRAL (max F1)
# ---------------------------
set.seed(42)
idx <- sample.int(nrow(X_train), size = floor(0.8 * nrow(X_train)))
X_tr <- as.matrix(X_train[idx, , drop = FALSE])
y_tr <- label[idx]
X_va <- as.matrix(X_train[-idx, , drop = FALSE])
y_va <- label[-idx]

mdl_hold <- lgb.train(params, lgb.Dataset(X_tr, label = y_tr, categorical_feature = cat_idx), nrounds = best_iter, verbose = -1)
p_va <- predict(mdl_hold, X_va)

best_th <- 0.5
best_f1 <- -Inf
for (th in seq(0.05, 0.95, by = 0.01)) {
  pred <- ifelse(p_va >= th, 1L, 0L)
  tp <- sum(pred == 1L & y_va == 1L)
  fp <- sum(pred == 1L & y_va == 0L)
  fn <- sum(pred == 0L & y_va == 1L)
  prec <- ifelse(tp + fp == 0, 0, tp/(tp+fp))
  rec  <- ifelse(tp + fn == 0, 0, tp/(tp+fn))
  f1   <- ifelse(prec + rec == 0, 0, 2*prec*rec/(prec+rec))
  if (f1 > best_f1) { best_f1 <- f1; best_th <- th }
}
cat(sprintf("Umbral óptimo por holdout (max F1): %.3f\n", best_th))

# ---------------------------
# Entrenamiento final y predicción sobre test
# ---------------------------
model <- lgb.train(params = params, data = lgb_train, nrounds = best_iter, verbose = 1)

pred_test_prob <- predict(model, as.matrix(X_test))
summary_probs <- summary(pred_test_prob)
print(summary_probs)

pred_test <- ifelse(pred_test_prob >= best_th, 1L, 0L)
cat("Distribución de etiquetas en test con umbral óptimo:\n")
print(table(pred_test))

submission <- data.table(id = test$id, inclinacion_peligrosa = pred_test)
fwrite(submission, "submission_lgbm_labels.csv")
cat("\nArchivo generado: submission_lgbm_labels.csv (valores 0/1)\n")
