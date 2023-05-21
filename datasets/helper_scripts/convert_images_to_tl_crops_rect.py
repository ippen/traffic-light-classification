import json
from PIL import Image
import os
import threading


def determine_class(attributes):
    pictogram = attributes['pictogram']
    state = attributes['state']
    direction = attributes['direction']
    reflection = attributes['reflection']
    occlusion = attributes['occlusion']
    
    if ((pictogram == "circle" or pictogram=="arrow_straight" or pictogram=="arrow_left" or pictogram=="arrow_right") and
        (state == "red" or state == "yellow" or state == "red_yellow" or state == "green" or state == "off") and
        (direction == "front") and
        (reflection == "not_reflected") and
        (occlusion == "not_occluded")):
        return state, pictogram
    
    else:
        return None


def crop_traffic_lights(json_file, output_dir, image_dir, min_width=10, tolerance = 2):
    counts = [0,0]
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    new_data = {}  # New JSON data
    
    for image_data in data['images']:
        labels = image_data['labels']
        
        image_name = os.path.splitext(os.path.basename(image_data['image_path']))[0]
        
        image_path = os.path.join(image_dir, image_name+'.jpg')
        image = Image.open(image_path)
        
        for label in labels:
            result = determine_class(label['attributes'])
            if result is not None:
                state, pictogram = result
                x = label['x']
                y = label['y']
                w = label['w']
                h = label['h']
                counts[0] += 1
                if w >= min_width:
                    max_dim = max(w,h)
                    square_size = max_dim + tolerance*2
    
                    # Calculate the center coordinates
                    center_x = x + w / 2
                    center_y = y + h / 2
                    
                    # Calculate the coordinates for the square
                    x_min = max(int(center_x - square_size / 2), 0)
                    y_min = max(int(center_y - square_size / 2), 0)
                    x_max = min(int(center_x + square_size / 2), image.width)
                    y_max = min(int(center_y + square_size / 2), image.height)
                    
                    region = (x_min, y_min, x_max, y_max)
                    
                    counts[1] += 1
                    traffic_light = image.crop(region)
                    
                    # Generate a unique filename for the cropped image
                    output_filename = f'{image_name}_{label["unique_id"]}__class_{state}-{pictogram}.png'
                    output_path = os.path.join(output_dir, 'images/', output_filename)
                    
                    traffic_light.save(output_path)
                    
                    # Add data to the new JSON
                    output_data = {
                        'state': state,
                        'pictogram': pictogram
                    }
                    new_data[output_filename] = output_data
        
        # Save the new JSON file
        new_json_file = os.path.join(output_dir, 'traffic_lights.json')
        with open(new_json_file, 'w') as f:
            json.dump(new_data, f, indent=4)
            
    print(f'Processed {image_path} with {counts[1]}/{counts[0]} cropped images'	)
    


def process_city(city):
    json_file = '/home/ippen/dataset/dtld/DTLD_Labels_v2.0/v2.0/' + city + '.json'
    image_dir = '/home/ippen/dataset/dtld/' + city + '/images'
    output_dir = '/home/ippen/dataset/cropped_rect_dtld/' + city

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir + '/images', exist_ok=True)

    crop_traffic_lights(json_file, output_dir, image_dir, 20, 5)


cities = ['Berlin', 'Bochum', 'Bremen', 'Dortmund', 'Duesseldorf', 'Essen', 'Frankfurt', "Fulda", "Hannover", "Kassel", "Koeln"]

# Create a list to store the threads
threads = []

# Create and start a thread for each city
for city in cities:
    thread = threading.Thread(target=process_city, args=(city,))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()


