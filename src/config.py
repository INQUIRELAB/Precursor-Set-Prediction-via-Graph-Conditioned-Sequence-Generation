"""
Configuration constants for file paths and directories.

Defines all raw data paths, processed data paths, and output directories.
No logic - just path constants.
"""

from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

# Raw data directories
RAW_DATA_DIR = DATA_DIR / "raw"
KONONOVA_2019_DIR = RAW_DATA_DIR / "kononova2019"
LEE_2025_DIR = RAW_DATA_DIR / "lee2025"

# Raw data files - Legacy datasets
RAW_SS_RXNS_80806 = RAW_DATA_DIR / "SS_rxns_80806.json.gz"
RAW_SOLID_STATE_2019 = RAW_DATA_DIR / "solid-state_dataset_2019-06-27_upd.json"

# Raw data files - Kononova et al. 2019
KONONOVA_TEXT_MINED = KONONOVA_2019_DIR / "text_mined_reactions.json"
KONONOVA_CURATED = KONONOVA_2019_DIR / "curated_reactions.json"

# Raw data files - Lee et al. 2025
LEE_2025_REACTIONS = LEE_2025_DIR / "lee2025_reactions.json"
LEE_2025_SUPPLEMENTARY = LEE_2025_DIR / "supplementary_data.json"

# Processed data directory
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Processed data files - Parquet
PROCESSED_REACTIONS_PARQUET = PROCESSED_DATA_DIR / "reactions.parquet"
PROCESSED_TRAIN_PARQUET = PROCESSED_DATA_DIR / "train.parquet"
PROCESSED_VAL_PARQUET = PROCESSED_DATA_DIR / "val.parquet"
PROCESSED_TEST_PARQUET = PROCESSED_DATA_DIR / "test.parquet"

# Processed data files - CSV (if needed)
PROCESSED_REACTIONS_CSV = PROCESSED_DATA_DIR / "reactions.csv"
PROCESSED_TRAIN_CSV = PROCESSED_DATA_DIR / "train.csv"
PROCESSED_VAL_CSV = PROCESSED_DATA_DIR / "val.csv"
PROCESSED_TEST_CSV = PROCESSED_DATA_DIR / "test.csv"

# Processed data files - Metadata
SPLIT_INFO_JSON = PROCESSED_DATA_DIR / "split_info.json"
DATASET_STATISTICS_JSON = PROCESSED_DATA_DIR / "dataset_statistics.json"
LABEL_ENCODER_PKL = PROCESSED_DATA_DIR / "label_encoder.pkl"
FEATURE_NAMES_JSON = PROCESSED_DATA_DIR / "feature_names.json"

# Model directories
XGB_BASELINE_DIR = MODELS_DIR / "xgb_baseline"
TRANSFORMER_DIR = MODELS_DIR / "transformer"
GNN_DIR = MODELS_DIR / "gnn"

# Model files - XGBoost
XGB_MODEL_PKL = XGB_BASELINE_DIR / "xgb_model.pkl"
XGB_LABEL_ENCODER_PKL = XGB_BASELINE_DIR / "label_encoder.pkl"
XGB_SCALER_PKL = XGB_BASELINE_DIR / "scaler.pkl"
XGB_FEATURE_NAMES_JSON = XGB_BASELINE_DIR / "feature_names.json"
XGB_TRAINING_METADATA_JSON = XGB_BASELINE_DIR / "training_metadata.json"

# Results directory
XGB_RESULTS_JSON = RESULTS_DIR / "xgb_baseline_results.json"
TRANSFORMER_RESULTS_JSON = RESULTS_DIR / "transformer_results.json"
GNN_RESULTS_JSON = RESULTS_DIR / "gnn_results.json"

# Artifacts directory (experiments, logs, etc.)
EXPERIMENT_LOGS_DIR = ARTIFACTS_DIR / "logs"
TENSORBOARD_DIR = ARTIFACTS_DIR / "tensorboard"
WANDB_DIR = ARTIFACTS_DIR / "wandb"
CHECKPOINTS_DIR = ARTIFACTS_DIR / "checkpoints"
