/*
 * Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef __DOUKA_PLUGIN_PHASE_FIELD__
#define __DOUKA_PLUGIN_PHASE_FIELD__

#include <douka/plugin_interface.hh>
#include <phase_field/phase_field.hh>
#include <string>

namespace douka_plugin {
struct Param {
  std::size_t field_size;
  std::size_t step;

  NLOHMANN_DEFINE_TYPE_INTRUSIVE(Param, field_size, step);

  bool validate() const {
    if (field_size < 1) {
      std::clog << "field_size must be greater than 0" << std::endl;
      return false;
    }

    if (step < 1) {
      std::clog << "step must be greater than 0" << std::endl;
      return false;
    }
    return true;
  }
};

class PhaseField : public douka::PluginInterface {
public:
  const std::string name = "phase_field";
  phase_field::Param param;
  Param plugin_param = {80, 500};

public:
  PhaseField();
  ~PhaseField() = default;
  bool set_option(const std::string &opt_file) override;
  bool predict(std::vector<double> &state, const std::vector<double> &noise) override;
};
} // namespace douka_plugin

#endif
