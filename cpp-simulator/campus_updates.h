//Copyright [2020] [Indian Institute of Science, Bangalore & Tata Institute of Fundamental Research, Mumbai]
//SPDX-License-Identifier: Apache-2.0
#ifndef UPDATES_H_
#define UPDATES_H_

#include "campus_models.h"
#include <vector>

std::vector<agent> init_nodes_campus();

std::vector<Interaction_Space> init_interaction_spaces();

double update_interaction_spaces(agent& node, int cur_day);

double update_n_k(agent& node, int cur_day, Interaction_Space& i_space);

void update_interaction_space_lambda(std::vector<agent> nodes, std::vector<Interaction_Space>& i_spaces, int cur_day);

void update_individual_lambda(std::vector<agent>& nodes, std::vector<Interaction_Space>& i_spaces, int cur_day);

void assign_individual_campus(std::vector<agent>& nodes, std::vector<Interaction_Space>& interaction_space, int cur_day);

node_update_status update_infection(agent& node, int cur_time);

#endif
