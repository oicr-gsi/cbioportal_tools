#!/usr/bin/env bash

qsub 	-l h_vmem=32g \
 		-cwd \
 		-b y \
 		-m beas -M kunal.chandan@oicr.on.ca \
 		-N Janus_DCIS \
 		./runner.sh

# Memory
# Current Directory
# There is a script to be Run
# Email me
# Name
# Script

# Cores 		-pe smp 4 \