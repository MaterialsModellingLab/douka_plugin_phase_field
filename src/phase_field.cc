/*
 * Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
 * SPDX-License-Identifier: Apache-2.0
 */

#include "phase_field.hh"
#include "common.hh"
#include <fstream>

namespace douka_plugin {
PhaseField::PhaseField() { this->param = phase_field::get_pure_ni_param(); }

bool PhaseField::set_option(const std::string &opt_file) {
  this->param = phase_field::get_pure_ni_param();
  this->param.lambda = 16.0;
  this->param.u = -0.2;
  this->param.setup();
  try {
    std::ifstream f{opt_file};
    this->plugin_param = nlohmann::json::parse(f);
  } catch (const std::ifstream::failure &e) {
    std::clog << e.what() << std::endl;
    return false;
  } catch (const nlohmann::json::exception &e) {
    std::clog << e.what() << std::endl;
    return false;
  }
  return this->plugin_param.validate();
}

bool PhaseField::predict(std::vector<double> &state, const std::vector<double> &noise) {
  static auto phi = phase_field::Field2D::fromShape(
      {this->plugin_param.field_size, this->plugin_param.field_size});
  static auto phi_next = phase_field::Field2D::like(phi);

  // Merge noise and state
  state2phi(state, noise, phi);

  // Copy state to phi
  this->param.epsilon_c = *(std::prev(state.end(), 2)) + *(std::prev(noise.end(), 2));
  this->param.epsilon_k = *(std::prev(state.end(), 1)) + *(std::prev(noise.end(), 1));

  phase_field::PhaseField2D system{this->param};
  for (std::size_t i = 0; i < this->plugin_param.step; ++i) {
    system.predict(phi, phi_next);
    phi = phi_next;
  }

  phi2state(phi, state);

  return true;
}
} // namespace douka_plugin


#include <douka/plugin_register_macro.hh>
DOUKA_PLUGIN_REGISTER(douka_plugin::PhaseField)
