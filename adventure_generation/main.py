import sys
import os, json
from adventure_generation.map_analyzer import MapAnalyzer
from adventure_generation.context_extractor import ContextExtractor
from adventure_generation.world_builder import WorldBuilder
#from adventure_generation.document_generator import DocumentGenerator
# from plot_drama_generator import PlotDramaGenerator
# from region_detailer import RegionDetailer
# from quest_line_generator import QuestLineGenerator
# from random_encounter_table import RandomEncounterTable
from adventure_generation.gpt4o_client import GPT4oClient
from adventure_generation.ollama_client import ollamaClient
import random

import threading, queue

# By default, I want to use GPT as little as possible despite gpt4o-mini being 
# extremely affordable. While testing, I will use ollama when possible.
USING_MONEY = True

def world_builder_task(context, region, llm_client, output_queue):
    
    print(f" - starting thread for region: {region['LocationName']}")
    world_builder = WorldBuilder(context, region, llm_client)
    
    # This starts the region development chain. This looks like:
    # 1. Describe the region in generalized detail
    # 2. Create each new location and describe it in detail
    # 3. Create each new character and describe them in detail
    # 4. Create a custom encounter table of random events for this region
    # 5. Create a minor side quest that connect characters and locations.
    
    built = world_builder.region_development_chain()
    output_queue.put(built)

def main(prompt_file, map_image):
    # Initialize GPT-4o client
    gpt4o_client = GPT4oClient()
    ollama_client = ollamaClient()

    # Check to see if base map description json file exists
    json_output_path = 'json_outputs/map_description.json'
    if os.path.exists(json_output_path):
        # Read JSON file
        print("- reading existing map description")
        with open(json_output_path, 'r') as file:
            world = json.load(file)
    else:
        # We use GPT-4o to analyze the map 
        # I couldn't get llava to read any of the text on my sample maps
        print("- studying the map with GPT4o")
        map_analyzer = MapAnalyzer(map_image, gpt4o_client)
        world = map_analyzer.identify_regions()

    # Extract context from the prompt file
    print("- reading the context file")
    context_extractor = ContextExtractor(prompt_file)
    context = context_extractor.extract_context()

    # Start Rolling for a random number of characters and locations in each region
    for region in world['regions']:
        
    # For each region, roll dice to determine the number of characters and locations need to be generated.
        if region['LocationType'] == 'bigTown':
            region['num_locations'] = random.randint(1, 8)
            region['num_characters'] = random.randint(1, 10)
            region['quests'] = random.randint(1, 6)
        elif region['LocationType'] == 'smallTown':
            region['num_locations'] = random.randint(1, 4)
            region['num_characters'] = random.randint(1, 6)
            region['quests'] = random.randint(1, 2)
        elif region['LocationType'] == 'other' or region['LocationType'] == 'NaturalFeature':
            region['num_locations'] = random.randint(1, 2)
            region['num_characters'] = random.randint(1, 4)
            region['quests'] = random.randint(1, 4)
            
    # Perform a rough calculation
    # TODO: This logic is broken. I would like to make this more accurate. 
    total_characters_locations = sum([region['num_locations'] + region['num_characters'] for region in world['regions']])
    query_count = total_characters_locations * 5 + len(world['regions'])

    # Warn the user about the number of queries
    print(f"Warning: about to perform {query_count} queries. Please confirm if this is okay.")
    if USING_MONEY == True:
        print(f"Warning: All queries will use OpenAI GPT 4o or 4o-mini")
    else:
        print(f"You are running in FREE MODE and will use a local ollama server")
    user_confirmation = input("Enter 'yes' to proceed, or any other key to stop: ")
    
    if user_confirmation.lower() != 'yes':
        print("Process stopped by user.")
        sys.exit(0)

    # If the user has confirmed, the remaining code will proceed as written
    # Create a queue to manage threading
    region_queue = queue.Queue()
    output_queue = queue.Queue()
    
    for region in world['regions']:
        region_queue.put(region)

    threads = []
    max_threads = 3
    
    def worker():
        while not region_queue.empty():
            region = region_queue.get()
            if USING_MONEY:
                world_builder_task(context, region, gpt4o_client, output_queue)
            else:
                world_builder_task(context, region, ollama_client, output_queue)
            region_queue.task_done()
            
    for i in range(max_threads):
        thread = threading.Thread(target=worker)
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Collect results from the output queue
    built_world = []
    while not output_queue.empty():
        built_world.append(output_queue.get())

    # Update the world with the built regions
    world['regions'] = built_world
    
    # Save the updated world as a new JSON file
    expanded_world_json_path = 'json_outputs/expanded_world.json'
    with open(expanded_world_json_path, 'w') as file:
        json.dump(world, file, indent=4)
    
    print("Adventure generation complete!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <prompt_file> <map_image>")
        sys.exit(1)
    
    prompt_file = sys.argv[1]
    map_image = sys.argv[2]
    main(prompt_file, map_image)