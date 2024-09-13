import sys # graceful exit option
import os # cause files
import json # I use too much
import random # for dice rolls
import threading, queue # for processing multiple jobs at once.
from adventure_generation.map_analyzer import MapAnalyzer # A special GPT-only feature (for now)
from adventure_generation.context_extractor import ContextExtractor # 
from adventure_generation.world_builder import WorldBuilder # does all the work
from adventure_generation.gpt4o_client import GPT4oClient # for money runs
from adventure_generation.ollama_client import ollamaClient # for local runs
#from adventure_generation.ollama_openai_client import ollamaClient # uses openai compatiblity.

# By default, I want to use GPT as little as possible despite gpt4o-mini being 
# extremely affordable. While testing, I will use ollama when possible.
global USING_MONEY
USING_MONEY = True
if "AC_USE_MONEY" in os.environ:
    USING_MONEY=os.getenv("AC_USE_MONEY")

# Do not generate image outputs
global CREATE_IMAGES
CREATE_IMAGES=True
if "AC_CREATE_IMAGES" in os.environ:
    CREATE_IMAGES=os.getenv("AC_CREATE_IMAGES")

global DEBUG
DEBUG=False
if "AC_DEBUG" in os.environ:
    DEBUG=os.getenv("AC_DEBUG")
    
    
print(f"""
-----------------------
GPT MODE*: {USING_MONEY}
CREATING IMAGES: {CREATE_IMAGES}
DEBUG MODE: {DEBUG}

* As of now, GPT is still required for map reading.
-----------------------
""")

def world_builder_task(context, region, llms, output_queue):
    # This starts the region development chain. This looks like:
    # 1. Describe the region in generalized detail
    # 2. Create each new location and describe it in detail
    # 3. Create each new character and describe them in detail
    # 4. Create a custom encounter table of random events for this region
    # 5. Create a minor side quest that connect characters and locations.
    
    print(f" - Starting thread for region: {region['LocationName']}")
    
    if USING_MONEY == True:
        world_builder = WorldBuilder(context, region, llms[0])
    else:
        world_builder = WorldBuilder(context, region, llms[1])
        
    built = world_builder.region_development_chain()
    
    # save waypoint with all json for review
    expanded_world_json_path = 'output/json_outputs/expanded_world_waypoint1.json'
    with open(expanded_world_json_path, 'w') as file:
        json.dump(built, file, indent=4)
    
    if CREATE_IMAGES == True:
        if USING_MONEY == True:
            built = world_builder.region_illustration_chain(llms[0])
        else:
            built = world_builder.region_illustration_chain_sd(llms[1])
    
        # save waypoint with images
        expanded_world_json_path = 'output/json_outputs/expanded_world_waypoint2.json'
        with open(expanded_world_json_path, 'w') as file:
            json.dump(built, file, indent=4)
    
    output_queue.put(built)
    
def world_builder_runner(context_extractor, world, llms):

    print("Creating a new world...")
    # Start Rolling for a random number of characters and locations in each region
    for region in world['regions']:
        
    # For each region, roll dice to determine the number of characters and locations need to be generated.
        if region['LocationType'] == 'bigTown':
            region['num_locations'] = random.randint(4, 10)
            region['num_characters'] = random.randint(4, 10)
            region['quests'] = random.randint(1, 6)
        elif region['LocationType'] == 'smallTown':
            region['num_locations'] = random.randint(2, 6)
            region['num_characters'] = random.randint(2, 6)
            region['quests'] = random.randint(1, 2)
        elif region['LocationType'] == 'other' or region['LocationType'] == 'NaturalFeature':
            region['num_locations'] = random.randint(1, 2)
            region['num_characters'] = random.randint(1, 4)
            region['quests'] = random.randint(1, 4)
            
        # DEBUG: Let's do this the right way
        
        if DEBUG is True:
            region['num_locations'] = 1
            region['num_characters'] = 1
            region['quests'] = 1
        
    # Warn the user about the number of queries
    print(f"Warning: about to perform 'very many' API calls. Generally more than 100 per map location. Please confirm if this is okay.")
    if USING_MONEY == True:
        print(f"Warning: All queries will use OpenAI GPT 4o, 4o-mini, 3.5-turbo, and DALL-E 3.")
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
    
    # We are giving the worker the context_extractor object, along with our chosen llm model
    # TODO: review how the LLM logic is used. We might only need to do this once.
    def worker():
        while not region_queue.empty():
            region = region_queue.get()
            world_builder_task(context_extractor, region, llms, output_queue)
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
    expanded_world_json_path = 'output/json_outputs/expanded_world.json'
    with open(expanded_world_json_path, 'w') as file:
        json.dump(world, file, indent=4)

def main(prompt_file, map_image, settings):
    # Initialize LLM clients (both)
    gpt4o_client = GPT4oClient()
    ollama_client=None
    if not USING_MONEY:
        ollama_client = ollamaClient()
        
    llms = [ gpt4o_client, ollama_client]
        
    # Extract context from the prompt file
    print("- reading the context file")
    context_extractor = ContextExtractor(prompt_file, map_image, settings)
    
    # Check if the output directory exists, if not, create it
    input_directory = 'input'
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)
    
    # Check if the output directory exists, if not, create it
    output_directory = 'output'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Check to see if base map description json file exists
    json_output_path = 'output/json_outputs/map_description.json'
    if os.path.exists(json_output_path):
        # Read JSON file
        print("- reading existing map description")
        with open(json_output_path, 'r') as file:
            world = json.load(file)
    else:
        # We use GPT-4o to analyze the map 
        # I couldn't get llava to read any of the text on my sample maps
        print(f"- studying the map with GPT4o: {context_extractor.get_input_imagepath()}")
        map_analyzer = MapAnalyzer(
            context_extractor.get_input_imagepath(),
            gpt4o_client)
        
        # This is so cool
        world = map_analyzer.identify_regions()

    # But basically, load the old world file, or createa  new one. 
    expanded_world_json_path = 'output/json_outputs/expanded_world.json'
    if os.path.exists(expanded_world_json_path):
        print("Existing world found. Do you want to use the existing world (option 1), or create a new one (option 2)?")
        user_option = input("Enter option number: ")
        if user_option == '1':
            print("Using the existing world.")
            with open(expanded_world_json_path, 'r') as file:
                world = json.load(file)
        elif user_option == '2':
            world=world_builder_runner(context_extractor, world, llms)
        else:
            print("Invalid input. Stopping.")
            sys.exit(1)
    else:
        world=world_builder_runner(context_extractor, world, llms)
                
    # Create a output directory and run document generator
    # Create output directory if it doesn't exist
    story_output_dir = 'output/story_html'
    if not os.path.exists(story_output_dir):
        os.makedirs(story_output_dir)
        
    # Run DocumentGenerator
    from adventure_generation.document_generator import DocumentGenerator
    print("Generating docs")
    template_dir = 'adventure_generation/templates'  # Directory where your HTML templates are stored
    document_generator = DocumentGenerator(expanded_world_json_path, template_dir, story_output_dir)
    document_generator.generate_html()
    
    # remove waypoint files
    waypoint_files = ['output/json_outputs/expanded_world_waypoint1.json', 'output/json_outputs/expanded_world_waypoint2.json']
    for waypoint in waypoint_files:
        if os.path.exists(waypoint):
            os.remove(waypoint)
    
    
    print("World generation complete!")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python main.py <prompt_file> <map_image> <settings.json>")
        sys.exit(1)
    
    prompt_file = sys.argv[1]
    map_image = sys.argv[2]
    settings = sys.argv[3]
    main(prompt_file, map_image, settings)