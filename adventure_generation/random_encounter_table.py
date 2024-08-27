class RandomEncounterTable:
    def __init__(self, detailed_regions, gpt4o_client):
        self.detailed_regions = detailed_regions
        self.gpt4o_client = gpt4o_client

    def generate_encounter_tables(self):
        encounter_tables = {}
        for region, details in self.detailed_regions.items():
            encounter_tables[region] = self.gpt4o_client.generate_random_encounters(region, details)
        return encounter_tables