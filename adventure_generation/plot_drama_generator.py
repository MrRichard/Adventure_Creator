class PlotDramaGenerator:
    def __init__(self, world_description, gpt4o_client):
        self.world_description = world_description
        self.gpt4o_client = gpt4o_client

    def generate_plot_drama(self):
        plot_drama = self.gpt4o_client.generate_plot_drama(self.world_description)
        return plot_drama