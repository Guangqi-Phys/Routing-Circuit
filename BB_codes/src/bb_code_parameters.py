## Credit to Bravyi et al.
import numpy as np
try:
	from pyscipopt import Model, quicksum
except ImportError:
	print("Error importing pyscipopt. Please run this script in the 'scipopt' conda environment.")
	print("Use: conda activate scipopt")
	import sys
	sys.exit(1)
from bposd.css import css_code



def get_minimal_logical_length(logical_operators):
    """
    Calculate the minimal length of logical operators in a sparse matrix.
    
    Args:
        logical_operators: A sparse matrix where each row represents a logical operator
        
    Returns:
        int: The minimal length (number of non-zero elements) among all logical operators
    """
    # Check if the input is a sparse matrix
    if not hasattr(logical_operators, 'getnnz'):
        raise ValueError("Input must be a sparse matrix")
    
    # Get the number of rows (number of logical operators)
    num_logicals = logical_operators.shape[0]
    
    # Initialize with a large value
    min_length = float('inf')
    min_index = -1
    
    # Calculate the length of each logical operator
    for i in range(num_logicals):
        # Get the number of non-zero elements in this row
        length = logical_operators.getrow(i).count_nonzero()
        
        # Update minimum if this is shorter
        if length < min_length:
            min_length = length
            min_index = i
    
    return min_length


def convert_logical_layout(logical_operator, m, n):
    """
    Convert logical operator indices to match the code layout.
    
    This function transforms the logical operator indices from the mathematical
    representation to the actual qubit indices in the physical layout.
    
    Args:
        logical_operator (list): List of indices representing a logical operator
		m: code.m
		n: code.n
        
    Returns:
        list: Converted logical operator with indices matching the physical layout
    """
    converted_logical = []
    for idx in logical_operator:
        if idx < n/2:
            converted_idx = (2*m+(idx//m)*4*m+(idx+2*m-1)%m*2+1)%(n*2) 
            converted_logical.append(int(converted_idx))
        else:
            idx = idx - n/2
            converted_idx = ((idx//m)*4*m+idx%m*2)%(n*2)
            converted_logical.append(int(converted_idx))
    return converted_logical



def transform_dictionary(input_dict):
    """
    Transform a dictionary with tuple keys (a, b) to a dictionary with tuple keys (a,)
    where the values are lists of elements grouped by the first element of the original keys.
    
    Args:
        input_dict (dict): Dictionary with keys in format (a, b) and any values
        
    Returns:
        dict: Dictionary with keys in format (a,) and values as lists
        
    Example:
        Input: {(12, 0): 0, (12, 1): 13, (12, 2): 24, (14, 0): 2, (14, 1): 15}
        Output: {(12): [0, 13, 24], (14): [2, 15]}
    """
    output_dict = {}
    
    # Iterate through each key-value pair in the input dictionary
    for (a, b), value in input_dict.items():
        # Create a single-element tuple key
        new_key = (a)
        
        # If the key doesn't exist in the output dictionary yet, initialize it with an empty list
        if new_key not in output_dict:
            output_dict[new_key] = []
        
        # Append the value to the list associated with the key
        output_dict[new_key].append(value)
    
    return output_dict

# computes the minimum Hamming weight of a binary vector x such that 
# stab @ x = 0 mod 2
# logicOp @ x = 1 mod 2
# here stab is a binary matrix and logicOp is a binary vector
def logical_operator_and_distance_compute(stab,logicOp):
	# number of qubits
	n = stab.shape[1]
	# number of stabilizers
	m = stab.shape[0]

	# maximum stabilizer weight
	wstab = np.max([np.sum(stab[i,:]) for i in range(m)])
	# weight of the logical operator
	wlog = np.sum(logicOp)
	# how many slack variables are needed to express orthogonality constraints modulo two
	num_anc_stab = int(np.ceil(np.log2(wstab)))
	num_anc_logical = int(np.ceil(np.log2(wlog)))
	# total number of variables
	num_var = n + m*num_anc_stab + num_anc_logical

	model = Model("distance")
	model.hideOutput()
	
    # Set numerical parameters to improve stability
	model.setRealParam('numerics/feastol', 1e-9)
	model.setRealParam('numerics/epsilon', 1e-9)
	model.setRealParam('numerics/sumepsilon', 1e-9)
	

	x = [model.addVar(vtype="B") for i in range(num_var)]
	
	# Set objective: minimize sum of first n variables
	model.setObjective(quicksum(x[i] for i in range(n)))

	# orthogonality to rows of stab constraints
	for row in range(m):
		weight = [0]*num_var
		supp = np.nonzero(stab[row,:])[0]
		for q in supp:
			weight[q] = 1
		cnt = 1
		for q in range(num_anc_stab):
			weight[n + row*num_anc_stab +q] = -(1<<cnt)
			cnt += 1
		model.addCons(quicksum(weight[i] * x[i] for i in range(num_var)) == 0)

	# odd overlap with logicOp constraint
	supp = logicOp.nonzero()[1]  # Changed to get column indices for sparse matrix
	weight = [0]*num_var
	for q in supp:
		weight[q] = 1
	cnt = 1
	for q in range(num_anc_logical):
			weight[n + m*num_anc_stab +q] = -(1<<cnt)
			cnt += 1
	model.addCons(quicksum(weight[i] * x[i] for i in range(num_var)) == 1)

	model.optimize()

	if model.getStatus() == "optimal":
		# Get the solution vector (first n components only, as these represent the actual qubits)
		solution = [model.getVal(x[i]) for i in range(n)]
		
		threshold = 0.5
		rounded_solution = [1 if val > threshold else 0 for val in solution]
		nonzero_positions = [i for i in range(n) if rounded_solution[i] > 0]
		# print("Nonzero positions:", nonzero_positions)
		nonzero_logicOp = logicOp.nonzero()[1].tolist()  # for sparse matrix, use nonzero()[1]
		# print("Logical operator:", logicOp.toarray().tolist())
		# print("Logical operator nonzero positions:", nonzero_logicOp)
		
		opt_val = sum(model.getVal(x[i]) for i in range(n))
		return int(opt_val), nonzero_positions
	else:
		raise RuntimeError("Problem could not be solved to optimality")


# Define the function outside any class for multiprocessing
def compute_logical_operator(args):
    """
    Standalone function to compute a logical operator
    
    Args:
        args: Tuple containing (hx_matrix, logical_operator, l_value, index)
        
    Returns:
        Tuple of (index, weight, converted_logical)
    """
    hx_matrix, logical_operator, m_value, n_value, idx = args
    w, z_logical_operator = logical_operator_and_distance_compute(hx_matrix, logical_operator)
    # converted_logical = convert_logical_layout(z_logical_operator, m_value, n_value)
    return idx, w, z_logical_operator

def gen_z_logical_operator(stab,logicOp):
	# number of qubits
	n = stab.shape[1]
	# number of stabilizers
	m = stab.shape[0]

	# maximum stabilizer weight
	wstab = np.max([np.sum(stab[i,:]) for i in range(m)])
	# weight of the logical operator
	wlog = np.sum(logicOp)
	# how many slack variables are needed to express orthogonality constraints modulo two
	num_anc_stab = int(np.ceil(np.log2(wstab)))
	num_anc_logical = int(np.ceil(np.log2(wlog)))
	# total number of variables
	num_var = n + m*num_anc_stab + num_anc_logical

	model = Model("distance")
	model.hideOutput()
	
	# Set numerical parameters to improve stability
	model.setRealParam('numerics/feastol', 1e-9)
	model.setRealParam('numerics/epsilon', 1e-9)
	model.setRealParam('numerics/sumepsilon', 1e-9)
	
	x = [model.addVar(vtype="B") for i in range(num_var)]
	
	# Set objective: minimize sum of first n variables
	model.setObjective(quicksum(x[i] for i in range(n)))

	# orthogonality to rows of stab constraints
	for row in range(m):
		weight = [0]*num_var
		supp = np.nonzero(stab[row,:])[0]
		for q in supp:
			weight[q] = 1
		cnt = 1
		for q in range(num_anc_stab):
			weight[n + row*num_anc_stab +q] = -(1<<cnt)
			cnt+=1
		model.addCons(quicksum(weight[i] * x[i] for i in range(num_var)) == 0)

	# odd overlap with logicOp constraint
	supp = logicOp.nonzero()[1]  # Changed to get column indices for sparse matrix
	weight = [0]*num_var
	for q in supp:
		weight[q] = 1
	cnt = 1
	for q in range(num_anc_logical):
			weight[n + m*num_anc_stab +q] = -(1<<cnt)
			cnt+=1
	model.addCons(quicksum(weight[i] * x[i] for i in range(num_var)) == 1)

	model.optimize()

	if model.getStatus() == "optimal":
		# Get the solution vector (first n components only, as these represent the actual qubits)
		solution = [model.getVal(x[i]) for i in range(n)]
		# print("Solution vector x (first n components):", solution)
		
		# Use a threshold to determine which values are actually 1 (handling floating point precision issues)
		threshold = 0.5
		rounded_solution = [1 if val > threshold else 0 for val in solution]
		nonzero_positions = [i for i in range(n) if rounded_solution[i] > 0]
		
		# print("Rounded solution vector:", rounded_solution)
		# print("Nonzero positions:", nonzero_positions)
		nonzero_logicOp = logicOp.nonzero()[1].tolist()  # for sparse matrix, use nonzero()[1]
		# print("Logical operator:", logicOp.toarray().tolist())
		# print("Logical operator nonzero positions:", nonzero_logicOp)
		
		# Use the rounded solution for the optimal value calculation
		opt_val = sum(rounded_solution)
		return nonzero_positions
	else:
		raise RuntimeError("Problem could not be solved to optimality")


def sparse_to_dense_without_row(sparse_matrix, row_to_exclude):
    """
    Convert a sparse matrix to a dense matrix, excluding a specific row.
    
    Args:
        sparse_matrix: A scipy sparse matrix (CSR format)
        row_to_exclude: The index of the row to exclude
        
    Returns:
        numpy.ndarray: A dense matrix without the specified row
    """
    if row_to_exclude < 0 or row_to_exclude >= sparse_matrix.shape[0]:
        raise ValueError(f"Row index {row_to_exclude} out of bounds for matrix with {sparse_matrix.shape[0]} rows")
    
    # Get the total number of rows
    num_rows = sparse_matrix.shape[0]
    
    # Create a list of row indices to keep (all except the one to exclude)
    rows_to_keep = [i for i in range(num_rows) if i != row_to_exclude]
    
    # Extract the submatrix with only the rows we want to keep
    submatrix = sparse_matrix[rows_to_keep, :]
    
    # Convert to dense format
    dense_matrix = submatrix.toarray()
    
    return dense_matrix

# ... existing code ...

def get_logical_ops_css(sparse_matrix, k, m, n):
    """
    Extract all column indices where the specified row has non-zero values.
    
    Args:
        sparse_matrix: A scipy sparse matrix in CSR format
        row_index: The row index to extract column indices from (default: 0)
        
    Returns:
        list: A list of column indices where the specified row has non-zero values
    """
    
    # Get the slice of the row
    
    # Get the column indices where values are non-zero
    col_indices = []
    converted_logicals = []
    for i in range(k):
        col_indices = (sparse_matrix[i,:].nonzero()[1])
        converted_logicals.append(convert_logical_layout(col_indices, m, n))
    
    # Convert to a regular Python list and return
    return converted_logicals





