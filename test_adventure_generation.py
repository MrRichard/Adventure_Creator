import os
from adventure_generation.context_extractor import ContextExtractor
from adventure_generation.map_analyzer import MapAnalyzer
from adventure_generation.region_detailer import RegionDetailer
from adventure_generation.gpt4o_client import GPT4oClient

# TODO: Update this file

def test_adventure_generation():
    # Set up paths
    prompt_file_path = "sample_inputs/ariel_coast.txt"
    map_image_path = "sample_inputs/ariel_coast.jpg"

    # Extract context
    context_extractor = ContextExtractor(prompt_file_path)
    context = context_extractor.extract_context()

    # Analyze map
    map_analyzer = MapAnalyzer(map_image_path)
    landscape_description = map_analyzer.identify_regions()

    # Generate world description
    gpt4o_client = GPT4oClient()
    regions = ["Region1", "Region2"]  # Example regions
    world_description = gpt4o_client.generate_world_description(context, regions)

    # Generate plot drama
    plot_drama = gpt4o_client.generate_plot_drama(world_description)

    # Detail regions
    region_detailer = RegionDetailer(regions, gpt4o_client)
    detailed_regions = region_detailer.detail_regions()

    # Print results
    print("Context:", context)
    print("Landscape Description:", landscape_description)
    print("World Description:", world_description)
    print("Plot Drama:", plot_drama)
    print("Detailed Regions:", detailed_regions)

if __name__ == "__main__":
    test_adventure_generation()