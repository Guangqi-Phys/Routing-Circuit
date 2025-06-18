import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.bb_code import BBCode
from circ_gen.circ_gen import gen_circ_only_z_detectors
from circ_gen.circ_gen_data_qubit_de import gen_circ_data_qubit_de_only_z_det
from parameters.code_config import get_config
from noise_model.noise_model import standard_depolarizing_noise_model
import stim
from src.circuit_level_distance import circuit_level_min_x_distance

"""
This script is used to compute circuit level X distance for a circuit with data qubit defects.
"""


"""
Code parameters for quantum error correction codes.

We assume the code polynomials have form:
A = 1 + y + x^a*y^b
B = 1 + x + x^c*y^d

Available configurations:
1: [[98,6,12]] - Balanced 7×7 Code (Eberhardt & Steffan, arXiv:2407.03973v1)
2: [[90,8,10]] - Rectangular 3×15 Code (Eberhardt & Steffan, arXiv:2407.03973v1)
3: [[144,12,12]] - Rectangular 12×6 Code (IBM)
4: [[108,8,10]] - Rectangular 9×6 Code (IBM)
5: [[72,12,6]] - Balanced 6×6 Code (IBM)
"""

# Print selected configuration information



if __name__ == "__main__":

    # polynomial parameters that defined the bb code
    # Select which code configuration to use
    code_setting = 4

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
    data_qubit_error_rate = 0.002
    circuit = gen_circ_data_qubit_de_only_z_det(code, sround, data_qubit_error_rate)


    test_probability = 0.002

    print(f"Applying noise with probability {test_probability}...")

    noise_circuit = standard_depolarizing_noise_model(circuit, probability=test_probability)

    print('Computing circuit level X distance...')
    cd_x = circuit_level_min_x_distance(noise_circuit, 500)
    print(f"Final circuit level X distance: {cd_x}")

