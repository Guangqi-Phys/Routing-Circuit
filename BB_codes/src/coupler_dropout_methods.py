import random
import numpy as np

# Set random seed for reproducibility
np_random = np.random.RandomState(seed=8)


def apply_z_coupler_dropout(z_stabilizer_dict, error_rate):
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
        
        # Apply dropout with probability error_rate
        if np_random.random() < error_rate:
            # Decide which of the last two elements to remove (either -1 or -2 index)
            index_to_remove = np_random.choice([-1, -2])
            # Remove the element at that index
            # del new_elements[index_to_remove]
            new_key = (key, index_to_remove)
            result_dict[new_key] = new_elements
        else:
            new_key = (key, 0)
            result_dict[new_key] = new_elements
    
    # also retrn all the keys with defects
    keys_with_defect = []
    for (a,b), elements in result_dict.items():
        if b != 0:
            keys_with_defect.append(a)
    
    return result_dict, keys_with_defect


def apply_x_coupler_dropout(x_stabilizer_dict, z_keys_with_defect,x_ancilla_labels,corresponding_z_ancilla, error_rate):
    """
    Apply dropout to stabilizers based on an error rate.
    For each x stabilizer, randomly delete one of the last two elements with probability given by error_rate.
    
    Notice that if the corresponding z stabilizer is already deleted, then the x stabilizer will not be deleted, other wise we can not design stabilizer measurement circuit.
    """
    result_dict = {}
    
    for key, elements in x_stabilizer_dict.items():
        # get the corresponding z stabilizer
        corr_key = corresponding_z_ancilla[x_ancilla_labels.index(key)]
        # check if the corresponding z stabilizer has defect
        if corr_key not in z_keys_with_defect:

            # Make a copy of the elements list
            new_elements = elements.copy()
        
            # Apply dropout with probability error_rate
            if np_random.random() < error_rate:
                # Decide which of the last two elements to remove (either -1 or -2 index)
                index_to_remove = np_random.choice([-1, -2])
                # Remove the element at that index
                # del new_elements[index_to_remove]
                new_key = (key, index_to_remove)
                result_dict[new_key] = new_elements
            else:
                new_key = (key, 0)
                result_dict[new_key] = new_elements
        else:
            new_key = (key, 0)
            result_dict[new_key] = elements

        #also retrn all the keys with defects
    keys_with_defect = []
    for (a,b), elements in result_dict.items():
        if b != 0:
            keys_with_defect.append(a)
    
    return result_dict, keys_with_defect   


def apply_z_coupler_dropout_fixed(z_stabilizer_dict):
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




# Example usage
if __name__ == "__main__":
    # Sample input dictionary
    input_dict = {
        (12): [0, 13, 24, 23, 93, 198],
        (14): [2, 15, 26, 13, 95, 200],
        (16): [4, 17, 28, 15, 97, 202],
        (18): [6, 19, 30, 17, 99, 204]
    }
    
    
    # Apply dropout with 50% probability
    output_dict, keys_with_defect = apply_z_coupler_dropout(input_dict, error_rate=0.5)
    
    # Print the result
    print("Input dictionary:")
    print(input_dict)
    print("\nOutput dictionary after dropout:")
    print(output_dict)
    print("\nKeys with defects:")
    print(keys_with_defect)
