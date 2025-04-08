#!/usr/bin/env bash
# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE="${SCRIPT_DIR}/.."

cd $BASE

if [ ! -d "output/param" ]; then
  echo "Parameter does not exist. Run paramgen.py first."
  exit 1
fi

douka init \
  --param  output/param/phase_field.init.json \
  --output output/init \
  --force
