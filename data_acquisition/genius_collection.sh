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
  echo "ERROR: No input CSV file provided. Usage: sbatch genius_collection.sh ./musicbrainz_tracks_2020.csv"
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
OUTPUT_DIR=~/api_output_${SLURM_JOB_ID}
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR" || exit

# Run the Genius lyrics script
python /home/smacieje/genius_lyrics_batch.py "$SLURM_SUBMIT_DIR/$INPUT_FILE" \
    --delay 2.0 \
    --checkpoint-interval 25

echo "Job completed at $(date)"