class RegionDetailer:
    def __init__(self, regions, gpt4o_client):
        self.regions = regions
        self.gpt4o_client = gpt4o_client

    def detail_regions(self):
        detailed_regions = {}
        for region in self.regions:
            detailed_regions[region] = self.gpt4o_client.generate_region_details(region)
        return detailed_regions
