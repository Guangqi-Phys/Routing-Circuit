import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sinter
from typing import List
from ldpc.sinter_decoders import SinterBpOsdDecoder
from src.surface_code import SurfaceCode, transform_dictionary
from noise_model.noise_model import si1000_noise_model, standard_depolarizing_noise_model
from circ_gen.circ_gen import gen_circ, gen_circ_3_coupler_new, gen_circ_3_coupler_gidney
import matplotlib.pyplot as plt
from parameters.bposd_para import BposdParameters
import pickle # Add this import



if __name__ == "__main__":

    # input_code_paras = [5,5]
    # code = SurfaceCode(input_code_paras)

    # circuit = gen_circ(code, sround)

    # noise_circuit = standard_depolarizing_noise_model(circuit, probability=test_probability)

    bposd_params = BposdParameters()
    my_max_iter, my_ms_scaling_factor, my_osd_method, my_bp_method, my_osd_order = bposd_params.get_params()

    surface_code_tasks = [
    sinter.Task(
        circuit = si1000_noise_model(
            gen_circ_3_coupler_new(SurfaceCode([d, d]), d), SurfaceCode([d, d]).full_qubit_set,
            probability=noise,
        ),
        json_metadata={'d': d, 'r': d, 'p': noise},
    )
    for d in [3,5,7,9]
    for noise in [0.0005, 0.001, 0.003, 0.005]  # for gidney's circuit
    # for noise in [0.008, 0.010, 0.012, 0.015, 0.018]  # for our circuit
    # for noise in [0.015, 0.018, 0.022, 0.025, 0.030, 0.035, 0.040] # for the normal circuit
    ]

    collected_surface_code_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=10,
        tasks=surface_code_tasks,
        # decoders=['pymatching'],
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
        max_shots=1_000_000,
        max_errors=500,
        print_progress=True,
        )

    # Create results directory if it doesn't exist
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # use pickle to save the results collected_surface_code_stats
    with open(os.path.join(results_dir, 'collected_sc_stats_routing_bposd_nodet_large.pkl'), 'wb') as f:
        pickle.dump(collected_surface_code_stats, f)
    print(f"Results saved to {os.path.join(results_dir, 'collected_sc_stats_routing.pkl')}")

    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=collected_surface_code_stats,
        x_func=lambda stat: stat.json_metadata['p'],
        group_func=lambda stat: f'd={stat.json_metadata["d"]}',
        failure_units_per_shot_func=lambda stat: stat.json_metadata['r'],
        )
    ax.set_ylim(1e-6, 1e-1)
    ax.set_xlim(0.0005, 0.01)  # Adjusted to match your max noise value
    ax.loglog()
    
    # Set x-grid to match the noise values used in simulation
    noise_values = [0.0005, 0.001, 0.01] 
    # noise_values = [0.008, 0.010, 0.015, 0.018]
    # noise_values = [0.015, 0.025, 0.030, 0.040]
    plt.xticks(noise_values)
    
    ax.set_title("Conventional 4 layers circuit")
    ax.set_xlabel("Phyical Error Rate")
    ax.set_ylabel("Logical Error Rate per Round")
    ax.grid(which='major')
    ax.grid(which='minor')
    ax.legend()
    fig.set_dpi(300)  # Show it bigger
    
    # Create figures directory if it doesn't exist
    figures_dir = 'figures'
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)
    
    # Save figure to file
    plt.savefig(os.path.join(figures_dir, 'sc_threshold_si1000.svg'), bbox_inches='tight', format='svg')
    # Optionally display the figure as well
    plt.show()