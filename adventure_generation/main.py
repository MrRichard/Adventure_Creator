import sys
import os, json
from adventure_generation.map_analyzer import MapAnalyzer
from adventure_generation.context_extractor import ContextExtractor
from adventure_generation.world_builder import WorldBuilder
from adventure_generation.document_generator import DocumentGenerator
# from plot_drama_generator import PlotDramaGenerator
# from region_detailer import RegionDetailer
# from quest_line_generator import QuestLineGenerator
# from random_encounter_table import RandomEncounterTable
from adventure_generation.gpt4o_client import GPT4oClient

def main(prompt_file, map_image):
    # Initialize GPT-4o client
    gpt4o_client = GPT4oClient()

    json_output_path = 'json_outputs/map_description.json'
    if os.path.exists(json_output_path):
        # Read JSON file
        print("- reading existing map description")
        with open(json_output_path, 'r') as file:
            world = json.load(file)
    else:
        # Analyze the map if JSON file doesn't exist
        print("- studying the map")
        map_analyzer = MapAnalyzer(map_image)
        world = map_analyzer.identify_regions()

    # Extract context from the prompt file
    print("- reading the context file")
    context_extractor = ContextExtractor(prompt_file)
    context = context_extractor.extract_context()

    # Build the world
    # WorldBuilder class now parses the json file and iterates through it.
    # TODO: world builder should also render the images
    expanded_json_output_path = 'json_outputs/expanded_world.json'
    if os.path.exists(expanded_json_output_path):
        # Read expanded JSON file
        print("- reading existing expanded world description")
        with open(expanded_json_output_path, 'r') as file:
            world = json.load(file)
    else:
        # Build the world if expanded JSON file doesn't exist
        world_builder = WorldBuilder(context, world, gpt4o_client)
        world = world_builder.build_world()
        
    # # Generate the Players document
    document_generator = DocumentGenerator(world)
    document_generator.generate_document()

    # # Generate the overarching plot drama
    # plot_drama_generator = PlotDramaGenerator(world_description, gpt4o_client)
    # plot_drama = plot_drama_generator.generate_plot_drama()

    # # Detail each region
    # region_detailer = RegionDetailer(regions, gpt4o_client)
    # detailed_regions = region_detailer.detail_regions()

    # # Generate quest lines
    # quest_line_generator = QuestLineGenerator(detailed_regions, plot_drama, gpt4o_client)
    # quest_lines = quest_line_generator.generate_quest_lines()

    # # Generate random encounter tables
    # random_encounter_table = RandomEncounterTable(detailed_regions, gpt4o_client)
    # encounter_tables = random_encounter_table.generate_encounter_tables()

    print("Adventure generation complete!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <prompt_file> <map_image>")
        sys.exit(1)
    
    prompt_file = sys.argv[1]
    map_image = sys.argv[2]
    main(prompt_file, map_image)