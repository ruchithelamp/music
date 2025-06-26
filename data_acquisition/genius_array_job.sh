#!/bin/bash

#SBATCH --job-name=genius_lyrics_array
#SBATCH --account=siads696s25_class
#SBATCH --mail-user=smacieje@umich.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=1g
#SBATCH --time=8:00:00
#SBATCH --partition=standard
#SBATCH --output=genius_lyrics_array_%A_%a.log
#SBATCH --error=genius_lyrics_array_%A_%a.err
#SBATCH --array=1-100%10

# === Error if no input folder ===
INPUT_FOLDER=$1
if [ -z "$INPUT_FOLDER" ]; then
  echo "ERROR: No input folder provided. Usage: sbatch genius_array_job.sh /path/to/input/folder"
  exit 1
fi

# Check if folder exists
if [ ! -d "$INPUT_FOLDER" ]; then
  echo "ERROR: Input folder '$INPUT_FOLDER' does not exist"
  exit 1
fi

echo "Array job started on $(date)"
echo "Running on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"
echo "Array Task ID: $SLURM_ARRAY_TASK_ID"
echo "Working directory: $(pwd)"
echo "Using input folder: $INPUT_FOLDER"

# Create array of input files (CSV files only)
mapfile -t INPUT_FILES < <(find "$INPUT_FOLDER" -name "*.csv" -type f | sort)

# Check if we have any CSV files
if [ ${#INPUT_FILES[@]} -eq 0 ]; then
  echo "ERROR: No CSV files found in '$INPUT_FOLDER'"
  exit 1
fi

echo "Found ${#INPUT_FILES[@]} CSV files to process"

# Check if array task ID is within bounds
if [ $SLURM_ARRAY_TASK_ID -gt ${#INPUT_FILES[@]} ]; then
  echo "Array task ID $SLURM_ARRAY_TASK_ID exceeds number of files (${#INPUT_FILES[@]}). Exiting."
  exit 0
fi

# Get the file for this array task (array is 1-indexed, bash arrays are 0-indexed)
INPUT_FILE="${INPUT_FILES[$((SLURM_ARRAY_TASK_ID-1))]}"
echo "Processing file: $INPUT_FILE"

# Load environment
module load python/3.11.5
source /home/smacieje/myenv/bin/activate

# Create unique output directory for this array task
OUTPUT_DIR=~/api_output_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR" || exit

# Run the Genius lyrics script
python /home/smacieje/genius_lyrics_batch.py "$INPUT_FILE" \
    --delay 2.0 \
    --checkpoint-interval 25

echo "Array task $SLURM_ARRAY_TASK_ID completed at $(date)"