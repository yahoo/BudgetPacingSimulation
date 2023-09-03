import src.configuration

default_unknown_value = -1
default_ps_value = 0
minimal_ps_value = 0.0001
num_hours_per_day = 24
num_iterations_per_day = src.configuration.num_iterations_per_day
percent_of_day_in_one_iteration = 1 / num_iterations_per_day
num_iterations_for_avg_daily_ps_below_threshold_reset = num_iterations_per_day - 3
num_iterations_per_hour = 60
pacing_signal_for_initialization = 0.0001
max_ps = 1
min_ps = 0
error_corresponding_to_max_correction = 0.25
max_ps_correction = 0.025
gradient_error_corresponding_to_max_correction = 1.5
max_ps_correction = 0.025
minimal_non_zero_ps_correction = 0.01
min_daily_budget_for_high_initialization = 10000
max_interval = num_iterations_per_day + 1.0
max_ps_correction_weight = 0.9
ps_correction_weight_factor = 0.2
budget_spend_threshold = 0.95
ps_invalid_value = -1
minutes_for_end_day_edge_case = 3

# field names for mystique's per-campaign statistics
FIELD_SPEND_HISTORY = 'spend_history'
FIELD_TARGET_SPEND_HISTORY = 'target_spend_history'
FIELD_TARGET_SLOPE_HISTORY = 'target_slope_history'
FIELD_PACING_SIGNAL_HISTORY = 'pacing_signal_history'
# field names for mystique's global statistics
FIELD_AVERAGE_NUM_BC_CAMPAIGNS = 'average_num_bc_campaigns'
FIELD_AVERAGE_NUM_NBC_CAMPAIGNS = 'average_num_nbc_campaigns'
