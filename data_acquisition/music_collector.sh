#!/bin/bash

#SBATCH --job-name=music_data_fetcher
#SBATCH --account=siads696s25_class
#SBATCH --mail-user=smacieje@umich.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=2g
#SBATCH --time=6:00:00
#SBATCH --partition=standard
#SBATCH --output=music_fetcher_%j.log
#SBATCH --error=music_fetcher_%j.err

echo "Job started on $(date)"
echo "Running on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"
echo "Working directory: $(pwd)"

module load python/3.11.5

#making your directory, if the data is not too large, use your home dir
mkdir -p ~/api_output_${SLURM_JOB_ID}
cd ~/api_output_${SLURM_JOB_ID}

# Activate your virtual environment here
source /home/smacieje/myenv/bin/activate

echo "Starting API calls..."

python /home/smacieje/music_data_fetcher.py

echo "API calls completed on $(date)"
echo "Job finished on $(date)"


