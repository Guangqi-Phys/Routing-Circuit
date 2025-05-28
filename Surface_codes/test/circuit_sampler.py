import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.surface_code import SurfaceCode, transform_dictionary
from circ_gen.circ_gen import gen_circ, gen_circ_3_coupler_gidney, gen_circ_3_coupler_new
from noise_model.noise_model import si1000_noise_model, standard_depolarizing_noise_model
import stim


if __name__ == "__main__":


    input_code_paras = [5,5]
    code = SurfaceCode(input_code_paras)
    # print("data qubits:", code.data_qubits_set)
    # print("z ancilla qubits:", code.z_stb_set)
    # print("x ancilla qubits:", code.x_stb_set)
    # print("z stabilizers:", transform_dictionary(code.z_stabilizers))
    # print("x stabilizers:", transform_dictionary(code.x_stabilizers))
    # print("z logical operators:", code.z_logical_op)
    # print("x logical operators:", code.x_logical_op)

    sround = 1

    print('Generating circuit...')
    # circuit = gen_circ(code, sround)
    # circuit = gen_circ(code, sround)
    circuit = gen_circ_3_coupler_new(code, sround)
    # print("circuit:", circuit)

    # circuit = stim.Circuit.from_file("test/d=5-style=3-CX-half-det.stim")

    # save circuit diagram to svg file 'detslice-with-ops-svg', tick=range(187, 197), filter_coords=['D188', ]
    svg_text = str(circuit.diagram('detslice-with-ops-svg'))
    with open("figures/circuit_det_gidney.svg", "w") as f:
        f.write(svg_text)



    test_probability = 0.02

    print(f"Applying noise with probability {test_probability}...")

    # full_qubit_set = code.data_qubits_set + code.x_stb_set + code.z_stb_set

    noise_circuit = si1000_noise_model(circuit, code.full_qubit_set, probability=test_probability)

    print("noisy circuit:", noise_circuit)

    # save the detector circuit diagram to svg file



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

