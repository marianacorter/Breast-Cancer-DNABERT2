# Breast Cancer Variant Classification Using DNABERT-2

## Author

Mariana Corte

262RBIF-125-1: Bioinformatics Software Engineering and AI/ML

## Project Overview

This project develops a deep learning pipeline to classify breast cancer-associated genetic variants as benign or pathogenic using a pretrained DNABERT-2 transformer model.

Breast cancer variants were obtained from the ClinVar database, filtered according to clinical significance and phenotype, and converted into genomic sequence inputs by extracting a 401 bp window centered on each variant from the human reference genome (GRCh38). The resulting sequences were used to fine-tune DNABERT-2 for binary sequence classification.

## Requirements

### Software

Before running the preprocessing pipeline, install the following software:

- Docker Desktop

At least 10 GB of free disk space is recommended to store the Docker image, reference genome, ClinVar dataset, and generated output files.

### Input Files

The preprocessing pipeline requires the following input files:

#### 1. ClinVar Variant Summary

Download the latest `variant_summary.txt.gz` file from the NCBI ClinVar FTP site:

https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/

After downloading:

1. Extract the compressed file (`variant_summary.txt.gz`).
2. Place the resulting `variant_summary.txt` file in your project directory.

#### 2. Human Reference Genome (GRCh38)

Download the GRCh38 reference genome (FASTA format) from UCSC:

https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/

Download:

- `hg38.fa.gz`

After downloading:

1. Decompress the file to obtain: hg38.fa


## Docker

The preprocessing pipeline can be executed using the pre-built Docker image available on Docker Hub.

### Pull the Docker image

Download the image:

```bash
docker pull marianacor/breast-project
```

### Prepare the input files

Before running the container, place the following files in your working directory:

- `variant_summary.txt` (ClinVar variant summary file)
- `hg38.fa` (Human reference genome in FASTA format)
- `preprocess.py` (Preprocessing python file)
- `requirements.txt` (File to install the dependencies)

The preprocessing script uses these files to filter breast cancer-associated variants and extract the corresponding DNA sequences.

### Run the preprocessing pipeline

From the directory containing the input files, execute:

```bash
docker run --rm -v "$(pwd)":/app marianacor/breast-project
```

The `-v "$(pwd)":/app` option mounts the current working directory into the Docker container, allowing the script to access the input files and save the generated outputs directly to your local directory. The running container will automatically execute:

```bash
python preprocess.py
```

## Dataset

The dataset was generated from the ClinVar `variant_summary.txt` file.

Filtering criteria included:

- Human genome assembly: GRCh38
- Variant type: Single Nucleotide Variants (SNVs)
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


### Output files

After the pipeline finishes, the following files will be generated:

```
breast_cancer_variants.csv
variant_sequences.csv
train.csv
valid.csv
test.csv
```

These files are then used by the `train_DNABERT2.ipynb` notebook for model training and evaluation.

## Model

### Environment Setup

The `train_DNABERT2.ipynb` notebook was developed and tested using Google Colab with GPU.

### 1. Enable GPU

Before running the notebook, switch the Colab runtime to a GPU:

### 2. Install the required packages

Run the following commands in the first notebook cell:

```python
!pip -q install -U "transformers==4.38.2" "peft==0.10.0" "accelerate==0.27.2" datasets scikit-learn
!pip -q uninstall -y triton
```

These package versions were used during model development to ensure compatibility with DNABERT-2. After the packages have been installed, restart the Colab runtime. Restarting the runtime ensures that the newly installed package versions are loaded correctly before training the model.

### 3. Run the notebook

Open `train_DNABERT2.ipynb` and execute all cells sequentially. The notebook will:

- Load the training, validation, and test datasets.
- Tokenize the DNA sequences using the DNABERT-2 tokenizer.
- Fine-tune the pretrained DNABERT-2 model.
- Evaluate the classifier on the test dataset.
- Generate the performance metrics and evaluation figures, including the confusion matrix and ROC curve.

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

The extracted DNA sequences correspond to the reference genome sequence surrounding each variant. The alternate allele is not inserted into the sequence because allele information was unavailable in the ClinVar summary file. Consequently, the model learns from the genomic context rather than the specific nucleotide change.

## References

1. Magics-Lab. (2024). GitHub - MAGICS-LAB/DNABERT_2: [ICLR 2024] DNABERT-2: Efficient Foundation Model and Benchmark for Multi-Species Genome. GitHub. https://github.com/MAGICS-LAB/DNABERT_2
   
2. Ji, Y., Zhou, Z., Liu, H., & Davuluri, R. V. (2021). DNABERT: pre-trained Bidirectional Encoder Representations from Transformers model for DNA-language in genome. Bioinformatics (Oxford, England), 37(15), 2112–2120. https://doi.org/10.1093/bioinformatics/btab083 
