import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import itertools  # Add this import statement
from src.bb_code import BBCode
from parameters.code_config import get_config

"""
This script is used to find the redundancy of the checks in the BB codes.
"""

def find_dependent_rows(matrix):
    """
    Find which rows of the matrix are linearly dependent.
    
    Args:
        matrix: Input binary matrix
        
    Returns:
        dependent_rows: List of indices of linearly dependent rows
    """
    # Convert to numpy array and ensure it's binary (mod 2)
    matrix = np.array(matrix, dtype=int) % 2
    
    # Special case: empty matrix has no dependent rows
    if matrix.size == 0:
        return []
    
    # Get matrix shape
    num_rows, num_cols = matrix.shape
    
    # Create a copy for row reduction
    reduced_matrix = matrix.copy()
    
    # Track original row indices
    row_indices = np.arange(num_rows)
    
    # Row echelon form (reduced row echelon form)
    # Using a more robust implementation
    r = 0  # Current row
    pivot_cols = []  # Columns with pivots
    
    for c in range(num_cols):
        # Find a pivot in this column
        pivot_row = None
        for i in range(r, num_rows):
            if reduced_matrix[i, c] == 1:
                pivot_row = i
                break
                
        if pivot_row is None:
            continue  # No pivot in this column
            
        # Swap rows if needed
        if pivot_row != r:
            reduced_matrix[[r, pivot_row]] = reduced_matrix[[pivot_row, r]]
            row_indices[[r, pivot_row]] = row_indices[[pivot_row, r]]
            
        # Record this pivot position
        pivot_cols.append(c)
        
        # Eliminate all other entries in this column
        for i in range(num_rows):
            if i != r and reduced_matrix[i, c] == 1:
                reduced_matrix[i] = (reduced_matrix[i] + reduced_matrix[r]) % 2
        
        r += 1
        if r == num_rows:
            break
    
    # Rows that didn't get pivots are dependent
    independent_rows = r
    dependent_rows = [int(row_indices[i]) for i in range(independent_rows, num_rows)]
    
    # Also identify rows that are all zeros
    for i in range(num_rows):
        if np.all(reduced_matrix[i] == 0) and row_indices[i] not in dependent_rows:
            dependent_rows.append(int(row_indices[i]))
    
    return sorted(dependent_rows)


def find_row_dependencies(matrix, dependent_row_idx):
    """
    Find which rows a dependent row depends on.
    
    Args:
        matrix: Input binary matrix
        dependent_row_idx: Index of the dependent row
        
    Returns:
        dependencies: List of row indices that the dependent row is a linear combination of,
                     or None if the row is not dependent
    """
    # Make matrix copy to avoid modifying original
    matrix = np.array(matrix, dtype=int)
    num_rows, num_cols = matrix.shape
    
    # Create augmented matrix - original matrix plus identity matrix
    aug = np.zeros((num_rows, num_cols + num_rows), dtype=int)
    aug[:, :num_cols] = matrix
    for i in range(num_rows):
        aug[i, num_cols + i] = 1
    
    # Gaussian elimination to row echelon form
    r = 0
    for c in range(num_cols):
        # Find pivot
        pivot_found = False
        for i in range(r, num_rows):
            if aug[i, c] == 1:
                pivot_found = True
                if i != r:
                    aug[[r, i]] = aug[[i, r]]
                break
        
        if not pivot_found:
            continue
        
        # Eliminate in other rows
        for i in range(num_rows):
            if i != r and aug[i, c] == 1:
                aug[i] = np.bitwise_xor(aug[i], aug[r])
        
        r += 1
        if r == num_rows:
            break
    
    # If the row is dependent, its original matrix part will be all zeros
    if not np.any(aug[dependent_row_idx, :num_cols]):
        # Row is dependent - find which rows it depends on
        dependencies = []
        for j in range(num_rows):
            if aug[dependent_row_idx, num_cols + j] == 1 and j != dependent_row_idx:
                dependencies.append(j)
        return dependencies
    else:
        # Row is not dependent
        return None


def find_all_dependencies(matrix):
    """
    Find all dependent rows and their dependencies.
    
    Args:
        matrix: Input binary matrix
        
    Returns:
        dependency_dict: Dictionary mapping each dependent row to its dependencies
    """
    # Find which rows are dependent
    dependent_rows = find_dependent_rows(matrix)
    
    # For each dependent row, find its dependencies
    dependency_dict = {}
    for row_idx in dependent_rows:
        dependencies = find_row_dependencies(matrix, row_idx)
        if dependencies:  # Skip if somehow no dependencies found
            dependency_dict[row_idx] = dependencies
    
    return dependency_dict


def verify_dependency(matrix, redundant_idx, dependency_indices):
    """
    Verify that a redundant row is indeed the sum of its claimed dependencies.
    
    Args:
        matrix: The matrix to check
        redundant_idx: Index of the redundant row
        dependency_indices: Indices of rows that the redundant row depends on
        
    Returns:
        is_valid: True if the dependency is valid, False otherwise
    """
    # Get the redundant row
    redundant_row = matrix[redundant_idx]
    
    # Compute the sum of dependency rows (in GF(2))
    computed_row = np.zeros_like(redundant_row)
    for idx in dependency_indices:
        computed_row = np.bitwise_xor(computed_row, matrix[idx])
    
    # Check if they match
    return np.array_equal(redundant_row, computed_row)


def analyze_matrix_dependencies(matrix):
    """
    Analyze a matrix to find and verify dependent rows.
    
    Args:
        matrix: Input binary matrix
        
    Returns:
        redundant_rows: List of indices of verified redundant rows
        dependencies: Dictionary mapping redundant rows to their dependencies
    """
    # Find all dependencies first
    dependencies = find_all_dependencies(matrix)
    
    # Verify each dependency
    verified_dependencies = {}
    for row_idx, deps in dependencies.items():
        if verify_dependency(matrix, row_idx, deps):
            verified_dependencies[row_idx] = deps
            print(f"Row {row_idx} is dependent: equals sum of rows {deps}")
        else:
            print(f"Row {row_idx} dependencies could not be verified")
    
    # Return the verified redundant rows and their dependencies
    redundant_rows = sorted(list(verified_dependencies.keys()))
    return redundant_rows, verified_dependencies


def find_check_redundancy(code):
    """
    Find redundant checks in BB code check matrices.
    
    Args:
        code: BBCode object containing the check matrices
    
    Returns:
        redundant_x_checks: list of indices of redundant X checks
        redundant_z_checks: list of indices of redundant Z checks
        x_dependencies: dictionary mapping redundant X checks to their dependencies
        z_dependencies: dictionary mapping redundant Z checks to their dependencies
    """
    # First, print matrix shapes for verification
    print(f"X check matrix shape: {code.hx.shape}")
    print(f"Z check matrix shape: {code.hz.shape}")
    
    # Direct calculation of matrix rank to verify our approach
    x_rank = np.linalg.matrix_rank(code.hx % 2)
    z_rank = np.linalg.matrix_rank(code.hz % 2)
    
    print(f"X check matrix rank: {x_rank} (should have {code.hx.shape[0] - x_rank} redundant rows)")
    print(f"Z check matrix rank: {z_rank} (should have {code.hz.shape[0] - z_rank} redundant rows)")
    
    print("\n=== Analyzing X Check Matrix ===")
    
    # First try direct method to find dependent rows
    x_dependent_rows = find_dependent_rows(code.hx)
    print(f"Found {len(x_dependent_rows)} dependent X checks: {x_dependent_rows}")
    
    # Then analyze fully
    redundant_x_checks, x_dependencies = analyze_matrix_dependencies(code.hx)
    
    print("\n=== Analyzing Z Check Matrix ===")
    
    # First try direct method to find dependent rows
    z_dependent_rows = find_dependent_rows(code.hz)
    print(f"Found {len(z_dependent_rows)} dependent Z checks: {z_dependent_rows}")
    
    # Then analyze fully
    redundant_z_checks, z_dependencies = analyze_matrix_dependencies(code.hz)
    
    # Print summary
    print(f"\nFound {len(redundant_x_checks)} redundant X checks out of {code.hx.shape[0]} total")
    print(f"Found {len(redundant_z_checks)} redundant Z checks out of {code.hz.shape[0]} total")
    
    # Look more closely at specific checks - we expect indices 50-53 to be redundant
    expected_redundant = [50, 51, 52, 53]
    
    print("\nDetailed analysis of expected redundant checks (50-53):")
    
    for check_idx in expected_redundant:
        print(f"\nAnalyzing X check {check_idx}:")
        # Try to find a small subset of checks that this check depends on
        for i in range(1, 5):  # Try combinations of 1-4 other checks
            for combo in itertools.combinations(range(code.hx.shape[0]), i):
                if check_idx in combo:
                    continue  # Skip combinations containing the check itself
                
                # Compute linear combination
                combined_row = np.zeros_like(code.hx[0])
                for idx in combo:
                    combined_row = np.bitwise_xor(combined_row, code.hx[idx])
                
                # Check if it equals our target check
                if np.array_equal(combined_row, code.hx[check_idx]):
                    print(f"  X check {check_idx} = X check {' + X check '.join(map(str, combo))}")
                    break
            else:
                continue
            break
        
        print(f"\nAnalyzing Z check {check_idx}:")
        # Try to find a small subset of checks that this check depends on
        for i in range(1, 5):  # Try combinations of 1-4 other checks
            for combo in itertools.combinations(range(code.hz.shape[0]), i):
                if check_idx in combo:
                    continue  # Skip combinations containing the check itself
                
                # Compute linear combination
                combined_row = np.zeros_like(code.hz[0])
                for idx in combo:
                    combined_row = np.bitwise_xor(combined_row, code.hz[idx])
                
                # Check if it equals our target check
                if np.array_equal(combined_row, code.hz[check_idx]):
                    print(f"  Z check {check_idx} = Z check {' + Z check '.join(map(str, combo))}")
                    break
            else:
                continue
            break
    
    return redundant_x_checks, redundant_z_checks, x_dependencies, z_dependencies


# Example of using the functions with a custom matrix
def demo_with_custom_matrix():
    # Create multiple example matrices to test different dependency scenarios
    
    # Example 1: Row 2 = Row 0 + Row 1, and Row 3 = Row 2
    print("Example 1: Simple dependencies")
    example_matrix1 = np.array([
        [1, 0, 1, 0],  # Row 0
        [0, 1, 1, 0],  # Row 1
        [1, 1, 0, 0],  # Row 2 = Row 0 + Row 1
        [1, 1, 0, 0]   # Row 3 = Row 2 (or Row 0 + Row 1)
    ])
    
    print("Example Matrix:")
    print(example_matrix1)
    
    print("\nAnalyzing matrix dependencies:")
    redundant_rows, dependencies = analyze_matrix_dependencies(example_matrix1)
    
    print(f"\nFound {len(redundant_rows)} redundant rows: {redundant_rows}")
    for idx in redundant_rows:
        deps = dependencies[idx]
        expression = " + ".join([f"Row{i}" for i in deps]) + f" = Row{idx}"
        print(f"  Row {idx} dependencies: {expression}")
    
    # Example 2: Explicitly test Row 3 = Row 0 + Row 1 (verify transitive dependencies)
    print("\n\nExample 2: Testing complex dependencies")
    example_matrix2 = np.array([
        [1, 0, 1, 0, 1],  # Row 0
        [0, 1, 0, 1, 1],  # Row 1
        [0, 0, 1, 1, 0],  # Row 2 (independent)
        [1, 1, 1, 1, 0]   # Row 3 = Row 0 + Row 1
    ])
    
    print("Example Matrix:")
    print(example_matrix2)
    
    print("\nAnalyzing matrix dependencies:")
    redundant_rows2, dependencies2 = analyze_matrix_dependencies(example_matrix2)
    
    print(f"\nFound {len(redundant_rows2)} redundant rows: {redundant_rows2}")
    for idx in redundant_rows2:
        deps = dependencies2[idx]
        expression = " + ".join([f"Row{i}" for i in deps]) + f" = Row{idx}"
        print(f"  Row {idx} dependencies: {expression}")


if __name__ == "__main__":
    # Choose which functionality to run
    run_demo = False # Set to False to analyze BB code instead
    
    if run_demo:
        demo_with_custom_matrix()
    else:
        print("Finding redundant checks in BB code")
        code_setting = 4
        code_config = get_config(code_setting)
        code_input_params = code_config.get_params()
        code = BBCode(code_input_params)
        redundant_x, redundant_z, x_deps, z_deps = find_check_redundancy(code)