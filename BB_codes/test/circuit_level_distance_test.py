import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.bb_code import BBCode
from circ_gen.circ_gen import gen_circ, gen_circ_only_z_detectors
from circ_gen.circ_gen_coupler_de import gen_circ_coupler_defect_only_z_detectors
from parameters.code_config import get_config
from noise_model.noise_model import si1000_noise_model, standard_depolarizing_noise_model
import stim
from src.circuit_level_distance import circuit_level_min_x_distance

"""
Code parameters for quantum error correction codes.

We assume the code polynomials have form:
A = 1 + y + x^a*y^b
B = 1 + x + x^c*y^d

Available configurations:
1: [[98,6,12]] - Balanced 7×7 Code (Eberhardt & Steffan, arXiv:2407.03973v1) 8
2: [[90,8,10]] - Rectangular 3×15 Code (Eberhardt & Steffan, arXiv:2407.03973v1) 6
3: [[144,12,12]] - Rectangular 12×6 Code (IBM) 9
4: [[108,8,10]] - Rectangular 9×6 Code (IBM) 8
5: [[72,12,6]] - Balanced 6×6 Code (IBM) 5
"""

# Print selected configuration information



if __name__ == "__main__":

    # polynomial parameters that defined the bb code
    # Select which code configuration to use
    code_setting = 1

    # Get the configuration and its normalized parameters
    config = get_config(code_setting)
    print(f"Selected configuration: {config}")
    code_input_params = config.get_params()
    print(f"BB code parameters: {code_input_params}")

    code = BBCode(code_input_params)


    # print(f"Code parameters: {code.params}")





    # body loop number of generated circuit
    sround = code.qcodedz

    print('Generating circuit...')
    circuit = gen_circ_coupler_defect_only_z_detectors(code, sround)


    test_probability = 0.002

    print(f"Applying noise with probability {test_probability}...")
    
    full_qubit_set = code.full_qubit_set
    noise_circuit = si1000_noise_model(circuit, full_qubit_set, probability=test_probability)

    print('Computing circuit level X distance...')
    cd_x = circuit_level_min_x_distance(noise_circuit, 500)
    print(f"Final circuit level X distance: {cd_x}")

