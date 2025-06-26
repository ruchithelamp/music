#!/bin/bash

#SBATCH --job-name=genius_lyrics
#SBATCH --account=siads696s25_class
#SBATCH --mail-user=smacieje@umich.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=1g
#SBATCH --time=8:00:00
#SBATCH --partition=standard
#SBATCH --output=genius_lyrics_%j.log
#SBATCH --error=genius_lyrics_%j.err

# === Error if no input file ===
INPUT_FILE=$1
if [ -z "$INPUT_FILE" ]; then
  echo "ERROR: No input CSV file provided. Usage: sbatch lyrics_fetcher.sh ./your_songs.csv"
  exit 1
fi

echo "Job started on $(date)"
echo "Running on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"
echo "Working directory: $(pwd)"
echo "Using input file: $INPUT_FILE"

# Load environment
module load python/3.11.5
source /home/smacieje/myenv/bin/activate

# Optional: move to a temporary output directory
OUTPUT_DIR=~/lyrics_output_${SLURM_JOB_ID}
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR" || exit

# Copy the input file to output directory for processing
cp "$SLURM_SUBMIT_DIR/$INPUT_FILE" ./

# Run the Genius lyrics script
python "$SLURM_SUBMIT_DIR/lyrics_fetcher.py" "$(basename "$INPUT_FILE")" \
    --output "lyrics_results_${SLURM_JOB_ID}.csv" \
    --delay 1.5 \
    --checkpoint-interval 10

# Copy results back to submit directory
if [ -f "lyrics_results_${SLURM_JOB_ID}.csv" ]; then
    cp "lyrics_results_${SLURM_JOB_ID}.csv" "$SLURM_SUBMIT_DIR/"
    echo "Results copied to: $SLURM_SUBMIT_DIR/lyrics_results_${SLURM_JOB_ID}.csv"
else
    echo "WARNING: Output file not found!"
fi

echo "Job completed at $(date)"
