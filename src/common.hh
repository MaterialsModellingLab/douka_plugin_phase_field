/*
 * Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
 * SPDX-License-Identifier: Apache-2.0
 */

#include <algorithm>
#include <omp.h>
#include <phase_field/phase_field.hh>

namespace douka_plugin {
inline void state2phi(const std::vector<double> &state, const std::vector<double> &noise,
                      phase_field::Field2D &phi) {
  const std::size_t y_size = phi.shape()[0];
  const std::size_t x_size = phi.shape()[1];
#pragma omp parallel for
  for (std::size_t y = 0; y < y_size; ++y) {
#pragma omp parallel for
    for (std::size_t x = 0; x < x_size; ++x) {
      const double tmp = state[y * x_size + x] + noise[y * x_size + x];
      phi[y][x] = std::clamp(tmp, phase_field::FieldState::liquid, phase_field::FieldState::solid);
    }
  }
}

inline void phi2state(const phase_field::Field2D &phi, std::vector<double> &state) {
  const std::size_t y_size = phi.shape()[0];
  const std::size_t x_size = phi.shape()[1];
#pragma omp parallel for
  for (std::size_t y = 0; y < y_size; ++y) {
#pragma omp parallel for
    for (std::size_t x = 0; x < x_size; ++x) {
      state[y * x_size + x] = phi[y][x];
    }
  }
}
} // namespace douka_plugin
