import numpy as np
import stim
from beliefmatching import detector_error_model_to_check_matrices
from ldpc import BpOsdDecoder
from parameters.bposd_para import BposdParameters
import multiprocessing
from concurrent.futures import ProcessPoolExecutor


def _run_single_iteration(circuit):
    """
    Helper function for multiprocessing that calculates X distance for a single iteration.
    
    Args:
        circuit (stim.Circuit): The circuit to analyze
        
    Returns:
        int: The X distance found for this iteration
    """
    # Create a copy of the circuit to avoid modifying the original
    circuit_copy = circuit.copy()
    
    # Calculate X distance for this iteration
    x_distance = circuit_level_x_distance(circuit_copy)
    print(f"Current circuit level X distance: {x_distance}")
    
    return x_distance


def circuit_level_min_x_distance(circuit: stim.Circuit, iter_num: int):
    """
    Calculate the minimum X distance of a circuit over multiple iterations using multiprocessing.
    
    This function repeatedly calls circuit_level_x_distance in parallel to find the minimum X distance.
    Multiple iterations are used because the decoder may find different logical operators
    in different runs, and we want to find the minimum weight logical operator.
    
    Args:
        circuit (stim.Circuit): The quantum circuit to analyze
        iter_num (int): Number of iterations to run the calculation
        
    Returns:
        int: The minimum X distance found across all iterations
    """
    # Determine the number of processes to use (up to the number of CPU cores)
    num_processes = min(multiprocessing.cpu_count(), iter_num)
    
    # Create a list of the same circuit for each iteration
    circuits = [circuit] * iter_num
    
    # Use ProcessPoolExecutor to run iterations in parallel
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        # Map the _run_single_iteration function to each circuit in the list
        distances = list(executor.map(_run_single_iteration, circuits))
    
    # Find the minimum distance from all iterations
    min_x_distance = min(distances) if distances else float('inf')
    
    return min_x_distance


def circuit_level_x_distance(circuit: stim.Circuit):
    """
    Calculate the X distance of a quantum circuit using a belief propagation decoder.
    
    This function determines the minimum weight of an X-type logical operator by:
    1. Converting the circuit to a detector error model
    2. Extracting the check matrix and observables matrix
    3. Creating a syndrome that triggers a logical error
    4. Using belief propagation with ordered statistics decoding to find a low-weight solution
    
    Args:
        circuit (stim.Circuit): The quantum circuit to analyze
        
    Returns:
        int: The minimum weight of an X-type logical operator found
    """
    # Extract the detector error model from the circuit
    dem = circuit.detector_error_model()
    # Convert the detector error model to check matrices
    dem_matrices = detector_error_model_to_check_matrices(dem, allow_undecomposed_hyperedges=True)
    
    # Get check matrix and observables matrix
    check_matrix = dem_matrices.check_matrix.todense()  # Convert check matrix to dense
    observables_matrix = dem_matrices.observables_matrix.todense()  # Convert observables matrix to dense

    # print(f"Check matrix shape: {check_matrix.shape}")
    # print(f"Observables matrix shape: {observables_matrix.shape}")

    # Select a random logical operator to find the distance (use the structure of Bravyi et al.) A logical operator at circuit level is a linear combination of rows of the check matrix and rows of the observables matrix.
    DXL_matrix = np.vstack((check_matrix, observables_matrix))
    random_vector = np.random.randint(2,size=DXL_matrix.shape[0]) 
    random_vector[-1] = 1
    random_logical_op = (random_vector @ DXL_matrix) % 2
    random_logical_op = np.reshape(random_logical_op,(1,DXL_matrix.shape[1]))

    # Combine the check matrix with the selected observable
    dem_matrix = np.vstack((check_matrix, random_logical_op))

    # Create a syndrome that only triggers the logical observable
    syndrome = np.zeros(dem_matrix.shape[0], dtype=int)
    syndrome[-1] = 1  # Set the last element (corresponding to the logical observable) to 1

    wminX = float('inf')  # Initialize minimum weight to infinity

    # Get decoder parameters
    bposd_params = BposdParameters()
    my_max_iter, my_ms_scaling_factor, my_osd_method, my_bp_method, my_osd_order = bposd_params.get_params()

    # Initialize the BP+OSD decoder
    bpdX = BpOsdDecoder(
        dem_matrix,
        error_rate=0.002,  # Physical error rate for the decoder
        max_iter=my_max_iter,  # Maximum number of iterations for BP
        bp_method=my_bp_method,  # Belief propagation method
        ms_scaling_factor=my_ms_scaling_factor,  # Min sum scaling factor
        osd_method=my_osd_method,  # OSD method
        osd_order=my_osd_order  # OSD search depth (commented out)
    )
    
    # Decode the syndrome to find a low-weight logical operator
    bpdX.decode(syndrome)
    low_weight_logical = bpdX.osdw_decoding
    
    # Count the weight of the found logical operator
    wt = np.count_nonzero(low_weight_logical)
    
    # Update minimum weight if the found operator is valid and has lower weight
    if wt < wminX and wt > 0:
        wminX = wt
    
    return wminX




