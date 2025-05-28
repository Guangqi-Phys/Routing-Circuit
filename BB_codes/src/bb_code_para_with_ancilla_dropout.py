import numpy as np
from multiprocessing import Pool
from bposd.css import css_code
from src.bb_code import BBCode
from src.bb_code_parameters import logical_operator_and_distance_compute




"""
This function is just for simulating the distance of a quantum code with coupler defects (for CNOT gate in the syndrrome measurement circuit), and we deal with it very simply, just delete the corresonding stabilizers. Then we computing the minimum distance of the code with a reduced parity check matrix.
"""


def get_distance_with_dropout(code: BBCode, dropout_num):
    """
    Calculate the minimum distance of a quantum code with dropout.
    
    Args:
        code (BBCode): The BBCode object representing the quantum code.
        dropout_num (int): The number of stabilizers to randomly discard.
        
    Returns:
        int: The minimum distance across all logical operators
    """
    # X type check matrix
    hx = code.hx
    # give a probability of dropout

    # generate the parity check matrix with dropout, randomly drop out dropout_num rows of hx
    hx_dropout = hx.copy()
    # Get total number of rows in hx
    # total_rows = hx.shape[0]
    # # Randomly select rows to keep (total rows - dropout_num
    # rows_to_keep = np.random.choice(total_rows, total_rows - dropout_num, replace=False)
    # Keep only selected rows

    selected_dorpout_rows = [0,24,2,26]
    # generate an array of 1 to 53
    total_rows = np.arange(54)
    # Remove selected rows from total_rows
    rows_to_keep = np.setdiff1d(total_rows, selected_dorpout_rows)

    hx_dropout = hx_dropout[rows_to_keep, :]

    # Print the size of hx_dropout
    print(f"hx_dropout_size: {hx_dropout.shape}")
    
    # Prepare arguments for parallel processing
    args = [(hx_dropout, code.qcode.lx[i,:]) for i in range(code.k)]
    
    # Use multiprocessing with 10 CPU cores
    with Pool(processes=10) as pool:
        results = pool.starmap(logical_operator_and_distance_compute, args)
    
    # Extract distances from results
    distances = [result[0] for result in results]
    
    # Print results
    for i, (distance, _) in enumerate(results):
        print(f"Distance of the logical operator {i} with dropout: {distance}")
    
    return min(distances) if distances else code.n
	
	

		
	
    
