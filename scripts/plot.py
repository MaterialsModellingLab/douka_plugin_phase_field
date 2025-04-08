#!/usr/bin/env python3
# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
from pathlib import Path

import celluloid
import matplotlib.pyplot as plt
import numpy as np


def read_json(filename: str) -> dict:
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def get_data(state_dir: Path, param: dict) -> dict:
    results = {}
    names = param["targets"].keys()
    for name in names:
        results[name] = {"all": {}, "mean": [], "std": []}
        for n in range(param["N"]):
            results[name]["all"][n] = []
    tmp = {}
    for t in range(0, param["T"] + 1):
        for name in names:
            tmp[name] = []
        for n in range(param["N"]):
            filename = "{}_{:04}_{:06}_{:06}.json".format(param["name"], n, t, t)
            if not (state_dir / filename).exists():
                continue
            data = read_json(state_dir / filename)
            for name in names:
                tmp[name].append(data["x"][param["targets"][name]["key"]])
        for name in names:
            if not tmp[name]:
                continue
            for n in range(param["N"]):
                results[name]["all"][n].append(np.array(tmp[name][n]))
            results[name]["mean"].append(np.array(tmp[name]).mean())
            results[name]["std"].append(np.array(tmp[name]).std())
    return results


def plot(output_dir: Path, results: dict, param: dict, show: bool = False):
    for name in results.keys():
        info = param["targets"][name]
        result = results[name]
        t_list = np.linspace(0.0, param["T"] * param["dt"], len(result["mean"]))
        fig = plt.figure()
        ax = fig.subplots(1)
        ax.hlines(
            info["truth"],
            t_list[0],
            t_list[-1],
            color="red",
            label="Ground Truth",
        )
        for value in result["all"].values():
            ax.plot(t_list, value, color=info["color"], alpha=0.2)
        ax.plot(t_list, result["mean"], color=info["color"], label="Estimated")
        ax.set_ylabel(info["label"])
        ax.set_xlabel("time [ns]")
        ax.legend()
        ax.set_xticks(t_list[::2])
        ax.set_xlim(0.0, param["T"] * param["dt"])
        plt.savefig(output_dir / "{}.png".format(name))
    if show:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Plot the estimation result")
    parser.add_argument("--show", action="store_true", help="Show the plot")
    parser.add_argument("--obs", action="store_true", help="Show the observation plot")

    args = parser.parse_args()

    base = Path(__file__).parent.parent.resolve()
    state_dir = base / "output" / "state"
    obs_dir = base / "output" / "obs"
    init_dir = base / "output" / "init"

    N = len(list(init_dir.glob("*.json")))
    T = len(list(obs_dir.glob("*.json"))) - 1
    to_ns = 1.0e9
    dt = 3.705e-12 * 500 * to_ns
    epsilon_c = 0.018
    epsilon_k = 0.13
    field_size = 80

    param = {
        "name": "phase_field",
        "N": N,
        "T": T,
        "dt": dt,
    }

    if args.obs:
        fig, (ax) = plt.subplots(1)
        camera = celluloid.Camera(fig)
        for i in range(T + 1):
            data = np.array(
                read_json(obs_dir / "{}_obs_{:06}.json".format(param["name"], i))["y"]
            ).reshape([field_size, field_size])
            ax.imshow(data, interpolation="nearest")
            camera.snap()
        anim = camera.animate()
        anim.save(obs_dir / "{}.mp4".format(param["name"]))
        if args.show:
            plt.show()
    else:
        param["targets"] = {
            "epsilon_c": {
                "key": -2,
                "label": r"$\varepsilon_c$",
                "truth": epsilon_c,
                "color": "tab:cyan",
            },
            "epsilon_k": {
                "key": -1,
                "label": r"$\varepsilon_k$",
                "truth": epsilon_k,
                "color": "tab:orange",
            },
        }

        results = get_data(state_dir, param)
        for result in results.values():
            if not result["mean"] or not result["std"]:
                exit("No data found")
        plot(output_dir=state_dir, results=results, param=param, show=args.show)


if __name__ == "__main__":
    main()
