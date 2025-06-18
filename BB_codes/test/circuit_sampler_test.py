import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.bb_code import BBCode
from circ_gen.circ_gen import gen_circ_only_z_detectors
from parameters.code_config import get_config
from noise_model.noise_model import standard_depolarizing_noise_model
from circ_gen.circ_gen_coupler_de import gen_circ_coupler_defect, gen_circ_coupler_defect_only_z_detectors, gen_circ_75per_coupler, gen_circ_50per_coupler
from circ_gen.circ_gen_data_qubit_de import gen_circ_data_qubit_de_only_z_det

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
    code_setting = 1

    # Get the configuration and its normalized parameters
    config = get_config(code_setting)
    print(f"Selected configuration: {config}")
    code_input_params = config.get_params()
    print(f"BB code parameters: {code_input_params}")

    code = BBCode(code_input_params)



    sround = code.d
    error_rate = 0.01

    print('Generating circuit...')
    circuit = gen_circ_50per_coupler(code, sround)

    # save circuit diagram to svg file
    # svg_text = str(circuit.diagram('timeline-svg'))
    # with open("figures/circuit_diagram_1.svg", "w") as f:
    #     f.write(svg_text)
    


    test_probability = 0.002

    print(f"Applying noise with probability {test_probability}...")

    noise_circuit = standard_depolarizing_noise_model(circuit, code.full_qubit_set, probability=test_probability)

    # save the detector circuit diagram to svg file

    print("noisy circuit:", noise_circuit)



    print('Generating detector error model...')
    dem = noise_circuit.detector_error_model()

    print('Sampling circuit...')

    sampler = noise_circuit.compile_sampler()
    one_sample = sampler.sample(shots=1)[0]
    for k in range(0, len(one_sample), code.n):
        timeslice = one_sample[k:k+code.n]
        print("".join("1" if e else "_" for e in timeslice))


    print('Sampling detector circuit...')

    detector_sampler = noise_circuit.compile_detector_sampler()
    one_sample = detector_sampler.sample(shots=1)[0]
    for k in range(0, len(one_sample), code.n):
        timeslice = one_sample[k:k+code.n]
        print("".join("!" if e else "_" for e in timeslice))



    







