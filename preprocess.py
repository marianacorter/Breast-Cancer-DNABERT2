# Libraries:

import pandas as pd # pandas is used to load, filter, and manipulate the ClinVar dataset
from pyfaidx import Fasta # Pyfaidx provides efficient random access to genomic sequences stored
from tqdm import tqdm # displays a progress bar while processing large datasets
from sklearn.model_selection import train_test_split # splits the dataset into training, validation, and test sets

# Function to filter the ClinVar variant summary file and retain only the breast cancer-associated SNVs:
def filter_clinvar():
    INPUT_FILE = "variant_summary.txt"
    OUTPUT_FILE = "breast_cancer_variants.csv"
    print("\nStep 1: Filtering ClinVar")

    # Define keywords used to identify breast cancer-related phenotypes
    breast_keywords = ["breast", "hereditary breast", "breast carcinoma", "breast cancer", "hereditary breast and ovarian cancer"]
    pattern = "|".join(breast_keywords)

    # Map ClinVar clinical significance categories to binary labels
    allowed = {"Pathogenic": 1, "Likely pathogenic": 1, "Benign": 0, "Likely benign": 0}
    chunks = [] # store the filtered data from each chunk
    total_rows = 0

    # Read the ClinVar file in chunks to reduce memory usage:
    for chunk in pd.read_csv(
        INPUT_FILE,
        sep="\t",
        low_memory=False,
        chunksize=100000):

        total_rows += len(chunk) # update the total number of processed variant

        chunk = chunk[chunk["Assembly"] == "GRCh38"] # keep only variants mapped to the GRCh38 human genome assembly
        chunk = chunk[chunk["PhenotypeList"].str.contains(pattern, case=False, na=False)] # keep only variants whose phenotype contains one of the keywords
        chunk = chunk[chunk["Type"] == "single nucleotide variant"] # retain only single nucleotide variants
        chunk = chunk[chunk["ClinicalSignificance"].isin(allowed.keys())] # keep only variants with one of the selected clinical significance labels
        chunk["label"] = chunk["ClinicalSignificance"].map(allowed) # convert the clinical significance labels into binary classes
        chunk = chunk[["GeneSymbol", "Chromosome", "Start", "ReferenceAllele", "AlternateAllele","ClinicalSignificance", "label"]] # keep only the columns required for downstream analysis
        chunks.append(chunk) # store the chunk

    clinvar = pd.concat(chunks, ignore_index=True) # combine everything

    # Print and save results:
    print(f"\nOriginal variants: {total_rows:,}")
    print(f"Remaining variants: {len(clinvar):,}")
    print("\nClass distribution")
    print(clinvar["label"].value_counts())
    clinvar.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved: {OUTPUT_FILE}")

# Function to extract genomic sequences surrounding each breast cancer variant:
def extract_sequences():
    GENOME = "hg38.fa"
    INPUT = "breast_cancer_variants.csv"
    OUTPUT = "variant_sequences.csv"
    WINDOW = 200 # number of base pairs extracted upstream and downstream

    print("\nStep 2: Extracting Sequences")

    genome = Fasta(GENOME) # load the reference genome using pyfaidx
    variants = pd.read_csv(INPUT) # load the filtered ClinVar variants
    print(f"Variants: {len(variants):,}")

    def extract_sequence(chromosome, position):
        chromosome = str(chromosome) # convert chromosome names to strings
        if chromosome not in genome.keys(): # if the chromosome name does not contain the "chr" prefix add it
            chromosome = "chr" + chromosome
        start = max(1, position - WINDOW) #  define the start coordinate
        end = position + WINDOW  # define the end coordinate
        return genome[chromosome][start - 1:end].seq.upper() # extract the DNA sequence from the reference genome and convert it to uppercase
    sequences = [] # store the sequences

    for _, row in tqdm(variants.iterrows(), total=len(variants)): # iterate through every variant in the dataset
        try:
            seq = extract_sequence(row["Chromosome"], int(row["Start"])) # extract the sequence surrounding the variant
            if len(seq) == 401: # keep only complete sequences of length 401 bp
                sequences.append(seq)
            else:
                sequences.append(None)
        except Exception: # if an invalid chromosome is found report missiing value
            sequences.append(None)

    variants["sequence"] = sequences # add the sequences as a new column
    variants = variants.dropna()

    # Print and save results:
    print(f"Remaining complete sequences: {len(variants):,}")
    variants.to_csv(OUTPUT, index=False)
    print(f"Saved: {OUTPUT}")

# Function to clean the extracted sequence dataset and split it into training, validation, and test sets:
def prepare_dataset():
    INPUT = "variant_sequences.csv"
    # output files:
    TRAIN_FILE = "train.csv"
    VALID_FILE = "valid.csv"
    TEST_FILE = "test.csv"

    print("\nStep 3: Preparing Dataset")

    df = pd.read_csv(INPUT) # load the dataset containing the extracted sequences
    print(f"Sequences before cleaning: {len(df):,}")

    df = df[["sequence", "label"]] # keep only the columns required for model training
    df = df.dropna() # remove rows with missing values
    df = df.drop_duplicates(subset="sequence") # remove duplicate DNA sequences
    print(f"Sequences after removing duplicates: {len(df):,}")

    df = df.sample(frac=1, random_state=42).reset_index(drop=True) # randomly shuffle the dataset before splitting
    
    # Split the dataset into 70% training and 30% temporary dataset
    train_df, temp_df = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=42)

    # Split the temporary dataset into validation and test sets of 15% validation and 15% test
    valid_df, test_df = train_test_split(temp_df, test_size=0.50, stratify=temp_df["label"], random_state=42)

    # Save each dataset as a separate CSV file
    train_df.to_csv(TRAIN_FILE, index=False)
    valid_df.to_csv(VALID_FILE, index=False)
    test_df.to_csv(TEST_FILE, index=False)

    # Print and save results:
    print("\nDataset Summary")
    print(f"Training:   {len(train_df):,}")
    print(f"Validation: {len(valid_df):,}")
    print(f"Testing:    {len(test_df):,}")

    # training results
    print("\nTraining labels")
    print(train_df["label"].value_counts())

    # validation results
    print("\nValidation labels")
    print(valid_df["label"].value_counts())

    # testing results
    print("\nTesting labels")
    print(test_df["label"].value_counts())

    print("\nSaved:")
    print(TRAIN_FILE)
    print(VALID_FILE)
    print(TEST_FILE)

# Execute the preprocessing pipeline:
if __name__ == "__main__":
    print("Breast Cancer DNABERT2 Preprocessing Pipeline")
    filter_clinvar()
    extract_sequences()
    prepare_dataset()
    print("\nPreprocessing complete")