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


    # Create results directory if it doesn't exist
    results_dir = 'results'

    # use pickle to load the results collected_surface_code_stats
    with open(os.path.join(results_dir, 'collected_sc_stats_routing_bposd_det_large.pkl'), 'rb') as f:
        collected_surface_code_stats = pickle.load(f)

    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=collected_surface_code_stats,
        x_func=lambda stat: stat.json_metadata['p'],
        group_func=lambda stat: f'd={stat.json_metadata["d"]}',
        failure_units_per_shot_func=lambda stat: stat.json_metadata['r'],
        )

    # for line in ax.get_lines():
    #     line.set_linestyle('dashed')

    ax.set_ylim(1e-6, 1)
    ax.set_xlim(0.0005, 0.01)  # Adjusted to match your max noise value
    ax.loglog()
    
    # Set x-grid to match the noise values used in simulation
    noise_values = [0.0005, 0.001, 0.01] 
    # noise_values = [0.008, 0.010, 0.015, 0.018]
    # noise_values = [0.015, 0.025, 0.030, 0.040]
    plt.xticks(noise_values)
    
    ax.set_title("Three couplers routing circuit - BPOSD")
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
    plt.savefig(os.path.join(figures_dir, 'sc_threshold_bposd_nodet_large.svg'), bbox_inches='tight', format='svg')
    # Optionally display the figure as well
    plt.show()