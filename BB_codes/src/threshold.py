import sinter
import stim
import numpy as np
from ldpc.sinter_decoders import SinterBpOsdDecoder
from matplotlib import pyplot as plt
from circ_gen.circ_gen import gen_circ_only_z_detectors
from circ_gen.circ_gen_coupler_de import gen_circ_coupler_defect_only_z_detectors
from noise_model.noise_model import si1000_noise_model, standard_depolarizing_noise_model
from parameters.bposd_para import BposdParameters
import os


bposd_params = BposdParameters()
my_max_iter, my_ms_scaling_factor, my_osd_method, my_bp_method, my_osd_order = bposd_params.get_params()

error_rates = [0.0005, 0.001, 0.003, 0.005, 0.007, 0.009]

def generate_tasks(code,distance,rounds):
    for p in error_rates:
        noise_circuit = si1000_noise_model(gen_circ_coupler_defect_only_z_detectors(code,rounds), code.full_qubit_set, probability=p)
        yield sinter.Task(
            circuit=noise_circuit,
            json_metadata={
                "p": p,
                "d": distance,
                "rounds": rounds,
            }
        )

def run_sinter_simulation(code,distance,rounds):
    # Clean up previous samples file
    sample_file = f"testdata/bposd_bb_code_d.csv"
    if os.path.exists(sample_file):
        os.remove(sample_file)

    samples = sinter.collect(
        num_workers=10,
        max_shots=100_000,
        max_errors=5_000,
        tasks=generate_tasks(code,distance,rounds),
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
        print_progress=True,
        save_resume_filepath=sample_file,
    )
    return samples




# def print_results(samples):
#     # Print samples as CSV data.
#     print(sinter.CSV_HEADER)
#     for sample in samples:
#         print(sample.to_csv_line())


def plot_sinter_simulation_threshold_results(samples,paras):
    # Render a matplotlib plot of the data.
    fig, ax = plt.subplots(figsize=(5, 5))
    sinter.plot_error_rate(
        ax=ax,
        stats=samples,
        group_func=lambda stat: f"BB Code d={stat.json_metadata['d']}",
        filter_func=lambda stat: stat.decoder == "bposd",
        x_func=lambda stat: stat.json_metadata["p"],
        failure_units_per_shot_func=lambda stat: stat.json_metadata['rounds'],
    )
    ax.set_ylabel("Logical Error Rate")
    ax.set_title(f"Threshold for BB Code {paras}")
    ax.loglog()
    ax.grid()
    ax.set_xlabel("Physical Error Rate")
    ax.legend()

    # Save to file and also open in a window
    fig.savefig("figures/bb_code_d="+str(paras)+"_threshold_plot.png", dpi=500)
    plt.show()















