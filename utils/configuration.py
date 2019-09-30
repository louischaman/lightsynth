import yaml

def load_lights(yaml_file):
    with open(yaml_file) as f:
        lights = yaml.load(f, Loader=yaml.FullLoader)

    return lights

def save_lights(lights, yaml_file):
    with open(yaml_file, 'w') as f:
        yaml.dump(lights, f)