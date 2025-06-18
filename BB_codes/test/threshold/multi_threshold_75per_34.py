import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import sinter
import stim
from typing import List
import numpy as np
from ldpc.sinter_decoders import SinterBpOsdDecoder
import matplotlib.pyplot as plt
from src.bb_code import BBCode
from parameters.code_config import get_config
from circ_gen.circ_gen import gen_circ, gen_circ_only_z_detectors
from circ_gen.circ_gen_coupler_de import gen_circ_50per_coupler, gen_circ_75per_coupler, gen_circ_coupler_defect_only_z_detectors
from noise_model.noise_model import si1000_noise_model, standard_depolarizing_noise_model
from parameters.bposd_para import BposdParameters
import pickle


bposd_params = BposdParameters()
my_max_iter, my_ms_scaling_factor, my_osd_method, my_bp_method, my_osd_order = bposd_params.get_params()




if __name__ == "__main__":

    # input_code_paras = [5,5]
    # code = SurfaceCode(input_code_paras)

    # circuit = gen_circ(code, sround)

    # noise_circuit = standard_depolarizing_noise_model(circuit, probability=test_probability)

    # circuit_set = 0

    # if circuit_set == 0:
    #     gen_circ_fun = gen_circ_coupler_defect_only_z_detectors
    # else:
    #     gen_circ_fun = gen_circ_only_z_detectors

    bposd_params = BposdParameters()
    my_max_iter, my_ms_scaling_factor, my_osd_method, my_bp_method, my_osd_order = bposd_params.get_params()
    

    print("Generating tasks...")

    # sample_file = f"testdata/bposd_bb_code_coupler_defect_cricuit.csv"
    # if os.path.exists(sample_file):
    #     os.remove(sample_file)

    bb_code_tasks = [
    sinter.Task(
        circuit = si1000_noise_model(
            gen_circ_75per_coupler(BBCode(get_config(code_setting).get_params()), BBCode(get_config(code_setting).get_params()).qcodedz), BBCode(get_config(code_setting).get_params()).full_qubit_set,
            probability=noise,
        ),
        json_metadata={'code': code_setting, 'r': BBCode(get_config(code_setting).get_params()).qcodedz, 'p': noise},
    )
    for code_setting in [3,4]
    for noise in [0.0001, 0.0005, 0.001, 0.003]
    ]
    
    print("Decoding...")
    collected_bb_code_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=10,
        tasks=bb_code_tasks,
        decoders=["bposd"],
        custom_decoders={
            "bposd": SinterBpOsdDecoder(
                schedule="parallel",
                max_iter=my_max_iter,
                bp_method= my_bp_method,
                ms_scaling_factor=my_ms_scaling_factor,
                osd_method=my_osd_method,
                osd_order = my_osd_order,
            ),
        },
        max_shots=10_000_000,
        max_errors=1000,
        print_progress=True,
        # save_resume_filepath=sample_file,
    )

    # Create results directory if it doesn't exist
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # use pickle to save the results collected_surface_code_stats
    with open(os.path.join(results_dir, 'collected_bb_stats_75per_coupler34.pkl'), 'wb') as f:
        pickle.dump(collected_bb_code_stats, f)
    # print(f"Results saved to {os.path.join(results_dir, 'collected_bb_stats_reduced_coupler.pkl')}")


    # fig, ax = plt.subplots(1, 1)
    # sinter.plot_error_rate(
    #     ax=ax,
    #     stats=collected_bb_code_stats,
    #     x_func=lambda stat: stat.json_metadata['p'],
    #     group_func=lambda stat: f'code {stat.json_metadata["code"]}',
    #     failure_units_per_shot_func=lambda stat: stat.json_metadata['r'],
    #     )
    # ax.set_ylim(1e-7, 1)
    # ax.set_xlim(0.0005, 0.01)  # Adjusted to match your max noise value
    # ax.loglog()
    
    # # Set x-grid to match the noise values used in simulation
    # noise_values = [0.0005, 0.001, 0.010]  
    # # noise_values = [0.008, 0.010, 0.015, 0.018]
    # # noise_values = [0.015, 0.025, 0.030, 0.040]
    # plt.xticks(noise_values)
    
    # ax.set_title("BB Code Error Rates per Round under Circuit Noise")
    # ax.set_xlabel("Phyical Error Rate")
    # ax.set_ylabel("Logical Error Rate per Round")
    # ax.grid(which='major')
    # ax.grid(which='minor')
    # ax.legend()
    # fig.set_dpi(300)  # Show it bigger
    
    # # Save figure to file
    # plt.savefig('figures/bb_wc_threshold_si1000.svg', bbox_inches='tight', format='svg')
    # # Optionally display the figure as well
    # plt.show()