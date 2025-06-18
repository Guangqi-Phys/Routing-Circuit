import random
import numpy as np

# Set random seed for reproducibility
np_random = np.random.RandomState(seed=8)



def apply_z_coupler_dropout_fixed_50per(z_stabilizer_dict):
    """
    Apply dropout to stabilizers based on an error rate.
    For each stabilizer, randomly delete one of the last two elements with probability given by error_rate.
    
    Args:
        z_stabilizer_dict (dict): Dictionary with keys in format (a,) and values as lists of length 6
        error_rate (float): Probability (between 0 and 1) of applying the dropout
        
    Returns:
        dict: Dictionary with a new key (a,b) where b is the index of the removed element, if b=0 then the element is not removed
        
    Example:
        Input: {(12,): [0, 13, 24, 23, 93, 198], (14,): [2, 15, 26, 13, 95, 200]}, error_rate=0.5
        Output might be: {(12,-1): [0, 13, 24, 23, 93], (14,-2): [2, 15, 26, 13, 200]}
        (element 198 was removed from first stabilizer and 95 from second)
    """
    result_dict = {}
    
    for key, elements in z_stabilizer_dict.items():
        
        # Make a copy of the elements list
        new_elements = elements.copy()
        
        index_to_remove = -2

        new_key = (key, index_to_remove)
        result_dict[new_key] = new_elements

    
    # also retrn all the keys with defects
    keys_with_defect = []
    for (a,b), elements in result_dict.items():
        if b != 0:
            keys_with_defect.append(a)
    
    return result_dict, keys_with_defect

def apply_x_coupler_dropout_fixed_50per(x_stabilizer_dict):
    """
    Apply dropout to stabilizers based on an error rate.
    For each stabilizer, randomly delete one of the last two elements with probability given by error_rate.
    
    Args:
        z_stabilizer_dict (dict): Dictionary with keys in format (a,) and values as lists of length 6
        error_rate (float): Probability (between 0 and 1) of applying the dropout
        
    Returns:
        dict: Dictionary with a new key (a,b) where b is the index of the removed element, if b=0 then the element is not removed
        
    Example:
        Input: {(12,): [0, 13, 24, 23, 93, 198], (14,): [2, 15, 26, 13, 95, 200]}, error_rate=0.5
        Output might be: {(12,-1): [0, 13, 24, 23, 93], (14,-2): [2, 15, 26, 13, 200]}
        (element 198 was removed from first stabilizer and 95 from second)
    """
    result_dict = {}
    
    for key, elements in x_stabilizer_dict.items():
        
        # Make a copy of the elements list
        new_elements = elements.copy()
        
        index_to_remove = -2

        new_key = (key, index_to_remove)
        result_dict[new_key] = new_elements

    
    # also retrn all the keys with defects
    keys_with_defect = []
    for (a,b), elements in result_dict.items():
        if b != 0:
            keys_with_defect.append(a)
    
    return result_dict, keys_with_defect

