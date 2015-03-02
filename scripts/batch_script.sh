#!/bin/bash
#PBS -l nodes=1:ppn=4
#PBS -l walltime=4:00:0
#das eigentliche script darf erst nach PBS Kommandos beginnen und die
#PBS Kommandos sollten auch nicht durch Kommentare unterbrochen werden

#cd $PBS_O_WORKDIR
#
#echo $PBS_O_WORKDIR
echo "----------------------------------------------"
echo "start"
echo "----------------------------------------------"

#python3 job.py 0 30&
#python3 job.py 30 61&
python3 job.py 0 250&
python3 job.py 250 501&
#python job.py 500 750&
#python job.py 750 1000&
wait

echo "----------------------------------------------"
echo "done"
echo "----------------------------------------------"

