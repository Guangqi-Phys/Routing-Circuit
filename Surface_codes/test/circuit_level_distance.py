import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.surface_code import SurfaceCode
from circ_gen.circ_gen import gen_circ, gen_circ_dual, gen_circ_3_coupler_gidney, gen_circ_3_coupler_new
from src.circuit_level_distance import circuit_level_min_x_distance
from noise_model.noise_model import si1000_noise_model, standard_depolarizing_noise_model
import stim

# Print selected configuration information



if __name__ == "__main__":

    input_code_paras = [7,7]
    code = SurfaceCode(input_code_paras)

    
    
    # print("z_stb", code.z_stb_set)

    # z_stb_reset = code.weird_x_stb_g1 + [q for q in code.z_stb_set_g if q not in code.weird_z_stb_g1]
    # x_stb_reset_1 = code.weird_z_stb_g2 + [q for q in code.x_stb_set_g if q not in code.weird_x_stb_g2]

    # print("z_stb_reset", sorted(z_stb_reset))


    # print("dual_z_stb", code.dual_z_stb_set)
    # print("z_stb_reset_1",sorted(x_stb_reset_1))

    



    # # print(f"Code parameters: {code.params}")

    # body loop number of generated circuit
    sround = code.d * 3

    print('Generating circuit...')
    circuit = gen_circ_3_coupler_new(code, sround)


    error_rate = 0.02

    print(f"Applying noise with probability {error_rate}...")

    noise_circuit = si1000_noise_model(circuit, code.full_qubit_set, probability=error_rate)

    # read circuit from file d=5-style=3-CX.stim
    # test_circuit = stim.Circuit.from_file("test/d=5-style=3-CX.stim")
    # test_circuit = stim.Circuit.from_file("test/d=5-style=3-CX-half-det.stim")

    # surface code with only 3 couplers

    # noise = 0.02
    # noise_circuit = stim.Circuit.generated(
    # "surface_code:unrotated_memory_z",
    # rounds=5,
    # distance=5,
    # after_clifford_depolarization=noise,
    # after_reset_flip_probability=noise,
    # before_measure_flip_probability=noise,
    # before_round_data_depolarization=noise)

    # test_noise_circuit = standard_depolarizing_noise_model(test_circuit, code.full_qubit_set, probability=error_rate)



    print('Computing circuit level X distance...')
    cd_x = circuit_level_min_x_distance(noise_circuit, 100)
    print(f"Final circuit level X distance: {cd_x}")

