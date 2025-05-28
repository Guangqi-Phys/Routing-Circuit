import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt
from src.bb_code import BBCode
from parameters.code_config import get_config
from src.threshold import run_sinter_simulation, plot_sinter_simulation_threshold_results

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


    # print(f"Code parameters: {code.params}")


    samples = run_sinter_simulation(code, code.qcodedz, code.qcodedz)

    plot_sinter_simulation_threshold_results(samples,code.params)













