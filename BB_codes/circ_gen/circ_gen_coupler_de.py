import numpy as np
from src.bb_code import BBCode
import stim
from src.bb_code_parameters import get_logical_ops_css, transform_dictionary
from src.coupler_dropout_methods import apply_z_coupler_dropout, apply_x_coupler_dropout, apply_z_coupler_dropout_fixed
from src.coupler_dropout_methods_50per import apply_x_coupler_dropout_fixed_50per, apply_z_coupler_dropout_fixed_50per

def gen_fixed_coupler_defect_50per(code: BBCode):
    """
    Generate a random coupler defect on the code stabilizers based on the error rate.

    In this case, only long range coupler defects are considered. We assume all short range couplers are perfect.

    return the z and x stabilizer group with defects.

    Example:
        Input stabilizers: {(12): [0, 13, 24, 23, 93, 198], (14): [2, 15, 26, 13, 95, 200]}, error_rate=0.5
        Output might be: {(12,-1): [0, 13, 24, 23, 93, 198], (14,-2): [2, 15, 26, 13, 95, 200]}
        (element 198 was removed from first stabilizer and 95 from second, note that we only record the coupler that broken, like in the case (12,-1): [0, 13, 24, 23, 93, 198], the coupler that connect 12 to 198 is broken. and in the case (14,-2): [2, 15, 26, 13, 95, 200], the coupler that connect 14 to 95 is broken.)
    """
    # generate a random coupler defect on the code
    # the coupler defect is a random pair of x and z stabilizers
    # the coupler defect is a random pair of x and z stabilizers
    trasfered_x_stabilizers = transform_dictionary(code.x_stabilizers)
    trasfered_z_stabilizers = transform_dictionary(code.z_stabilizers)

    z_stb_with_def, z_keys_with_defect = apply_z_coupler_dropout_fixed_50per(trasfered_z_stabilizers)
    x_stb_with_def, x_keys_with_defect = apply_x_coupler_dropout_fixed_50per(trasfered_x_stabilizers)


    return z_stb_with_def, x_stb_with_def


def gen_fixed_coupler_defect(code: BBCode):
    """
    Generate a random coupler defect on the code stabilizers based on the error rate.

    In this case, only long range coupler defects are considered. We assume all short range couplers are perfect.

    return the z and x stabilizer group with defects.

    Example:
        Input stabilizers: {(12): [0, 13, 24, 23, 93, 198], (14): [2, 15, 26, 13, 95, 200]}, error_rate=0.5
        Output might be: {(12,-1): [0, 13, 24, 23, 93, 198], (14,-2): [2, 15, 26, 13, 95, 200]}
        (element 198 was removed from first stabilizer and 95 from second, note that we only record the coupler that broken, like in the case (12,-1): [0, 13, 24, 23, 93, 198], the coupler that connect 12 to 198 is broken. and in the case (14,-2): [2, 15, 26, 13, 95, 200], the coupler that connect 14 to 95 is broken.)
    """
    # generate a random coupler defect on the code
    # the coupler defect is a random pair of x and z stabilizers
    # the coupler defect is a random pair of x and z stabilizers
    trasfered_x_stabilizers = transform_dictionary(code.x_stabilizers)
    trasfered_z_stabilizers = transform_dictionary(code.z_stabilizers)

    z_stb_with_def, z_keys_with_defect = apply_z_coupler_dropout_fixed(trasfered_z_stabilizers)
    
    x_stb_with_def = {}
    for key, elements in trasfered_x_stabilizers.items():   
        # Make a copy of the elements list
        new_elements = elements.copy()
        new_key = (key, 0)
        x_stb_with_def[new_key] = new_elements


    return z_stb_with_def, x_stb_with_def


def gen_random_coupler_defect(code: BBCode, error_rate):
    """
    Generate a random coupler defect on the code stabilizers based on the error rate.

    In this case, only long range coupler defects are considered. We assume all short range couplers are perfect.

    return the z and x stabilizer group with defects.

    Example:
        Input stabilizers: {(12): [0, 13, 24, 23, 93, 198], (14): [2, 15, 26, 13, 95, 200]}, error_rate=0.5
        Output might be: {(12,-1): [0, 13, 24, 23, 93, 198], (14,-2): [2, 15, 26, 13, 95, 200]}
        (element 198 was removed from first stabilizer and 95 from second, note that we only record the coupler that broken, like in the case (12,-1): [0, 13, 24, 23, 93, 198], the coupler that connect 12 to 198 is broken. and in the case (14,-2): [2, 15, 26, 13, 95, 200], the coupler that connect 14 to 95 is broken.)
    """
    # generate a random coupler defect on the code
    # the coupler defect is a random pair of x and z stabilizers
    # the coupler defect is a random pair of x and z stabilizers
    trasfered_x_stabilizers = transform_dictionary(code.x_stabilizers)
    trasfered_z_stabilizers = transform_dictionary(code.z_stabilizers)
    z_stb_with_def, z_keys_with_defect = apply_z_coupler_dropout(trasfered_z_stabilizers, error_rate)
    x_stb_with_def, x_keys_with_defect = apply_x_coupler_dropout(trasfered_x_stabilizers, z_keys_with_defect, code.x_ancilla_labels, code.corresponding_z_ancillas, error_rate)

    return z_stb_with_def, x_stb_with_def

def gen_cnot_pairs_with_defect(code: BBCode, z_stb_with_de, x_stb_with_de):
    """
    Construct a list of cnot pairs between ancilla qubits and data qubits
    the short range cnot gates are labeled as 0,1,2,3, with relative position [[-1,0], [0,1], [1,0], [0,-1]], so qubits in the same row in the 2d layout can be labeled by even (0,2, [-1,0] and [1,0]) or odd (1,3, [0,1] and [0,-1]). The long range couplers for z ancilla has relative position [-c1,-d1] and [-a1,-b1], we have the convention that [-c1,-d1] is even and [-a1,-b1] is odd for z stabilizer setup, while [-c1,-d1] is odd and [-a1,-b1] is even for x stabilizer setup.

    We label the long range couplers as even and odd to make sure that we can arrange those cnot gates in the process of applying short range cnot gates. for example, each z stabilizer has two long range couplers, we label them as even and odd, and we can apply the short range cnot gates in the order of [0,1,2,3], then the long range cnot can be coupled as [0,1+even,2+odd,3] (+ means apply the two cnot gates in parallel).
    """

    x_cnot_pairs = []
    z_cnot_pairs = []
    
    # first cnot pairs
    z_pair_0 = []
    for (a,b), elements in z_stb_with_de.items():
        z_pair_0 += [elements[0], a]
    z_cnot_pairs.append(z_pair_0)

    x_pair_0 = []
    for (a,b), elements in x_stb_with_de.items():
        x_pair_0 += [a, elements[0]]
    x_cnot_pairs.append(x_pair_0)


    # second cnot pairs
    z_pair_1 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == 0:
            z_pair_1 += [elements[1], a]
        elif b == -1:
            z_pair_1 += [elements[1], a]
        elif b == -2:
            z_pair_1 += [elements[1], a]
            z_pair_1 += [elements[4], code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)]]
    z_cnot_pairs.append(z_pair_1)

    x_pair_1 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == 0:
            x_pair_1 += [a, elements[1]]
        elif b == -1:
            x_pair_1 += [a, elements[1]]
            x_pair_1 += [code.corresponding_z_ancillas[code.x_ancilla_labels.index(a)], elements[5]]
        elif b == -2:
            x_pair_1 += [a, elements[1]]
    x_cnot_pairs.append(x_pair_1)

    # third cnot pairs
    z_pair_2 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == 0:
            z_pair_2 += [elements[2], a]
        elif b == -1:
            z_pair_2 += [elements[2], a]
            z_pair_2 += [elements[5], code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)]]
        elif b == -2:
            z_pair_2 += [elements[2], a]
    z_cnot_pairs.append(z_pair_2)

    x_pair_2 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == 0:
            x_pair_2 += [a, elements[2]]
        elif b == -1:
            x_pair_2 += [a, elements[2]]
        elif b == -2:
            x_pair_2 += [a, elements[2]]
            x_pair_2 += [code.corresponding_z_ancillas[code.x_ancilla_labels.index(a)], elements[4]]
    x_cnot_pairs.append(x_pair_2)

    # fourth cnot pairs
    z_pair_3 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == 0:
            z_pair_3 += [elements[3], a]    
        elif b == -1:
            z_pair_3 += [elements[3], a]
        elif b == -2:
            z_pair_3 += [elements[3], a]
    z_cnot_pairs.append(z_pair_3)

    x_pair_3 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == 0:
            x_pair_3 += [a, elements[3]]
        elif b == -1:
            x_pair_3 += [a, elements[3]]
        elif b == -2:
            x_pair_3 += [a, elements[3]]
    x_cnot_pairs.append(x_pair_3)


    # fifth cnot pairs
    z_pair_4 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == 0:
            z_pair_4 += [elements[4], a]
    z_cnot_pairs.append(z_pair_4)

    x_pair_4 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == 0:
            x_pair_4 += [a, elements[4]]
    x_cnot_pairs.append(x_pair_4)   


    # sixth cnot pairs
    z_pair_5 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == 0:
            z_pair_5 += [elements[5], a]    
    z_cnot_pairs.append(z_pair_5)

    x_pair_5 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == 0:
            x_pair_5 += [a, elements[5]]
    x_cnot_pairs.append(x_pair_5)


    # seventh cnot pairs
    z_pair_6 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -1:
            z_pair_6 += [code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)], elements[4]]
        elif b == -2:
            z_pair_6 += [code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)], elements[5]]
    z_cnot_pairs.append(z_pair_6)

    x_pair_6 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -1:
            x_pair_6 += [elements[4], code.corresponding_z_ancillas[code.x_ancilla_labels.index(a)]]
        elif b == -2:
            x_pair_6 += [elements[5], code.corresponding_z_ancillas[code.x_ancilla_labels.index(a)]]
    x_cnot_pairs.append(x_pair_6)

    # eighth cnot pairs
    z_pair_7 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -1:
            z_pair_7 += [elements[4], a]
        elif b == -2:
            z_pair_7 += [elements[5], a]
    z_cnot_pairs.append(z_pair_7) 

    x_pair_7 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -1:
            x_pair_7 += [a, elements[4]]
        elif b == -2:
            x_pair_7 += [a, elements[5]]
    x_cnot_pairs.append(x_pair_7)



    # ninth cnot pairs
    z_pair_8 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -1:
            z_pair_8 += [code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)], elements[4]]   
        elif b == -2:
            z_pair_8 += [code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)], elements[5]]
    z_cnot_pairs.append(z_pair_8)


    x_pair_8 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -1:
            x_pair_8 += [elements[4], code.corresponding_z_ancillas[code.x_ancilla_labels.index(a)]]
        elif b == -2:
            x_pair_8 += [elements[5], code.corresponding_z_ancillas[code.x_ancilla_labels.index(a)]]
    x_cnot_pairs.append(x_pair_8)


    # tenth cnot pairs
    z_pair_9 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -1:
            z_pair_9 += [elements[5], code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)]]
        elif b == -2:
            z_pair_9 += [elements[4], code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)]]
    z_cnot_pairs.append(z_pair_9)

    x_pair_9 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -1:
            x_pair_9 += [code.corresponding_z_ancillas[code.x_ancilla_labels.index(a)], elements[5]]
        elif b == -2:
            x_pair_9 += [code.corresponding_z_ancillas[code.x_ancilla_labels.index(a)], elements[4]]
    x_cnot_pairs.append(x_pair_9)
    
    return x_cnot_pairs, z_cnot_pairs

    

def gen_cnot_pairs_75per_coupler(code: BBCode, z_stb_with_de, x_stb_with_de):
    """
    Construct a list of cnot pairs between ancilla qubits and data qubits
    the short range cnot gates are labeled as 0,1,2,3, with relative position [[-1,0], [0,1], [1,0], [0,-1]], so qubits in the same row in the 2d layout can be labeled by even (0,2, [-1,0] and [1,0]) or odd (1,3, [0,1] and [0,-1]). The long range couplers for z ancilla has relative position [-c1,-d1] and [-a1,-b1], we have the convention that [-c1,-d1] is even and [-a1,-b1] is odd for z stabilizer setup, while [-c1,-d1] is odd and [-a1,-b1] is even for x stabilizer setup.

    We label the long range couplers as even and odd to make sure that we can arrange those cnot gates in the process of applying short range cnot gates. for example, each z stabilizer has two long range couplers, we label them as even and odd, and we can apply the short range cnot gates in the order of [0,1,2,3], then the long range cnot can be coupled as [0,1+even,2+odd,3] (+ means apply the two cnot gates in parallel).
    """

    x_cnot_pairs = []
    z_cnot_pairs = []
    
    # first cnot pairs
    z_pair_0 = []
    for (a,b), elements in z_stb_with_de.items():
        z_pair_0 += [elements[0], a]
    z_cnot_pairs.append(z_pair_0)

    x_pair_0 = []
    for (a,b), elements in x_stb_with_de.items():
        x_pair_0 += [a, elements[0]]
    x_cnot_pairs.append(x_pair_0)


    # second cnot pairs
    z_pair_1 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_1 += [elements[1], a]
            z_pair_1 += [elements[4], code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)]]
    z_cnot_pairs.append(z_pair_1)

    x_pair_1 = []
    for (a,b), elements in x_stb_with_de.items():
        x_pair_1 += [a, elements[1]]
    x_cnot_pairs.append(x_pair_1)

    # third cnot pairs
    z_pair_2 = []
    for (a,b), elements in z_stb_with_de.items():
        z_pair_2 += [elements[2], a]
    z_cnot_pairs.append(z_pair_2)

    x_pair_2 = []
    for (a,b), elements in x_stb_with_de.items():
        x_pair_2 += [a, elements[2]]
    x_cnot_pairs.append(x_pair_2)

    # fourth cnot pairs
    z_pair_3 = []
    for (a,b), elements in z_stb_with_de.items():
        z_pair_3 += [elements[3], a]
    z_cnot_pairs.append(z_pair_3)

    x_pair_3 = []
    for (a,b), elements in x_stb_with_de.items():
        x_pair_3 += [a, elements[3]]
    x_cnot_pairs.append(x_pair_3)


    # fifth cnot pairs

    z_pair_4 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_4 += [code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)], elements[5]]
    z_cnot_pairs.append(z_pair_4)

    x_pair_4 = []
    for (a,b), elements in x_stb_with_de.items():
        x_pair_4 += [a, elements[4]]
    x_cnot_pairs.append(x_pair_4)   


    # sixth cnot pairs

    z_pair_5 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_5 += [elements[5], a]
    z_cnot_pairs.append(z_pair_5) 

    x_pair_5 = []
    for (a,b), elements in x_stb_with_de.items():
        x_pair_5 += [a, elements[5]]
    x_cnot_pairs.append(x_pair_5)


    # seventh cnot pairs

    z_pair_6 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_6 += [code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)], elements[5]]
    z_cnot_pairs.append(z_pair_6)

    # eighth cnot pairs
    z_pair_7 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_7 += [elements[4], code.corresponding_x_ancillas[code.z_ancilla_labels.index(a)]]
    z_cnot_pairs.append(z_pair_7)
    
    return x_cnot_pairs, z_cnot_pairs

def gen_cnot_pairs_50per_coupler(code: BBCode, z_stb_with_de, x_stb_with_de):
    """
    Construct a list of cnot pairs between ancilla qubits and data qubits
    the short range cnot gates are labeled as 0,1,2,3, with relative position [[-1,0], [0,1], [1,0], [0,-1]], so qubits in the same row in the 2d layout can be labeled by even (0,2, [-1,0] and [1,0]) or odd (1,3, [0,1] and [0,-1]). The long range couplers for z ancilla has relative position [-c1,-d1] and [-a1,-b1], we have the convention that [-c1,-d1] is even and [-a1,-b1] is odd for z stabilizer setup, while [-c1,-d1] is odd and [-a1,-b1] is even for x stabilizer setup.

    We label the long range couplers as even and odd to make sure that we can arrange those cnot gates in the process of applying short range cnot gates. for example, each z stabilizer has two long range couplers, we label them as even and odd, and we can apply the short range cnot gates in the order of [0,1,2,3], then the long range cnot can be coupled as [0,1+even,2+odd,3] (+ means apply the two cnot gates in parallel).
    """

    x_cnot_pairs = []
    z_cnot_pairs = []
    
    # first cnot pairs
    z_pair_0 = []
    for (a,b), elements in z_stb_with_de.items():
        z_pair_0 += [elements[0], a]
    z_cnot_pairs.append(z_pair_0)

    x_pair_0 = []
    for (a,b), elements in x_stb_with_de.items():
        x_pair_0 += [a, elements[0]]
    x_cnot_pairs.append(x_pair_0)


    # second cnot pairs
    z_pair_1 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_1 += [elements[1], a]
            z_pair_1 += [elements[4], code.corresponding_x_ancillas_50per[code.z_ancilla_labels.index(a)]]
    z_cnot_pairs.append(z_pair_1)

    x_pair_1 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -2:
            x_pair_1 += [a, elements[1]]
    x_cnot_pairs.append(x_pair_1)

    # third cnot pairs
    z_pair_2 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_2 += [elements[2], a]
    z_cnot_pairs.append(z_pair_2)

    x_pair_2 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -2:
            x_pair_2 += [a, elements[2]]
            x_pair_2 += [code.corresponding_z_ancillas_50per[code.x_ancilla_labels.index(a)], elements[4]]
    x_cnot_pairs.append(x_pair_2)

    # fourth cnot pairs
    z_pair_3 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_3 += [elements[3], a]
    z_cnot_pairs.append(z_pair_3)

    x_pair_3 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -2:
            x_pair_3 += [a, elements[3]]
    x_cnot_pairs.append(x_pair_3)


    # fifth cnot pairs
    z_pair_6 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_6 += [code.corresponding_x_ancillas_50per[code.z_ancilla_labels.index(a)], elements[5]]
    z_cnot_pairs.append(z_pair_6)

    x_pair_6 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -2:
            x_pair_6 += [elements[5], code.corresponding_z_ancillas_50per[code.x_ancilla_labels.index(a)]]
    x_cnot_pairs.append(x_pair_6)

    # sixth cnot pairs
    z_pair_7 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_7 += [elements[5], a]
    z_cnot_pairs.append(z_pair_7) 

    x_pair_7 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -2:
            x_pair_7 += [a, elements[5]]
    x_cnot_pairs.append(x_pair_7)



    # seventh cnot pairs
    z_pair_8 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_8 += [code.corresponding_x_ancillas_50per[code.z_ancilla_labels.index(a)], elements[5]]
    z_cnot_pairs.append(z_pair_8)


    x_pair_8 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -2:
            x_pair_8 += [elements[5], code.corresponding_z_ancillas_50per[code.x_ancilla_labels.index(a)]]
    x_cnot_pairs.append(x_pair_8)


    # eighth cnot pairs
    z_pair_9 = []
    for (a,b), elements in z_stb_with_de.items():
        if b == -2:
            z_pair_9 += [elements[4], code.corresponding_x_ancillas_50per[code.z_ancilla_labels.index(a)]]
    z_cnot_pairs.append(z_pair_9)

    x_pair_9 = []
    for (a,b), elements in x_stb_with_de.items():
        if b == -2:
            x_pair_9 += [code.corresponding_z_ancillas_50per[code.x_ancilla_labels.index(a)], elements[4]]
    x_cnot_pairs.append(x_pair_9)
    
    return x_cnot_pairs, z_cnot_pairs



def gen_circ_coupler_defect(code: BBCode, sround):

        
    coupler_error_rate = 1 # 1 means 1/4 coupler dropout
    z_stb_with_de, x_stb_with_de = gen_random_coupler_defect(code, coupler_error_rate)
    x_cnot_pairs, z_cnot_pairs = gen_cnot_pairs_with_defect(code, z_stb_with_de, x_stb_with_de)


    # print the x and z stabilizers with defects
    # for (a,b), elements in x_stb_with_de.items():
    #     if b != 0:
    #         print("x_stb_with_de: ", (a,b), x_stb_with_de[(a,b)])
    # for (a,b), elements in z_stb_with_de.items():
    #     if b != 0:
    #         print("z_stb_with_de: ", (a,b), z_stb_with_de[(a,b)])


    circuit = stim.Circuit()

    # annotate qubit coordinates
    for i in range(2*code.l):
        for j in range(2*code.m):
            circuit.append("QUBIT_COORDS", code.qubit_label(i, j), [i, j])

    #reset data qubits
    circuit.append("R", code.data_qubits_set)
    
    # reset ancilla qubits
    circuit.append("RX", code.x_ancilla_labels)
    circuit.append("RX", code.z_ancilla_labels)

    circuit.append("TICK")


    for i in range(10):
        circuit.append("CNOT", x_cnot_pairs[i])
        circuit.append("TICK")


    circuit.append("MX", code.x_ancilla_labels)
    circuit.append("MX", code.z_ancilla_labels)

    circuit.append("TICK")

    circuit.append("R", code.x_ancilla_labels)
    circuit.append("R", code.z_ancilla_labels)

    circuit.append("TICK")

    for i in range(10):
        circuit.append("CNOT", z_cnot_pairs[i])
        circuit.append("TICK")

    # measure and reset stabilizers
    circuit.append("M", code.x_ancilla_labels)
    circuit.append("M", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        circuit.append("DETECTOR", stim.target_rec(-int(code.n/2)+i), [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
    

    circuit.append("TICK")

    # define loop body circuit
    loop_body_circuit = stim.Circuit()

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])

    loop_body_circuit.append("RX", code.x_ancilla_labels)
    loop_body_circuit.append("RX", code.z_ancilla_labels)

    loop_body_circuit.append("TICK")

    for i in range(10):
        loop_body_circuit.append("CNOT", x_cnot_pairs[i])
        loop_body_circuit.append("TICK")

    # measure and reset stabilizers
    loop_body_circuit.append("MX", code.x_ancilla_labels)
    loop_body_circuit.append("MX", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n)+i), stim.target_rec(-int(code.n*3)+i)], [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])

    loop_body_circuit.append("R", code.x_ancilla_labels)
    loop_body_circuit.append("R", code.z_ancilla_labels)

    loop_body_circuit.append("TICK")

    for i in range(10):
        loop_body_circuit.append("CNOT", z_cnot_pairs[i])
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("M", code.x_ancilla_labels)
    loop_body_circuit.append("M", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n/2)+i), stim.target_rec(-int(code.n*2+code.n/2)+i)], [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
    
    loop_body_circuit.append("TICK")

    
    # adding loop body circuit to the main circuit
    circuit.append(stim.CircuitRepeatBlock(
    body=loop_body_circuit,
    repeat_count=sround))

    # final measurements and detector setting
    circuit.append("M", code.data_qubits_set)

    for i in code.z_ancilla_labels:
        ii = code.z_ancilla_labels.index(i)
        data_qubits_stb = [value for (key1, key2), value in code.z_stabilizers.items() if key1 == i]
        circuit.append("DETECTOR", [stim.target_rec(-int(code.n*3/2)+ii), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[0])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[1])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[2])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[3])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[4])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[5]))], [code.z_ancilla_labels[ii]//int(code.l*2),code.z_ancilla_labels[ii]%int(code.l*2), 1])



    # adding observable measurement to the circuit
    for i in range(len(code.z_logical_operators)):
        logical_ops = get_logical_ops_css(code.qcode.lz, code.k, code.m, code.n)
        circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(code.data_qubits_set.index(idx)-code.n) for idx in logical_ops[i]], [i])
        # print("z_random_logical: ", code.z_random_logical) 


    return circuit


def gen_circ_coupler_defect_only_z_detectors(code: BBCode, sround):

        
    coupler_error_rate = 1 # 1 means 1/4 coupler dropout
    z_stb_with_de, x_stb_with_de = gen_fixed_coupler_defect(code)
    x_cnot_pairs, z_cnot_pairs = gen_cnot_pairs_with_defect(code, z_stb_with_de, x_stb_with_de)


    # print number of coupler defects and the number of total coupler
    num_x_stb_defects = 0
    num_z_stb_defects = 0
    for (a,b), elements in x_stb_with_de.items():
        if b != 0:
            num_x_stb_defects += 1
    for (a,b), elements in z_stb_with_de.items():
        if b != 0:
            num_z_stb_defects += 1
    
    num_stb_defects = num_z_stb_defects + num_x_stb_defects

    print("Number of coupler defects, Number of total long-range couplers:", num_stb_defects, code.n*2)
    


    # print the x and z stabilizers with defects



    circuit = stim.Circuit()

    # annotate qubit coordinates
    for i in range(2*code.l):
        for j in range(2*code.m):
            circuit.append("QUBIT_COORDS", code.qubit_label(i, j), [i, j])

    #reset data qubits
    circuit.append("R", code.data_qubits_set)
    
    # reset ancilla qubits
    circuit.append("RX", code.x_ancilla_labels)
    circuit.append("RX", code.z_ancilla_labels)

    circuit.append("TICK")


    for i in range(10):
        circuit.append("CNOT", x_cnot_pairs[i])
        circuit.append("TICK")


    circuit.append("MX", code.x_ancilla_labels)
    circuit.append("MX", code.z_ancilla_labels)

    circuit.append("TICK")

    circuit.append("R", code.x_ancilla_labels)
    circuit.append("R", code.z_ancilla_labels)

    circuit.append("TICK")

    for i in range(10):
        circuit.append("CNOT", z_cnot_pairs[i])
        circuit.append("TICK")

    # measure and reset stabilizers
    circuit.append("M", code.x_ancilla_labels)
    # for i in range(int(code.n/2)):
    #     circuit.append("DETECTOR", stim.target_rec(-int(code.n/2)+i), [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])
    circuit.append("M", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        circuit.append("DETECTOR", stim.target_rec(-int(code.n/2)+i), [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
    

    circuit.append("TICK")

    # define loop body circuit
    loop_body_circuit = stim.Circuit()

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])

    loop_body_circuit.append("RX", code.x_ancilla_labels)
    loop_body_circuit.append("RX", code.z_ancilla_labels)

    loop_body_circuit.append("TICK")

    for i in range(10):
        loop_body_circuit.append("CNOT", x_cnot_pairs[i])
        loop_body_circuit.append("TICK")

    # measure and reset stabilizers
    loop_body_circuit.append("MX", code.x_ancilla_labels)
    loop_body_circuit.append("MX", code.z_ancilla_labels)
    # for i in range(int(code.n/2)):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n)+i), stim.target_rec(-int(code.n*3)+i)], [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])

    loop_body_circuit.append("R", code.x_ancilla_labels)
    loop_body_circuit.append("R", code.z_ancilla_labels)

    loop_body_circuit.append("TICK")

    for i in range(10):
        loop_body_circuit.append("CNOT", z_cnot_pairs[i])
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("M", code.x_ancilla_labels)
    # for i in range(int(code.n/2)):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n/2)+i), stim.target_rec(-int(code.n*2+code.n/2)+i)], [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])
    loop_body_circuit.append("M", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n/2)+i), stim.target_rec(-int(code.n*2+code.n/2)+i)], [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
    
    loop_body_circuit.append("TICK")

    
    # adding loop body circuit to the main circuit
    circuit.append(stim.CircuitRepeatBlock(
    body=loop_body_circuit,
    repeat_count=sround))

    # final measurements and detector setting
    circuit.append("M", code.data_qubits_set)

    for i in code.z_ancilla_labels:
        ii = code.z_ancilla_labels.index(i)
        data_qubits_stb = [value for (key1, key2), value in code.z_stabilizers.items() if key1 == i]
        circuit.append("DETECTOR", [stim.target_rec(-int(code.n*3/2)+ii), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[0])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[1])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[2])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[3])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[4])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[5]))], [code.z_ancilla_labels[ii]//int(code.l*2),code.z_ancilla_labels[ii]%int(code.l*2), 1])



    # adding observable measurement to the circuit
    for i in range(code.k):
        logical_ops = get_logical_ops_css(code.qcode.lz, code.k, code.m, code.n)
        circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(code.data_qubits_set.index(idx)-code.n) for idx in logical_ops[i]], [i])
        # print("z_random_logical: ", code.z_random_logical) 


    return circuit



def gen_circ_50per_coupler(code: BBCode, sround):

    
    z_stb_with_de, x_stb_with_de = gen_fixed_coupler_defect_50per(code)
    x_cnot_pairs, z_cnot_pairs = gen_cnot_pairs_50per_coupler(code, z_stb_with_de, x_stb_with_de)


    # print number of coupler defects and the number of total coupler
    num_x_stb_defects = 0
    num_z_stb_defects = 0
    for (a,b), elements in x_stb_with_de.items():
        if b != 0:
            num_x_stb_defects += 1
    for (a,b), elements in z_stb_with_de.items():
        if b != 0:
            num_z_stb_defects += 1
    
    num_stb_defects = num_z_stb_defects + num_x_stb_defects

    print("Number of coupler defects, Number of total long-range couplers:", num_stb_defects, code.n*2)
    


    # print the x and z stabilizers with defects



    circuit = stim.Circuit()

    # annotate qubit coordinates
    for i in range(2*code.l):
        for j in range(2*code.m):
            circuit.append("QUBIT_COORDS", code.qubit_label(i, j), [i, j])

    #reset data qubits
    circuit.append("R", code.data_qubits_set)
    
    # reset ancilla qubits
    circuit.append("RX", code.x_ancilla_labels)
    circuit.append("RX", code.z_ancilla_labels)

    circuit.append("TICK")


    for i in range(len(x_cnot_pairs)):
        circuit.append("CNOT", x_cnot_pairs[i])
        circuit.append("TICK")


    circuit.append("MX", code.x_ancilla_labels)
    circuit.append("MX", code.z_ancilla_labels)

    circuit.append("TICK")

    circuit.append("R", code.x_ancilla_labels)
    circuit.append("R", code.z_ancilla_labels)

    circuit.append("TICK")

    for i in range(len(z_cnot_pairs)):
        circuit.append("CNOT", z_cnot_pairs[i])
        circuit.append("TICK")

    # measure and reset stabilizers
    circuit.append("M", code.x_ancilla_labels)
    # for i in range(int(code.n/2)):
    #     circuit.append("DETECTOR", stim.target_rec(-int(code.n/2)+i), [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])
    circuit.append("M", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        circuit.append("DETECTOR", stim.target_rec(-int(code.n/2)+i), [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
    

    circuit.append("TICK")

    # define loop body circuit
    loop_body_circuit = stim.Circuit()

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])

    loop_body_circuit.append("RX", code.x_ancilla_labels)
    loop_body_circuit.append("RX", code.z_ancilla_labels)

    loop_body_circuit.append("TICK")

    for i in range(len(x_cnot_pairs)):
        loop_body_circuit.append("CNOT", x_cnot_pairs[i])
        loop_body_circuit.append("TICK")

    # measure and reset stabilizers
    loop_body_circuit.append("MX", code.x_ancilla_labels)
    loop_body_circuit.append("MX", code.z_ancilla_labels)
    # for i in range(int(code.n/2)):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n)+i), stim.target_rec(-int(code.n*3)+i)], [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])

    loop_body_circuit.append("R", code.x_ancilla_labels)
    loop_body_circuit.append("R", code.z_ancilla_labels)

    loop_body_circuit.append("TICK")

    for i in range(len(z_cnot_pairs)):
        loop_body_circuit.append("CNOT", z_cnot_pairs[i])
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("M", code.x_ancilla_labels)
    # for i in range(int(code.n/2)):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n/2)+i), stim.target_rec(-int(code.n*2+code.n/2)+i)], [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])
    loop_body_circuit.append("M", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n/2)+i), stim.target_rec(-int(code.n*2+code.n/2)+i)], [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
    
    loop_body_circuit.append("TICK")

    
    # adding loop body circuit to the main circuit
    circuit.append(stim.CircuitRepeatBlock(
    body=loop_body_circuit,
    repeat_count=sround))

    # final measurements and detector setting
    circuit.append("M", code.data_qubits_set)

    for i in code.z_ancilla_labels:
        ii = code.z_ancilla_labels.index(i)
        data_qubits_stb = [value for (key1, key2), value in code.z_stabilizers.items() if key1 == i]
        circuit.append("DETECTOR", [stim.target_rec(-int(code.n*3/2)+ii), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[0])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[1])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[2])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[3])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[4])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[5]))], [code.z_ancilla_labels[ii]//int(code.l*2),code.z_ancilla_labels[ii]%int(code.l*2), 1])



    # adding observable measurement to the circuit
    for i in range(code.k):
        logical_ops = get_logical_ops_css(code.qcode.lz, code.k, code.m, code.n)
        circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(code.data_qubits_set.index(idx)-code.n) for idx in logical_ops[i]], [i])
        # print("z_random_logical: ", code.z_random_logical) 


    return circuit



def gen_circ_75per_coupler(code: BBCode, sround):

        
    coupler_error_rate = 1 # 1 means 1/4 coupler dropout
    z_stb_with_de, x_stb_with_de = gen_fixed_coupler_defect(code)
    x_cnot_pairs, z_cnot_pairs = gen_cnot_pairs_75per_coupler(code, z_stb_with_de, x_stb_with_de)


    # print number of coupler defects and the number of total coupler
    num_x_stb_defects = 0
    num_z_stb_defects = 0
    for (a,b), elements in x_stb_with_de.items():
        if b != 0:
            num_x_stb_defects += 1
    for (a,b), elements in z_stb_with_de.items():
        if b != 0:
            num_z_stb_defects += 1
    
    num_stb_defects = num_z_stb_defects + num_x_stb_defects

    print("Number of coupler defects, Number of total long-range couplers:", num_stb_defects, code.n*2)
    


    # print the x and z stabilizers with defects



    circuit = stim.Circuit()

    # annotate qubit coordinates
    for i in range(2*code.l):
        for j in range(2*code.m):
            circuit.append("QUBIT_COORDS", code.qubit_label(i, j), [i, j])

    #reset data qubits
    circuit.append("R", code.data_qubits_set)
    
    # reset ancilla qubits
    circuit.append("RX", code.x_ancilla_labels)
    circuit.append("RX", code.z_ancilla_labels)

    circuit.append("TICK")


    for i in range(len(x_cnot_pairs)):
        circuit.append("CNOT", x_cnot_pairs[i])
        circuit.append("TICK")


    circuit.append("MX", code.x_ancilla_labels)
    circuit.append("MX", code.z_ancilla_labels)

    circuit.append("TICK")

    circuit.append("R", code.x_ancilla_labels)
    circuit.append("R", code.z_ancilla_labels)

    circuit.append("TICK")

    for i in range(len(z_cnot_pairs)):
        circuit.append("CNOT", z_cnot_pairs[i])
        circuit.append("TICK")

    # measure and reset stabilizers
    circuit.append("M", code.x_ancilla_labels)
    # for i in range(int(code.n/2)):
    #     circuit.append("DETECTOR", stim.target_rec(-int(code.n/2)+i), [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])
    circuit.append("M", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        circuit.append("DETECTOR", stim.target_rec(-int(code.n/2)+i), [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
    

    circuit.append("TICK")

    # define loop body circuit
    loop_body_circuit = stim.Circuit()

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])

    loop_body_circuit.append("RX", code.x_ancilla_labels)
    loop_body_circuit.append("RX", code.z_ancilla_labels)

    loop_body_circuit.append("TICK")

    for i in range(len(x_cnot_pairs)):
        loop_body_circuit.append("CNOT", x_cnot_pairs[i])
        loop_body_circuit.append("TICK")

    # measure and reset stabilizers
    loop_body_circuit.append("MX", code.x_ancilla_labels)
    loop_body_circuit.append("MX", code.z_ancilla_labels)
    # for i in range(int(code.n/2)):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n)+i), stim.target_rec(-int(code.n*3)+i)], [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])

    loop_body_circuit.append("R", code.x_ancilla_labels)
    loop_body_circuit.append("R", code.z_ancilla_labels)

    loop_body_circuit.append("TICK")

    for i in range(len(z_cnot_pairs)):
        loop_body_circuit.append("CNOT", z_cnot_pairs[i])
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("M", code.x_ancilla_labels)
    # for i in range(int(code.n/2)):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n/2)+i), stim.target_rec(-int(code.n*2+code.n/2)+i)], [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])
    loop_body_circuit.append("M", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n/2)+i), stim.target_rec(-int(code.n*2+code.n/2)+i)], [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
    
    loop_body_circuit.append("TICK")

    
    # adding loop body circuit to the main circuit
    circuit.append(stim.CircuitRepeatBlock(
    body=loop_body_circuit,
    repeat_count=sround))

    # final measurements and detector setting
    circuit.append("M", code.data_qubits_set)

    for i in code.z_ancilla_labels:
        ii = code.z_ancilla_labels.index(i)
        data_qubits_stb = [value for (key1, key2), value in code.z_stabilizers.items() if key1 == i]
        circuit.append("DETECTOR", [stim.target_rec(-int(code.n*3/2)+ii), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[0])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[1])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[2])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[3])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[4])), stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[5]))], [code.z_ancilla_labels[ii]//int(code.l*2),code.z_ancilla_labels[ii]%int(code.l*2), 1])



    # adding observable measurement to the circuit
    for i in range(code.k):
        logical_ops = get_logical_ops_css(code.qcode.lz, code.k, code.m, code.n)
        circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(code.data_qubits_set.index(idx)-code.n) for idx in logical_ops[i]], [i])
        # print("z_random_logical: ", code.z_random_logical) 


    return circuit