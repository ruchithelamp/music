#!/bin/bash

#SBATCH --job-name=genius_lyrics_array
#SBATCH --account=siads696s25_class
#SBATCH --mail-user=smacieje@umich.edu
#SBATCH --mail-type=ARRAY_TASKS
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=1g
#SBATCH --time=8:00:00
#SBATCH --partition=standard
#SBATCH --output=genius_lyrics_array_%A_%a.log
#SBATCH --error=genius_lyrics_array_%A_%a.err
#SBATCH --array=1-N%10

# === Error if no input directory ===
INPUT_DIR=$1
if [ -z "$INPUT_DIR" ] || [ ! -d "$INPUT_DIR" ]; then
  echo "ERROR: No input directory provided or directory doesn't exist. Usage: sbatch run_lyrics_fetcher.sh /music_data/2007/musicbrainz/"
  exit 1
fi

echo "Array job started on $(date)"
echo "Running on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"
echo "Array Task ID: $SLURM_ARRAY_TASK_ID"
echo "Working directory: $(pwd)"
echo "Using input directory: $INPUT_DIR"

# Create array of CSV files
mapfile -t CSV_FILES < <(find "$INPUT_DIR" -name "*.csv" -type f | sort)
TOTAL_FILES=${#CSV_FILES[@]}

echo "Found $TOTAL_FILES CSV files to process"

# Check if array task ID is valid
if [ "$SLURM_ARRAY_TASK_ID" -gt "$TOTAL_FILES" ]; then
    echo "Array task ID $SLURM_ARRAY_TASK_ID exceeds number of files ($TOTAL_FILES). Exiting."
    exit 0
fi

# Get the file for this array task (arrays are 1-indexed, bash arrays are 0-indexed)
CURRENT_FILE="${CSV_FILES[$((SLURM_ARRAY_TASK_ID-1))]}"
FILENAME=$(basename "$CURRENT_FILE")

echo "Processing file: $CURRENT_FILE"

# Load environment
module load python/3.11.5
source /home/smacieje/myenv/bin/activate

# Create unique output directory for this array task
OUTPUT_DIR=~/lyrics_output_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR" || exit

# Copy the input file to output directory for processing
cp "$CURRENT_FILE" ./

# Run the Genius lyrics script
python "$SLURM_SUBMIT_DIR/lyrics_fetcher.py" "$FILENAME" \
    --output "lyrics_results_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}.csv" \
    --delay 1.5 \
    --checkpoint-interval 10

# Copy results back to submit directory
OUTPUT_FILE="lyrics_results_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}.csv"
if [ -f "$OUTPUT_FILE" ]; then
    cp "$OUTPUT_FILE" "$SLURM_SUBMIT_DIR/"
    echo "Results copied to: $SLURM_SUBMIT_DIR/$OUTPUT_FILE"
else
    echo "WARNING: Output file not found!"
fi

# Clean up temporary directory (optional)
cd "$SLURM_SUBMIT_DIR"
rm -rf "$OUTPUT_DIR"

echo "Array task $SLURM_ARRAY_TASK_ID completed at $(date)"