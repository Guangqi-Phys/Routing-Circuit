import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sinter
import stim
from typing import List
import numpy as np
from ldpc.sinter_decoders import SinterBpOsdDecoder
import matplotlib.pyplot as plt
from src.bb_code import BBCode
from parameters.code_config import get_config
from circ_gen.circ_gen import gen_circ_only_z_detectors
from circ_gen.circ_gen_coupler_de import gen_circ_coupler_defect_only_z_detectors
from noise_model.noise_model import si1000_noise_model, standard_depolarizing_noise_model
from parameters.bposd_para import BposdParameters
import pickle


bposd_params = BposdParameters()
my_max_iter, my_ms_scaling_factor, my_osd_method, my_bp_method, my_osd_order = bposd_params.get_params()




if __name__ == "__main__":


    results_dir = 'results'

    # use pickle to load the results collected_surface_code_stats
    with open(os.path.join(results_dir, 'collected_bb_stats_reduced_coupler12.pkl'), 'rb') as f:
        collected_surface_code_stats_12 = pickle.load(f)
    with open(os.path.join(results_dir, 'collected_bb_stats_reduced_coupler34.pkl'), 'rb') as f:
        collected_surface_code_stats_34 = pickle.load(f)
    with open(os.path.join(results_dir, 'collected_bb_stats_reduced_coupler5.pkl'), 'rb') as f:
        collected_surface_code_stats_5 = pickle.load(f)

    collected_surface_code_stats = collected_surface_code_stats_12 + collected_surface_code_stats_34 + collected_surface_code_stats_5

    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=collected_surface_code_stats,
        x_func=lambda stat: stat.json_metadata['p'],
        group_func=lambda stat: f'code {stat.json_metadata["code"]}',
        failure_units_per_shot_func=lambda stat: stat.json_metadata['r'],
    )
    ax.set_ylim(1e-7, 1e-1)
    ax.set_xlim(0.0005, 0.01)  # Adjusted to match your max noise value
    ax.loglog()
    
    # Set x-grid to match the noise values used in simulation
    noise_values = [0.0005, 0.001, 0.01]  
    # noise_values = [0.008, 0.010, 0.015, 0.018]
    # noise_values = [0.015, 0.025, 0.030, 0.040]
    plt.xticks(noise_values)
    
    # ax.set_title("BB Code Full-Coupler Sequential Circuit")
    ax.set_title("BB Code Routing Circuit")
    ax.set_xlabel("Phyical Error Rate")
    ax.set_ylabel("Logical Error Rate per Round")
    ax.grid(which='major')
    ax.grid(which='minor')
    ax.legend()
    fig.set_dpi(300)  # Show it bigger
    
    # Save figure to file
    plt.savefig('figures/bb_wc_threshold_si1000.pdf', bbox_inches='tight', format='pdf')
    # Optionally display the figure as well
    plt.show()