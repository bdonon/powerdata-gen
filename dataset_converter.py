import pandapower as pp
import pandapower.converter as pc
import argparse
import tqdm
import os


def get_export(extension):
    if extension == '.json':
        return pp.to_json
    elif extension == '.pkl':
        return pp.to_pickle
    elif extension == '.xlsx':
        return pp.to_excel
    elif extension == '.sql':
        return pp.to_sql
    elif extension == '.m':
        return pc.to_mpc
    else:
        raise ValueError('Extension not valid !')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Convert a database into a target format.')
    parser.add_argument('--source_database', type=str, required=True,
                        help='Path to the database (which contains train/ and test/) which you want to convert')
    parser.add_argument('--target_database', type=str, required=True,
                        help='Name of the database you want to create.')
    parser.add_argument('--target_extension', type=str, required=True,
                        help='Extension in which you want to convert your database.')
    args = parser.parse_args()

    export = get_export(args.target_extension)

    # Create database dir
    os.mkdir(args.target_database)

    # Train set
    for mode in ['train', 'test']:
        os.mkdir(os.path.join(args.target_database, mode))
        source_path = os.path.join(args.source_database, mode)
        target_path = os.path.join(args.target_database, mode)
        for source_file in tqdm.tqdm(os.listdir(source_path), desc='Processing {} set'.format(mode)):
            if source_file.endswith('.json'):
                net = pp.from_json(os.path.join(source_path, source_file))
                target_file = os.path.splitext(source_file)[0]
                export(net, os.path.join(target_path, target_file))
            else:
                pass
