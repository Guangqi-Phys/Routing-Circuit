import numpy as np
from .bb_code import BBCode
from bposd.css import css_code


def check_logical_operator_converted(x_stabilizers, logical_operators):
    """
    Check if the logical operator is a valid logical operator for the code.
    
    A valid logical operator must have even overlap with all stabilizers.
    This means for each stabilizer, the number of qubits that are both in the
    stabilizer and the logical operator must be even (including zero).
    
    Args:
        x_stabilizers (dict): Dictionary mapping (stabilizer_index, position) to qubit indices
        logical_operators (list): List of lists, where each inner list contains qubit indices
                                 for a logical operator
    
    Returns:
        str or tuple: "check done" if all logical operators have even overlap with all stabilizers,
                     otherwise returns (failed_logical_ops, failed_stabilizers) containing the
                     logical operators and stabilizers that don't meet the parity constraint
    """
    # Group stabilizers by their index
    stabilizer_groups = {}
    for (stab_idx, _), qubit_idx in x_stabilizers.items():
        if stab_idx not in stabilizer_groups:
            stabilizer_groups[stab_idx] = []
        stabilizer_groups[stab_idx].append(qubit_idx)
    
    failed_logical_ops = []
    failed_stabilizers = []
    
    # Check each logical operator against all stabilizers
    for log_op_idx, logical_op in enumerate(logical_operators):
        logical_op_set = set(logical_op)
        
        for stab_idx, stabilizer_qubits in stabilizer_groups.items():
            # Count the overlap between the stabilizer and logical operator
            overlap_count = sum(1 for qubit in stabilizer_qubits if qubit in logical_op_set)
            
            # Check if the overlap is odd (invalid)
            if overlap_count % 2 != 0:
                failed_logical_ops.append(log_op_idx)
                failed_stabilizers.append(stab_idx)
                print(f"Logical operator {log_op_idx} has odd overlap ({overlap_count}) with stabilizer {stab_idx}")
    
    if not failed_logical_ops:
        return "check done"
    else:
        # Return unique failures
        return (list(set(failed_logical_ops)), list(set(failed_stabilizers)))
    

def check_logical_operator_from_integer_programing(hx, logical_operators):
    """
    Check if the logical operators are valid logical operators for the code.
    
    A valid logical operator must commute with all stabilizers.
    This means for each stabilizer, hx * logical_operator must be 0 (mod 2).
    
    Args:
        hx (numpy.ndarray): The X-type stabilizer check matrix
        logical_operators (list or numpy.ndarray): Either a list of logical operators, where each is a list of indices 
                                  where the logical operator acts (e.g., [2, 3, 5]), or a single logical operator
                                  as a binary vector or list of indices
        
    Returns:
        bool: True if all logical operators are valid, False otherwise
    """
    n = hx.shape[1]  # Number of qubits
    
    # Handle the case where logical_operators is a single logical operator (not a list of logical operators)
    if isinstance(logical_operators, np.ndarray) and logical_operators.ndim == 1:
        # Already a binary vector
        binary_vector = logical_operators
        result = np.dot(hx, binary_vector) % 2
        if np.any(result):
            print(f"Found invalid logical operator: {np.where(binary_vector == 1)[0]}")
            print(f"Result of hx * logical_op: {result}")
            return False
        return True
    
    # Handle the case where logical_operators is a list of indices for a single logical operator
    if isinstance(logical_operators, list) and (len(logical_operators) == 0 or not isinstance(logical_operators[0], (list, np.ndarray))):
        binary_vector = np.zeros(n, dtype=int)
        for idx in logical_operators:
            binary_vector[idx] = 1
        
        result = np.dot(hx, binary_vector) % 2
        if np.any(result):
            print(f"Found invalid logical operator: {logical_operators}")
            print(f"Result of hx * logical_op: {result}")
            return False
        return True
    
    # Handle the case where logical_operators is a list of logical operators
    for i, logical_op_indices in enumerate(logical_operators):
        # Convert index list to binary vector
        binary_vector = np.zeros(n, dtype=int)
        for idx in logical_op_indices:
            binary_vector[idx] = 1
        
        # Compute hx * logical_operator (mod 2)
        result = np.dot(hx, binary_vector) % 2
        
        # Check if any element is non-zero
        if np.any(result):
            print(f"Found invalid logical operator {i}: {logical_op_indices}")
            print(f"Result of hx * logical_op: {result}")
            return False
            
    return True

