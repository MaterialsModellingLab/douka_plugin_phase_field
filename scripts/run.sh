#!/usr/bin/env bash
# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

set -e

function job_executor() {
  local cores=$1
  local N=$2
  local threads_per_proc=$3
  local job_func=$4

  local used_threads=0
  declare -a pids=()
  declare -a pid_threads=()

  for (( i=0; i<N; i++ )); do
    while (( used_threads + threads_per_proc > cores )); do
      wait -n
      used_threads=$(( used_threads - pid_threads[0] ))

      pids=("${pids[@]:1}")
      pid_threads=("${pid_threads[@]:1}")
    done

    ( OMP_NUM_THREADS=$threads_per_proc $job_func "$i" ) &
    pid=$!
    pids+=($pid)
    pid_threads+=($threads_per_proc)
    used_threads=$(( used_threads + threads_per_proc ))
  done

  for pid in "${pids[@]}"; do
    wait "$pid"
  done
}

# Resource detection
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  phys_cores=$(lscpu | awk '/^Core\(s\) per socket:/ {core=$4} /^Socket\(s\):/ {print core * $2}')
  logi_cores=$(lscpu | awk '/^CPU\(s\):/ {print $2}')
elif [[ "$OSTYPE" == "darwin"* ]]; then
  phys_cores=$(sysctl -n hw.physicalcpu)
  logi_cores=$(sysctl -n hw.logicalcpu)
else
  echo "Unsupported OS: $OSTYPE" >&2
  exit 1
fi


# Main script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE="${SCRIPT_DIR}/.."
NAME="phase_field"

cd ${BASE}

if [ ! -d "output/obs" ]; then
  echo "Observation does not exist. Run obsgen.sh first."
  exit 1
fi

if [ ! -d "output/init" ]; then
  echo "Initial state does not exist. Run init.sh first."
  exit 1
fi

# If previous state exists, archive it
if [ -d "output/state" ]; then
  tar -zcf output/state$(date +%Y%m%d_%H%M%S).tar.gz -C output state
  rm -rf output/state/*
else
  mkdir -p output/state
fi

# Copy initial state
cp output/init/* output/state

# T is file number - 1 of ./output/obs directory
T=$(ls output/obs/${NAME}*.json | wc -l | awk '{print $1-1}')
# N is file number of ./output/init directory
N=$(ls output/init/${NAME}*.json | wc -l)

# Tuned parameters
prediction_threads_per_proc=2

for (( t = 0; t < T; t++)); do
  function predict_job() {
    local i=$1
    douka predict \
      --state        output/state/$(printf ${NAME}_%04d_%06d_%06d.json $i $t $t) \
      --param        output/param/${NAME}.predict.json \
      --plugin       ${NAME} \
      --plugin_param param/${NAME}.json \
      --output       output/state \
      >> output/${NAME}.log
  }

  echo "Predict ${t}"
  job_executor $phys_cores $N $prediction_threads_per_proc predict_job

  echo "Filter  ${t}"
  OMP_NUM_THREADS=$(( $phys_cores )) \
  douka filter \
      --state  output/state/${NAME}_%04d_$(printf '%06d' $((t + 1)))_$(printf '%06d' $t).json \
      --param  output/param/${NAME}.filter-enkf.json \
      --obs    output/obs/${NAME}_obs_$(printf '%06d' $((t + 1))).json \
      --output output/state \
      >> output/${NAME}.log
done
