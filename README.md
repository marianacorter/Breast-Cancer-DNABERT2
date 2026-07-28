# Breast Cancer Variant Classification Using DNABERT-2

## Project Overview

This project develops a deep learning pipeline to classify breast cancer-associated genetic variants as benign or pathogenic using a pretrained DNABERT-2 transformer model.

Breast cancer variants were obtained from the ClinVar database, filtered according to clinical significance and phenotype, and converted into genomic sequence inputs by extracting a 401 bp window centered on each variant from the human reference genome (GRCh38). The resulting sequences were used to fine-tune DNABERT-2 for binary sequence classification.

## Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

## Docker

Build the Docker image:

```bash
docker build -t breast-project .
```

Run the preprocessing pipeline:

```bash
docker run --rm \
-v "$(pwd)":/app \
breast-project
```

## Dataset

The dataset was generated from the ClinVar `variant_summary.txt` file.

Filtering criteria included:

- Human genome assembly: **GRCh38**
- Variant type: **Single Nucleotide Variants (SNVs)**
- Breast cancer-related phenotypes
- Clinical significance:
  - Pathogenic
  - Likely Pathogenic
  - Benign
  - Likely Benign

Binary labels were assigned as:

| Label | Clinical Significance |
|------:|-----------------------|
| 0 | Benign / Likely Benign |
| 1 | Pathogenic / Likely Pathogenic |

A 401 bp DNA sequence (±200 bp around each variant) was extracted from the hg38 reference genome for every retained variant.

## Preprocessing Pipeline

The preprocessing script performs three steps:

### Step 1: Filter ClinVar

- Load the ClinVar variant summary file
- Filter breast cancer-associated variants
- Keep only GRCh38 SNVs
- Assign binary labels
- Save filtered variants

Output:

```
breast_cancer_variants.csv
```

### Step 2: Extract DNA Sequences

Using the hg38 reference genome, a 401 bp sequence is extracted around each variant.

Output:

```
variant_sequences.csv
```

### Step 3: Prepare the Dataset

- Remove incomplete sequences
- Remove duplicate sequences
- Shuffle the dataset
- Create a stratified train/validation/test split (70/15/15)

Outputs:

```
train.csv
valid.csv
test.csv
```

## Model

The classifier is based on a pretrained **DNABERT-2** transformer.

Training settings:

- Learning rate: 2e-5
- Epochs: 5
- Batch size: 4 (training)
- Batch size: 8 (evaluation)
- Weight decay: 0.01
- Optimizer: AdamW (Hugging Face Trainer)
- Loss function: Weighted CrossEntropyLoss

To compensate for class imbalance, class weights were computed using Scikit-learn's `compute_class_weight()` function.

## Evaluation Metrics

Model performance was evaluated using:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion Matrix
- ROC Curve

## Running the Notebook

Open

```
BreastCancer_DNABERT2Model.ipynb
```

Run all cells to:

- Load the datasets
- Tokenize DNA sequences
- Fine-tune DNABERT-2
- Evaluate the classifier
- Generate performance figures

## Results

After preprocessing:

| Step | Variants |
|------|----------:|
| Original ClinVar | 9,020,434 |
| Filtered breast cancer variants | 16,117 |
| Complete sequences | 16,087 |
| Unique sequences | 14,000 |

Dataset split:

| Dataset | Samples |
|---------|---------:|
| Training | 9,800 |
| Validation | 2,100 |
| Testing | 2,100 |

The final model was evaluated using the test dataset. Performance metrics, confusion matrix, and ROC curve are generated in the training notebook.

## Notes

The extracted DNA sequences correspond to the **reference genome sequence** surrounding each variant. The alternate allele is not inserted into the sequence because allele information was unavailable in the ClinVar summary file. Consequently, the model learns from the genomic context rather than the specific nucleotide change.

---

## Author

Mariana Corte
