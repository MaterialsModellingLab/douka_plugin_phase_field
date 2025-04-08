#!/usr/bin/env python3
# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
import math
import pathlib

import numpy as np


def field_init(radius=10) -> np.array:
    field = np.ones((field_size, field_size)) * -1.0
    for i in range(radius):
        for j in range(radius):
            if i**2.0 + j**2.0 <= radius**2.0:
                field[i][j] = 1.0
    return field.flatten()


def write_json(filename: str, obj: dict):
    if not output_path.exists():
        output_path.mkdir(parents=True)
    with open(output_path / filename, "w") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, separators=(",", ": "))
        print("Write {}".format(filename))


def write_obs_param():
    obj = {}
    obj["name"] = name
    obj["seed"] = seed
    obj["k"] = k
    obj["l"] = l
    obj["t"] = 10
    obj["x0"] = field_init().tolist() + [epsilon_c, epsilon_k]

    filename = "{}.obsgen.json".format(name)
    write_json(filename, obj)


def write_init_param():
    obj = {}
    obj["name"] = name
    obj["seed"] = seed
    obj["N"] = N
    obj["k"] = k
    obj["x0"] = field_init().tolist() + [epsilon_c, epsilon_k]
    obj["V0"] = np.zeros((l)).tolist() + [V_epsilon_c, V_epsilon_k]

    filename = "{}.init.json".format(name)
    write_json(filename, obj)


def write_predict_param():
    obj = {}
    obj["name"] = name
    obj["seed"] = seed
    obj["k"] = k
    obj["Q"] = (np.ones((l)) * Q_phi).tolist() + [Q_epsilon_c, Q_epsilon_k]
    filename = "{}.predict.json".format(name)
    write_json(filename, obj)


def write_filter_enkf_param():
    obj = {}
    obj["name"] = name
    obj["seed"] = seed
    obj["N"] = N
    obj["k"] = k
    obj["l"] = l
    obj["R"] = (np.ones((l)) * R).tolist()
    filename = "{}.filter-enkf.json".format(name)
    write_json(filename, obj)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate parameter files for phase field")
    parser.add_argument("--N", help="Number of ensemble", default=10, type=int)
    parser.add_argument("--seed", help="Random seed", default=1, type=int)
    parser.add_argument("--output", help="Output directory", default="output/param")
    args = parser.parse_args()

    N = args.N
    seed = args.seed

    base = pathlib.Path(__file__).parent.parent.resolve()
    param_path = base / "param"
    output_path = base / args.output

    # Data Assimilation Param
    name = "phase_field"

    # Phase field param
    with open(param_path / "{}.json".format(name), "r") as f:
        data = json.load(f)

    field_size = data["field_size"]
    epsilon_c = data["epsilon_c"]
    epsilon_k = data["epsilon_k"]

    k = field_size * field_size + 2
    l = field_size * field_size

    R = math.pow(1.0e-2, 2.0)

    Q_phi = math.pow(1.0e-4, 2.0)
    Q_epsilon_c = math.pow(1.0e-6, 2.0)
    Q_epsilon_k = math.pow(1.0e-6, 2.0)

    # Initial distribution of parameter
    V_epsilon_c = math.pow(4.0e-3, 2.0)
    V_epsilon_k = math.pow(1.0e-3, 2.0)

    write_obs_param()
    write_init_param()
    write_predict_param()
    write_filter_enkf_param()
