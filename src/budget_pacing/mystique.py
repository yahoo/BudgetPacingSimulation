from pacing_system_interface import PacingSystemInterface


class MystiqueTrackedCampaigns:
    def __init__(self, daily_budget):
        self.daily_budget = daily_budget
        self.spend = [(0, 0)]   # each entry is the current timestamp and the spend reported from the previous iteration

    def update_spend(self, timestamp, spend):
        self.spend.append((timestamp, spend))


class MystiqueImpl(PacingSystemInterface):
    def __init__(self):
        self.campaigns = {}     # a dict containing campaign id as key and MystiqueTrackedCampaigns instance as val

    def add_campaign(self, campaign):
        campaign_id = campaign.id
        daily_budget = campaign.daily_budget
        if campaign_id not in self.campaigns.keys():
            self.campaigns[campaign_id] = MystiqueTrackedCampaigns(daily_budget)

    def update_campaign_spend(self, timestamp, campaign_id, spend_since_last_run):
        if campaign_id in self.campaigns.keys():
            self.campaigns[campaign_id].update_spend(timestamp, spend_since_last_run)

    def get_pacing_signal(self, campaign_id):
        pass
