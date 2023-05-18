import json

#cities = ['Berlin', 'Bochum', 'Bremen', 'Duesseldorf', 'Essen', "Fulda", "Hannover", "Kassel", "Koeln"]
cities = ['Dortmund', 'Frankfurt']

dataset_path = '/home/ippen/dataset/cropped_dtld_mix/validation/'

combined_data = {}
for city in cities:
    label_path = dataset_path+city+'/labels.json'
    with open(label_path, 'r') as f:
        data = json.load(f)
        #Combine the data
        combined_data = {**combined_data, **data}
        
with open('combined_labels.json', 'w') as f:
    json.dump(combined_data, f, indent=4)

	