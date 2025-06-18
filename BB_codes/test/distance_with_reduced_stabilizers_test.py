import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt
from src.bb_code import BBCode
from parameters.code_config import get_config
from bposd.css import css_code
from src.bb_code_para_with_ancilla_dropout import get_distance_with_dropout
import csv

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

    # dropout_prob = 0.1

    # distance_with_dropout = get_distance_with_dropout(code,dropout_num)
    # print(f"Distance with dropout: {distance_with_dropout}")

    distance_with_dropout_list = []
    num_trial = 1
    trial_list = np.arange(3, 4)
    for dropout_num in trial_list:
        distance_with_dropout = 0
        # average 5 times of distance with dropout for each drop out probab
        for i in range(num_trial):
            distance_with_dropout += get_distance_with_dropout(code,dropout_num)
        distance_with_dropout = distance_with_dropout/num_trial
        distance_with_dropout_list.append(distance_with_dropout)
        print(f"Distance with dropout: {distance_with_dropout}")


    # Save results to CSV file
    with open('testdata/dropout_distance.dat', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Dropout Number', 'Average Distance'])
        for dropout_num, avg_distance in zip(trial_list, distance_with_dropout_list):
            writer.writerow([dropout_num, avg_distance])

    # Create visualization of distance metrics with respect to dropout count
    plt.figure(figsize=(10, 6))
    plt.plot(trial_list, distance_with_dropout_list, marker='o', color='#1f77b4', linewidth=2)
    plt.xlabel('Number of Qubits Dropped', fontsize=12)
    plt.ylabel('Circuit Distance Metric', fontsize=12)
    plt.title('Impact of Qubit Dropout on Circuit Distance', fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(trial_list)
    plt.tight_layout()
    plt.savefig('figures/distance_with_dropout.png', dpi=300, bbox_inches='tight')
    plt.close()  # More efficient than plt.show() in non-interactive contexts
