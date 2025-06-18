import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
from src.bb_code import BBCode
import numpy as np
from qiskit.result.distributions import probability
from src.bb_code_parameters import transform_dictionary, get_logical_ops_css
from parameters.code_config import get_config

# Set random seed for reproducibility
np_random = np.random.RandomState(seed=8)


def binary_matrix_rank(M):
    """
    Compute the rank of a binary matrix over GF(2).
    Args:
        M (np.ndarray): Binary matrix (entries 0 or 1).
    Returns:
        int: Rank over GF(2).
    """
    M = M.copy() % 2
    n_rows, n_cols = M.shape
    rank = 0
    row = 0
    for col in range(n_cols):
        pivot = None
        for r in range(row, n_rows):
            if M[r, col]:
                pivot = r
                break
        if pivot is not None:
            # Swap rows
            if pivot != row:
                M[[row, pivot]] = M[[pivot, row]]
            # Eliminate below
            for r in range(row + 1, n_rows):
                if M[r, col]:
                    M[r] ^= M[row]
            rank += 1
            row += 1
        if row >= n_rows:
            break
    return rank


def generate_random_data_qubit_defects(code, error_rate):
    # Set random seed for reproducibility
    data_qubit_set = code.data_qubits_set
    # Generate random defects
    defects = np_random.choice([0, 1], size=len(data_qubit_set), p=[1-error_rate, error_rate])
    # Apply defects to data qubits
    defects_set = []
    for i, defect in enumerate(defects):
        if defect == 1:
            defects_set.append(data_qubit_set[i])
    # lefted_qubits_set = sorted(list(set(data_qubit_set) - set(defects_set)))
    return defects_set


def gen_stabilizer_with_data_qubit_defects(code, defects_set):
    """
    Generate stabilizer operators with data qubit defects
    """

    x_stabilizers_dq_def = transform_dictionary(code.x_stabilizers)
    z_stabilizers_dq_def = transform_dictionary(code.z_stabilizers)
    # delete all the elements in x_stabilizers that are in defects_set, x_stabilizers is a dictionary like {1:[1,2,3,4,5,6], 2:[1,2,3,4,5,6],...}, delete all the elements in x_stabilizers that are in defects_set
    for key in x_stabilizers_dq_def:
        x_stabilizers_dq_def[key] = sorted(list(set(x_stabilizers_dq_def[key]) - set(defects_set)))
    for key in z_stabilizers_dq_def:
        z_stabilizers_dq_def[key] = sorted(list(set(z_stabilizers_dq_def[key]) - set(defects_set)))
    return x_stabilizers_dq_def, z_stabilizers_dq_def


def stabilizers_dq_def_check(code, defects_set):
    ""
    """
    In this function, we list all complete stabilizers, also for the stabilizers with data qubit defects, we list how many defects they have.
    """
    x_stabilizers_dq_def, z_stabilizers_dq_def = gen_stabilizer_with_data_qubit_defects(code, defects_set)

    # generate new dictionary for x_stabilizers_dq_def, z_stabilizers_dq_def
    stb_keys = []

    complete_x_stabilizers = {}
    incomplete_x_stabilizers = {}
    complete_x_key = []
    incomplete_x_key = []
    for key, element in x_stabilizers_dq_def.items():  # Use.items() to iterate over key-value pairs
        if len(element) == 6:  # Check length of list, not shape attribute
            complete_x_stabilizers[key] = element  # Store the key (stabilizer index)
            complete_x_key.append(key)
        else:
            incomplete_x_stabilizers[key] = element  # Store the key (stabilizer index) and the elements
            incomplete_x_key.append(key)
    #
    complete_z_stabilizers = {}
    incomplete_z_stabilizers = {}
    complete_z_key = []
    incomplete_z_key = []
    for key, element in z_stabilizers_dq_def.items():  # Use.items() to iterate over key-value pairs
        if len(element) == 6:  # Check length of list, not shape attribute
            complete_z_stabilizers[key] = element  # Store the key (stabilizer index)
            complete_z_key.append(key)  # Store the key (stabilizer index) and the elements, and the key of the incomplete stabilizer in a list, for later use in the for loop to generate the meta stabilizer for
        else:
            incomplete_z_stabilizers[key] = element  # Store the key (stabilizer index) and the elements
            incomplete_z_key.append(key)  # Store the key (stabilizer index) and the elements, and the key of the incomplete stabilizer in a list, for later use in the for loop to generate the meta stabilizer for


    # print("complete_x_stabilizers: ", complete_x_stabilizers)
    # print("incomplete_x_stabilizers: ", incomplete_x_stabilizers)
    # print("complete_z_stabilizers: ", complete_z_stabilizers)
    # print("incomplete_z_stabilizers: ", incomplete_z_stabilizers)

    # store complete_x_key, complete_z_key, incomplete_x_key, incomplete_z_key into stb_keys
    stb_keys = (complete_x_key, complete_z_key, incomplete_x_key, incomplete_z_key)

    return incomplete_x_stabilizers, incomplete_z_stabilizers, stb_keys




def gen_meta_stabilizers(code, defects_set):
    """
    In this function, we generate meta stabilizers for the incomplete stabilizers.
    We find linearly independent meta stabilizers (over GF(2)) that avoid defects.
    """


    incomplete_x_stabilizers, incomplete_z_stabilizers, stb_keys = stabilizers_dq_def_check(code, defects_set)

    x_stabilizers_de_matrix = []
    z_stabilizers_de_matrix = []

    #get full stabilizers for imcomplete_x_stabilizers and incomplete_z_stabilizers
    x_stabilizers = transform_dictionary(code.x_stabilizers)
    z_stabilizers = transform_dictionary(code.z_stabilizers)
    incomplete_x_stabilizers_com = {}
    incomplete_z_stabilizers_com = {}
    for key, element in incomplete_x_stabilizers.items():
        incomplete_x_stabilizers_com[key] = x_stabilizers[key]
    for key, element in incomplete_z_stabilizers.items():
        incomplete_z_stabilizers_com[key] = z_stabilizers[key]
    
    # Generate matrix for incomplete_x_stabilizers
    x_keys = list(incomplete_x_stabilizers_com.keys())
    for key, element in incomplete_x_stabilizers_com.items():
        row_vector = np.zeros(code.n*2)
        for i in element:
            row_vector[i] = 1
        x_stabilizers_de_matrix.append(row_vector)
    
    # Generate matrix for incomplete_z_stabilizers
    z_keys = list(incomplete_z_stabilizers_com.keys())
    for key, element in incomplete_z_stabilizers_com.items():
        row_vector = np.zeros(code.n*2)
        for i in element:
            row_vector[i] = 1
        z_stabilizers_de_matrix.append(row_vector)
    
    x_stabilizers_de_matrix = np.array(x_stabilizers_de_matrix).astype(int)
    z_stabilizers_de_matrix = np.array(z_stabilizers_de_matrix).astype(int)
    
    meta_x_stabilizers = []
    meta_x_components = []
    meta_z_stabilizers = []
    meta_z_components = []
    
    # Process X stabilizers
    if x_stabilizers_de_matrix.size > 0:
        n_x = len(x_keys)
        for weight in range(2, n_x + 1):
            for combination in np.array(np.meshgrid(*[np.array([0, 1]) for _ in range(n_x)])).T.reshape(-1, n_x):
                if np.sum(combination) != weight:
                    continue
                # Calculate the resulting meta stabilizer
                meta_stabilizer = np.zeros(code.n*2, dtype=int)
                for i, include in enumerate(combination):
                    if include:
                        meta_stabilizer = np.bitwise_xor(meta_stabilizer, x_stabilizers_de_matrix[i].astype(int))
                # Check if this combination avoids all defects
                valid = True
                for defect in defects_set:
                    if meta_stabilizer[defect] == 1:
                        valid = False
                        break
                if not valid:
                    continue
                # Check GF(2) linear independence of meta stabilizers
                if meta_x_stabilizers:
                    prev = np.vstack(meta_x_stabilizers)
                    test = np.vstack([prev, meta_stabilizer])
                    if binary_matrix_rank(test) <= len(meta_x_stabilizers):
                        continue
                # Add if independent
                components = [x_keys[i] for i in range(n_x) if combination[i] == 1]
                meta_x_stabilizers.append(meta_stabilizer)
                meta_x_components.append(components)
    
    # Process Z stabilizers (similar logic)
    if z_stabilizers_de_matrix.size > 0:
        n_z = len(z_keys)
        for weight in range(2, n_z + 1):
            for combination in np.array(np.meshgrid(*[np.array([0, 1]) for _ in range(n_z)])).T.reshape(-1, n_z):
                if np.sum(combination) != weight:
                    continue
                meta_stabilizer = np.zeros(code.n*2, dtype=int)
                for i, include in enumerate(combination):
                    if include:
                        meta_stabilizer = np.bitwise_xor(meta_stabilizer, z_stabilizers_de_matrix[i].astype(int))
                valid = True
                for defect in defects_set:
                    if meta_stabilizer[defect] == 1:
                        valid = False
                        break
                if not valid:
                    continue
                if meta_z_stabilizers:
                    prev = np.vstack(meta_z_stabilizers)
                    test = np.vstack([prev, meta_stabilizer])
                    if binary_matrix_rank(test) <= len(meta_z_stabilizers):
                        continue
                components = [z_keys[i] for i in range(n_z) if combination[i] == 1]
                meta_z_stabilizers.append(meta_stabilizer)
                meta_z_components.append(components)
    
    print(f"\nFound {len(meta_x_stabilizers)} linearly independent meta X stabilizers:")
    for i, components in enumerate(meta_x_components):
        print(f"  Meta X stabilizer {i+1}: combination of X stabilizers {components}")
    
    print(f"\nFound {len(meta_z_stabilizers)} linearly independent meta Z stabilizers:")
    for i, components in enumerate(meta_z_components):
        print(f"  Meta Z stabilizer {i+1}: combination of Z stabilizers {components}")
    
    return (meta_x_stabilizers, meta_x_components), (meta_z_stabilizers, meta_z_components)





def check_meta_stabilizers_defect_constraint(meta_stabilizers, defects_set):
    """
    Check that all meta stabilizers have zeros at all positions in defects_set.
    Args:
        meta_stabilizers (list of np.ndarray): List of meta stabilizer vectors.
        defects_set (list of int): Indices of defect positions.
    Returns:
        bool: True if all meta stabilizers meet the constraint, False otherwise.
    """
    for idx, stabilizer in enumerate(meta_stabilizers):
        for defect in defects_set:
            if stabilizer[defect] != 0:
                print(f"Meta stabilizer {idx} violates defect constraint at position {defect}.")
                return False
    print("All meta stabilizers meet the defect constraint.")
    return True


def gen_logicals_without_support_defects(code, defects_set, num_threads=10):
    """
    Generate logical operators with defects and without support.
    Returns a list of logical operators (as lists of qubit indices) that do not overlap with defects_set.
    Uses multi-threading to speed up the computation.
    
    Args:
        code: The BB code object
        defects_set: Set of defect qubit indices
        num_threads: Number of threads to use (default: 10)
    Returns:
        List of logical operators without support on defects
    """
    import concurrent.futures
    from functools import partial
    
    logical_z_ops = get_logical_ops_css(code.qcode.lz, code.k, code.m, code.n)
    z_stabilizers = transform_dictionary(code.z_stabilizers)
    
    logicals_no_defect = []
    
    def process_logical(logical):
        # Start with the original logical operator
        logical_vec = np.zeros(code.n*2, dtype=int)
        logical_vec[logical] = 1
        
        # Build stabilizer matrix
        stab_matrix = []
        stab_keys = []
        for key, qubits in z_stabilizers.items():
            row = np.zeros(code.n*2, dtype=int)
            row[qubits] = 1
            stab_matrix.append(row)
            stab_keys.append(key)
        stab_matrix = np.array(stab_matrix, dtype=int)
        
        # Try all combinations of stabilizers
        found = False
        
        # If there are too many stabilizers, we need to limit the search
        max_combinations = 2**20  # Limit to prevent memory issues
        total_combinations = 2**len(stab_matrix)
        step = max(1, total_combinations // max_combinations)
        
        for i in range(0, total_combinations, step):
            combo = np.array(list(np.binary_repr(i, width=len(stab_matrix))), dtype=int)
            candidate = logical_vec.copy()
            for j, use_stab in enumerate(combo):
                if use_stab:
                    candidate = np.bitwise_xor(candidate, stab_matrix[j])
            # Check if candidate has support on any defect
            if all(candidate[d] == 0 for d in defects_set):
                return np.where(candidate == 1)[0].tolist()
        
        print(f"Warning: No logical operator found without support on defects for logical {logical[:5]}...")
        return None
    
    # Use ThreadPoolExecutor to parallelize the computation
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(process_logical, logical_z_ops))
    
    # Filter out None results
    logicals_no_defect = [result for result in results if result is not None]
    
    return logicals_no_defect


def check_logicals_no_defect(code, logicals_no_defect, defects_set):
    """
    Check that the logical operators have no support on defects and commute with X stabilizers.
    
    Args:
        code: The BB code object
        logicals_no_defect: List of logical operators without support on defects
        defects_set: Set of defect qubit indices
    
    Returns:
        bool: True if all checks pass, False otherwise
    """
    # Check 1: No support on defects
    for i, logical in enumerate(logicals_no_defect):
        for defect in defects_set:
            if defect in logical:
                print(f"Logical operator {i} has support on defect {defect}")
                return False
    
    print("All logical operators have no support on defects ✓")
    
    # Check 2: Commutation with X stabilizers
    # Convert X stabilizers to matrix form
    x_stabilizers = transform_dictionary(code.x_stabilizers)
    
    for i, logical in enumerate(logicals_no_defect):
        logical_vec = np.zeros(code.n*2, dtype=int)
        logical_vec[logical] = 1
        
        for key, x_stab in x_stabilizers.items():
            x_stab_vec = np.zeros(code.n*2, dtype=int)
            x_stab_vec[x_stab] = 1
            
            # Check commutation by counting overlaps (should be even for commutation)
            overlap = np.sum(logical_vec * x_stab_vec) % 2
            if overlap != 0:
                print(f"Logical operator {i} does not commute with X stabilizer {key}")
                return False
    
    print("All logical operators commute with X stabilizers ✓")
    return True


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

    error_rate = 0.02
    # Get the defects_set used for meta stabilizer generation
    defects_set = generate_random_data_qubit_defects(code, error_rate)

    print("defects_set: ", defects_set)

    # Generate meta stabilizers using the same defects_set
    # (You may need to refactor gen_meta_stabilizers to accept defects_set as an argument for full determinism)
    meta_x_stabilizers, meta_z_stabilizers = gen_meta_stabilizers(code, defects_set)

    print("meta_x_stabilizers: ", meta_x_stabilizers[1])
    print("meta_z_stabilizers: ", meta_z_stabilizers[1])

    # Check constraints using the correct defects_set
    check_meta_stabilizers_defect_constraint(meta_x_stabilizers[0], defects_set)
    check_meta_stabilizers_defect_constraint(meta_z_stabilizers[0], defects_set)

    a, b, stb_keys = stabilizers_dq_def_check(code, defects_set)
    print("stb_keys: ", stb_keys)

    logicals_no_defect = gen_logicals_without_support_defects(code, defects_set)
    print("logicals_no_defect: ", logicals_no_defect)

    # After generating logicals_no_defect
    check_result = check_logicals_no_defect(code, logicals_no_defect, defects_set)
    print(f"Logical operators validation: {'Passed' if check_result else 'Failed'}")

    


