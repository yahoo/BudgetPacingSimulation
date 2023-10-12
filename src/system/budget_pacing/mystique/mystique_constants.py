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
minimal_non_zero_ps_correction = 0.01
min_daily_budget_for_high_initialization = 10000
max_interval = num_iterations_per_day + 1.0
max_ps_correction_weight = 0.9
ps_correction_weight_factor = 0.2
budget_spend_threshold = 0.95
ps_invalid_value = -1
minutes_for_end_day_edge_case = 3
ps_threshold_for_bc_campaigns = 0.95  # average ps value above which a campaign is defined as budget constrained (BC)

# field names for mystique's per-campaign statistics
FIELD_SPEND_HISTORY = 'Spend History'
FIELD_TARGET_SPEND_HISTORY = 'Target Spend History'
FIELD_TARGET_SLOPE_HISTORY = 'Target Slope History'
FIELD_PACING_SIGNAL_HISTORY = 'Pacing Signal History'
# field names for mystique's global statistics
FIELD_NUM_BC_CAMPAIGNS = 'Number of BC Campaigns'
FIELD_NUM_NBC_CAMPAIGNS = 'Number of NBC Campaigns'
