#!/bin/bash
#PBS -l nodes=1:ppn=1,pmem=32gb,pvmem=32gb
#PBS -l walltime=03:00:00
#PBS -N symbolic
#PBS -o /users/c/f/cfusting/job_logs
#PBS -e /users/c/f/cfusting/job_logs
#PBS -q shortq
export PYTHONPATH=$HOME/gp_mecl:$HOME/arctic-browing
cd $HOME/symbolic_results
source $HOME/arctic-browning/ml/symbolic.py -d $data -s $seed -n $name
