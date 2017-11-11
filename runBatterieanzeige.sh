#!/bin/sh

PWD=$(pwd)
RUNPROGRAMM=$(ls -la ${pwd} | grep -c 'mainWindow.pid')

#echo "Test: ${RUNPROGRAMM}"

if [ ${RUNPROGRAMM} -gt 0 ]
then
	echo "Programm ist schon gestartet!!!"
else
	echo "Start Programm ..."
	python ${PWD}/mainWindow.py & \
	echo $! > ${PWD}/mainWindow.pid
fi

