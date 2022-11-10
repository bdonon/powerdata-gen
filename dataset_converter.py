import pandapower as pp
import pandapower.converter as pc
import numpy as np
import argparse
import tqdm
import os

from pandapower.converter.matpower.to_mpc import _ppc2mpc
from scipy.io import savemat
import copy


def to_mpc(net, filename=None, **kwargs):
    """Modification of the `to_mpc` implementation of pandapower
    (https://github.com/e2nIEE/pandapower/blob/develop/pandapower/converter/matpower/to_mpc.py)

    The present implementation saves all objects and sets the status of out-of-service
    objects to 0.
    The default implementation deletes objects that are out-of-service, which
    completely alters the object ordering. For visualization purpose, panoramix relies
    heavily on this ordering.
    """

    net = copy.deepcopy(net)

    # Save actual object status
    gen_status = net.gen.in_service.astype(float).values
    ext_grid_status = net.ext_grid.in_service.astype(float).values
    line_status = net.line.in_service.astype(float).values
    trafo_status = net.trafo.in_service.astype(float).values
    ppc_gen_status = np.concatenate([ext_grid_status, gen_status])
    ppc_branch_status = np.concatenate([line_status, trafo_status])

    # Set all objects to be in_service and convert to pypower object
    net.gen.in_service = True
    net.ext_grid.in_service = True
    net.line.in_service = True
    net.trafo.in_service = True
    ppc = pp.converter.to_ppc(net, **kwargs)

    # Manually change the Gen and Branch status to reflect the actual in_service values
    ppc['gen'][:, 7] = ppc_gen_status
    ppc['branch'][:, 10] = ppc_branch_status

    # Untouched part
    mpc = dict()
    mpc["mpc"] = _ppc2mpc(ppc)
    if filename is not None:
        savemat(filename, mpc)
    return mpc


def get_export(extension):
    if extension == '.json':
        return pp.to_json
    elif extension == '.pkl':
        return pp.to_pickle
    elif extension == '.xlsx':
        return pp.to_excel
    elif extension == '.sql':
        return pp.to_sql
    elif extension == '.mat':
        return (lambda x, y : to_mpc(x, y, take_slack_vm_limits=False))
    elif extension == '.m':
        from oct2py import octave
        return matpower_export_factory(octave)
    else:
        raise ValueError('Extension not valid !')


def matpower_export_factory(octave):
    def matpower_export(net, target_path):
        pc.to_mpc(net, 'tmp.mat')
        mpc = octave.loadcase('tmp.mat')
        #octave.runpf(mpc)
        octave.savecase(target_path, mpc)
        os.remove('tmp.mat')
    return matpower_export

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

    source_path = args.source_database
    target_path = args.target_database
    for source_file in tqdm.tqdm(os.listdir(source_path)):
        if source_file.endswith('.json'):
            net = pp.from_json(os.path.join(source_path, source_file))
            target_file = os.path.splitext(source_file)[0] + args.target_extension
            export(net, os.path.join(target_path, target_file))
        else:
            pass
