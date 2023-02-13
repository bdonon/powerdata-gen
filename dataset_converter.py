import argparse
import tqdm
import os

import ml4ps as mp


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Convert a database into a target format.')
    parser.add_argument('--source_database', type=str, required=True,
                        help='Path to the database (which contains train/ and test/) which you want to convert')
    parser.add_argument('--target_database', type=str, required=True,
                        help='Name of the database you want to create.')
    parser.add_argument('--target_extension', type=str, required=True,
                        help='Extension in which you want to convert your database.')
    args = parser.parse_args()

    # Create database dir
    os.mkdir(args.target_database)

    backend = mp.PandaPowerBackend()

    source_path = args.source_database
    target_path = args.target_database
    for source_file in tqdm.tqdm(os.listdir(source_path)):
        if source_file.endswith('.json'):
            power_grid = backend.load_power_grid(os.path.join(source_path, source_file))
            backend.save_power_grid(power_grid, target_path, format=args.target_extension)
        else:
            pass
