from os.path import join, dirname, realpath
import itertools
import pytest
import numpy as np
import biotite.structure.io.mmtf as biotite_mmtf
import MolecularNodes.assembly.mmtf as mmtf


DATA_DIR = join(dirname(realpath(__file__)), "data")


@pytest.mark.parametrize("pdb_id, file_format", itertools.product(
    ["1f2n", "5zng"],
    ["mmtf"]
))
def test_get_transformations(pdb_id, file_format):
    """
    Compare an assembly built from transformation information in
    MolecularNodes with assemblies built in Biotite.
    """
    path = join(DATA_DIR, f"{pdb_id}.{file_format}")
    if file_format == "mmtf":
        mmtf_file = biotite_mmtf.MMTFFile.read(path)
        atoms = biotite_mmtf.get_structure(mmtf_file, model=1)
        try:
            ref_assembly = biotite_mmtf.get_assembly(mmtf_file, model=1)
        except NotImplementedError:
            pytest.skip(
                "The limitation of the function does not support this "
                "structure"
            )
        test_parser = mmtf.MMTFAssemblyParser(mmtf_file) 
    else:
        raise ValueError(f"Format '{file_format}' does not exist")
    
    assembly_id = test_parser.list_assemblies()[0]
    transformations = test_parser.get_transformations(assembly_id)
    # Build assembly from transformation information
    test_assembly = None
    for chain_ids, rotation, translation in transformations:
        sub_assembly = atoms[np.isin(atoms.chain_id, chain_ids)].copy()
        sub_assembly.coord = np.dot(rotation, sub_assembly.coord.T).T
        sub_assembly.coord += translation
        if test_assembly is None:
            test_assembly = sub_assembly
        else:
            test_assembly += sub_assembly
    
    assert test_assembly.array_length() == ref_assembly.array_length()
    # The atom name is used as indicator of correct atom ordering here
    assert np.all(test_assembly.atom_name == ref_assembly.atom_name)
    assert np.allclose(test_assembly.coord, ref_assembly.coord, atol=1e-4)