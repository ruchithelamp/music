#!/bin/bash

#SBATCH --job-name=musicbrainz_array
#SBATCH --account=siads696s25_class
#SBATCH --mail-user=smacieje@umich.edu
#SBATCH --mail-type=ARRAY_TASKS
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=8G
#SBATCH --time=8:00:00
#SBATCH --partition=standard
#SBATCH --array=0-45
#SBATCH --output=musicbrainz_%A_%a.out
#SBATCH --error=musicbrainz_%A_%a.err

echo "Job started on $(date)"
echo "Running on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"
echo "Array Task ID: $SLURM_ARRAY_TASK_ID"
echo "Working directory: $(pwd)"

module load python/3.11.5

# Replace this with your actual venv path
source /home/smacieje/myenv/bin/activate

# === CONFIGURATION ===
YEAR=2009
CHUNK_SIZE=1000
OFFSET=$((CHUNK_SIZE * SLURM_ARRAY_TASK_ID))
OUTPUT_DIR=~/api_output_${SLURM_JOB_ID}
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "Starting MusicBrainz collection for YEAR=$YEAR, OFFSET=$OFFSET, CHUNK_SIZE=$CHUNK_SIZE"

python /home/smacieje/musicbrainz_batch2.py $YEAR \
    --offset $OFFSET \
    --max-releases $CHUNK_SIZE \
    --output-dir "$OUTPUT_DIR"

echo "Chunk completed on $(date)"
