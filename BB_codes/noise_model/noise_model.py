import numpy as np
import stim

def standard_depolarizing_noise_model(
        circuit: stim.Circuit, 
        full_qubit_set: list, 
        probability: float) -> stim.Circuit:
    """
    Applies a standard depolarizing noise model to a Stim circuit.
    
    This noise model simulates common quantum errors including:
    - Depolarizing noise on single-qubit gates
    - Depolarizing noise on two-qubit gates
    - Measurement errors
    - State preparation errors
    
    Args:
        circuit (stim.Circuit): The input quantum circuit
        probability (float): Base error probability for all noise operations
        
    Returns:
        stim.Circuit: A new circuit with noise operations inserted
    """
    n = circuit.num_qubits
    result = stim.Circuit()
    
    for instruction in circuit:
        # Handle nested repeat blocks recursively
        if isinstance(instruction, stim.CircuitRepeatBlock):
            result.append(stim.CircuitRepeatBlock(
                repeat_count=instruction.repeat_count,
                body=standard_depolarizing_noise_model(instruction.body_copy(), full_qubit_set=full_qubit_set,
                                                        probability=probability)))
        # Add Z errors after R gates (rotation around Z axis)
        elif instruction.name == 'R':
            result.append(instruction)
            result.append('Z_ERROR', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Add X errors after RX gates (rotation around X axis)
        elif instruction.name == 'RX':
            result.append(instruction)
            result.append('X_ERROR', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Add measurement errors: Z error before measurement and depolarizing after
        elif instruction.name == 'M':
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append(instruction)
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Add two-qubit depolarizing noise after CNOT gates
        elif instruction.name == 'CX':
            result.append(instruction)
            result.append('DEPOLARIZE2', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Add measurement errors for MR gates (measure and reset)
        elif instruction.name == 'MR':
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append(instruction)
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Add measurement errors for MRX gates (measure and reset with X rotation)
        elif instruction.name == 'MRX':
            result.append('X_error', instruction.targets_copy(), probability)
            result.append(instruction)
            result.append('X_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Pass through other instructions unchanged
        else:
            result.append(instruction)
    return result

def si1000_noise_model(
        circuit: stim.Circuit, 
        full_qubit_set: list, 
        probability: float) -> stim.Circuit:
    """
    Applies the SI1000 noise model to a Stim circuit.
    
    This is a specialized noise model with different error rates for different operations:
    - Higher error rates for measurement operations (5x base probability)
    - Lower error rates for two-qubit gates (1/10x base probability)
    - Double error rates for rotation gates (2x base probability)
    
    Args:
        circuit (stim.Circuit): The input quantum circuit
        probability (float): Base error probability for all noise operations
        
    Returns:
        stim.Circuit: A new circuit with noise operations inserted
    """
    n = circuit.num_qubits
    result = stim.Circuit()
    
    for instruction in circuit:
        # Handle nested repeat blocks recursively
        if isinstance(instruction, stim.CircuitRepeatBlock):
            result.append(stim.CircuitRepeatBlock(
                repeat_count=instruction.repeat_count,
                body=si1000_noise_model(instruction.body_copy(), full_qubit_set = full_qubit_set,
                                                        probability=probability)))
        # Add Z errors after R gates with double probability
        elif instruction.name == 'R':
            result.append(instruction)
            result.append('Z_ERROR', instruction.targets_copy(), 2*probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), 2*probability)
        # Add X errors after RX gates with double probability
        elif instruction.name == 'RX':
            result.append(instruction)
            result.append('X_ERROR', instruction.targets_copy(), 2*probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), 2*probability)
        # Add measurement errors with 5x probability before and 1x after
        elif instruction.name == 'M':
            result.append('Z_error', instruction.targets_copy(), 5*probability)
            result.append(instruction)
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), 2*probability)
        # Add reduced depolarizing noise after CNOT gates
        elif instruction.name == 'CX':
            result.append(instruction)
            result.append('DEPOLARIZE2', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability/10)
        # Add measurement errors for MR gates with 5x probability before and 1x after
        elif instruction.name == 'MR':
            result.append('Z_error', instruction.targets_copy(), 5*probability)
            result.append(instruction)
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), 2*probability)
        # Add measurement errors for MRX gates with 5x probability before and 1x after
        elif instruction.name == 'MRX':
            result.append('X_error', instruction.targets_copy(), 5*probability)
            result.append(instruction)
            result.append('X_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), 2*probability)
        # Pass through other instructions unchanged
        else:
            result.append(instruction)
    return result

# def with_dephasing_before_ticks(
#         circuit: stim.Circuit, 
#         *, 
#         probability: float) -> stim.Circuit:
#     """
#     Applies dephasing noise before each TICK instruction in a Stim circuit.
    
#     This noise model simulates time-dependent dephasing by adding Z errors
#     to all qubits before each TICK instruction, which represents a unit of time
#     in the circuit.
    
#     Args:
#         circuit (stim.Circuit): The input quantum circuit
#         probability (float): Error probability for the dephasing noise
        
#     Returns:
#         stim.Circuit: A new circuit with dephasing noise inserted before TICKs
#     """
#     n = circuit.num_qubits
#     result = stim.Circuit()
    
#     for instruction in circuit:
#         # Handle nested repeat blocks recursively
#         if isinstance(instruction, stim.CircuitRepeatBlock):
#             result.append(stim.CircuitRepeatBlock(
#                 repeat_count=instruction.repeat_count,
#                 body=with_dephasing_before_ticks(instruction.body_copy(),
#                                                  probability=probability)))
#         # Add Z errors to all qubits before each TICK
#         elif instruction.name == 'TICK':
#             result.append('Z_ERROR', range(n), probability)
#             result.append(instruction)
#         # Pass through other instructions unchanged
#         else:
#             result.append(instruction)
#     return result