import src.system.budget_pacing.mystique.mystique_constants as mystique_constants
import src.system.budget_pacing.mystique.mystique_utils as utils
from src.system.clock import Clock


class MystiqueTrackedCampaign:
    def __init__(self, daily_budget: float):
        self.daily_budget = daily_budget
        self.ps = mystique_constants.pacing_signal_for_initialization
        self.previous_ps = mystique_constants.pacing_signal_for_initialization
        self.last_positive_ps = mystique_constants.pacing_signal_for_initialization
        self.ps_history = []  # list of lists for each day, each entry in arr is the calculated ps and the location is number of iteration
        self.today_ps = []    # each entry is the calculated PS, the location in the arr is the number of iteration
        self.spend_history = []   # list of lists for each day, each entry in arr is the spend and the location is number of iteration
        self.today_spend = []   # each entry is the spend reported from the previous iteration, the location in the arr is the number of iteration
        self.current_target_slope = []
        self.target_slope_history = []
        self.current_target_spend_curve = []
        self.target_spend_history = []
        self.sum_ps_below_threshold = 0
        self.count_ps_below_threshold = 0
        self.new_day_init(is_new_campaign=True)

    def new_day_init(self, is_new_campaign=False):
        # updating the PS values
        if is_new_campaign:
            if self.daily_budget > mystique_constants.min_daily_budget_for_high_initialization:
                self.ps = mystique_constants.max_ps
                self.previous_ps = mystique_constants.max_ps
                self.last_positive_ps = mystique_constants.max_ps
        self.previous_ps = self.last_positive_ps
        avg_ps_below_threshold = self.get_avg_daily_ps_below_threshold()
        if avg_ps_below_threshold != mystique_constants.ps_invalid_value:
            self.previous_ps = avg_ps_below_threshold
            self.last_positive_ps = avg_ps_below_threshold
        self.previous_ps = min(self.previous_ps, mystique_constants.max_ps)

        # updating the PS history arr and initializing today's PS arr
        if len(self.today_ps) > 0:
            self.ps_history.append(self.today_ps)
        self.today_ps = []

        # updating the spend history arr and initializing today's spend arr
        if len(self.today_spend) > 0:
            self.spend_history.append(self.today_spend)
        self.today_spend = []

        # initializing the average PS value below threshold metrics
        self.sum_ps_below_threshold = 0
        self.count_ps_below_threshold = 0

    def update_spend(self, spend: float):
        self.today_spend.append(spend)

    def update_pacing_signal(self, ps: float):
        """Because of the update of the average daily PS below threshold metrics, this must always be called after update_spend"""
        self.previous_ps = self.ps
        if self.ps > 0:
            self.last_positive_ps = self.ps
        self.ps = ps
        self.today_ps.append(ps)

        # updating the average daily PS below threshold metrics
        if self.get_today_spend() / self.daily_budget < mystique_constants.budget_spend_threshold:
            self.sum_ps_below_threshold += self.ps
            self.count_ps_below_threshold += 1

    def update_target_slope_curve(self, target_slope_curve: list[float]):
        if len(self.current_target_slope) > 0:
            self.target_slope_history.append(self.current_target_slope)
        self.current_target_slope = target_slope_curve

    def update_target_spend_curve(self, target_spend_curve: list[float]):
        if len(self.current_target_spend_curve) > 0:
            self.target_spend_history.append(self.current_target_spend_curve)
        self.current_target_spend_curve = target_spend_curve

    def get_spend_in_last_time_interval(self):
        return self.today_spend[-1]

    def get_today_spend(self):
        return sum(self.today_spend)

    def get_avg_daily_ps_below_threshold(self):
        """average PS value for all iterations where spend-to-budget ratio < mystique_constants.budget_spend_threshold"""
        if self.count_ps_below_threshold == 0:
            return mystique_constants.ps_invalid_value
        return self.sum_ps_below_threshold / self.count_ps_below_threshold

    def get_avg_daily_ps(self):
        return self.get_avg_daily_ps_below_threshold()

    def get_avg_hourly_ps(self):
        return utils.get_average_per_size(self.today_ps, mystique_constants.num_iterations_per_hour)
