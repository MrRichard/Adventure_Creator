class QuestLineGenerator:
    def __init__(self, detailed_regions, plot_drama, gpt4o_client):
        self.detailed_regions = detailed_regions
        self.plot_drama = plot_drama
        self.gpt4o_client = gpt4o_client

    def generate_quest_lines(self):
        quest_lines = {}
        for region, details in self.detailed_regions.items():
            quest_lines[region] = self.gpt4o_client.generate_quest_lines(region, details, self.plot_drama)
        return quest_lines