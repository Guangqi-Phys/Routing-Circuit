import numpy as np
from src.bb_code import BBCode
import stim
from src.bb_code_parameters import get_logical_ops_css

def gen_cnot_pairs(code: BBCode):
    """
    Construct a list of cnot pairs between ancilla qubits and data qubits
    """

    x_cnot_pairs = []
    z_cnot_pairs = []

    for k in range(6):
        x_pair_k = []
        z_pair_k = []
        for q in code.x_ancilla_labels:
            x_pair_k += [q, code.x_stabilizers[(q, k)]]
        for q in code.z_ancilla_labels:
            z_pair_k += [code.z_stabilizers[(q, k)], q]
        x_cnot_pairs.append(x_pair_k)
        z_cnot_pairs.append(z_pair_k)
    return x_cnot_pairs, z_cnot_pairs

def gen_circ(code: BBCode, sround, seed=0):

    # 1. generate a sequence of X(0)/Z(1) and polynomial term
    np.random.seed(seed)
    seq = [(i,j) for i in [0, 1] for j in range(6)]
    # np.random.shuffle(seq)
    circuit = stim.Circuit()

    # annotate qubit coordinates
    for i in range(2*code.l):
        for j in range(2*code.m):
            circuit.append("QUBIT_COORDS", code.qubit_label(i, j), [i, j])

    circuit.append("TICK")

    #reset data qubits
    circuit.append("R", code.data_qubits_set)

    circuit.append("TICK")
    
    # reset ancilla qubits
    circuit.append("RX", code.x_ancilla_labels)
    circuit.append("R", code.z_ancilla_labels)

    circuit.append("TICK")

    x_cnot_pairs, z_cnot_pairs = gen_cnot_pairs(code)

    for i, j in seq:
        if i == 0:
            circuit.append("CNOT", x_cnot_pairs[j])
        else:
            circuit.append("CNOT", z_cnot_pairs[j])
        
        circuit.append("TICK")

    # measure
    circuit.append("MRX", code.x_ancilla_labels)
    circuit.append("MR", code.z_ancilla_labels)

    for i in range(int(code.n/2)):
        circuit.append("DETECTOR", stim.target_rec(-int(code.n/2)+i), [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
    

    circuit.append("TICK")

    # define loop body circuit
    loop_body_circuit = stim.Circuit()
        
    for i, j in seq:
        if i == 0:
            loop_body_circuit.append("CNOT", x_cnot_pairs[j])
        else:
            loop_body_circuit.append("CNOT", z_cnot_pairs[j])
        
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])
    # measure and reset stabilizers
    loop_body_circuit.append("MRX", code.x_ancilla_labels)
    for i in range(int(code.n/2)):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n/2)+i), stim.target_rec(-int(code.n+code.n/2)+i)], [code.x_ancilla_labels[i]//int(code.l*2),code.x_ancilla_labels[i]%int(code.l*2), 0])


    loop_body_circuit.append("MR", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n/2)+i), stim.target_rec(-int(code.n+code.n/2)+i)], [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
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
    # circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(code.data_qubits_set.index(idx)-code.n) for idx in code.z_random_logical], [0])


    return circuit



def gen_circ_only_z_detectors(code: BBCode, sround, seed=0):

    # 1. generate a sequence of X(0)/Z(1) and polynomial term
    np.random.seed(seed)
    seq = [(i,j) for i in [0, 1] for j in range(6)]
    # np.random.shuffle(seq)
    circuit = stim.Circuit()

    # annotate qubit coordinates
    for i in range(2*code.l):
        for j in range(2*code.m):
            circuit.append("QUBIT_COORDS", code.qubit_label(i, j), [i, j])

    circuit.append("TICK")

    #reset data qubits
    circuit.append("R", code.data_qubits_set)

    circuit.append("TICK")
    
    # reset ancilla qubits
    circuit.append("RX", code.x_ancilla_labels)
    circuit.append("R", code.z_ancilla_labels)

    circuit.append("TICK")

    x_cnot_pairs, z_cnot_pairs = gen_cnot_pairs(code)

    for i, j in seq:
        if i == 0:
            circuit.append("CNOT", x_cnot_pairs[j])
        else:
            circuit.append("CNOT", z_cnot_pairs[j])
        
        circuit.append("TICK")

    # measure
    circuit.append("MRX", code.x_ancilla_labels)
    circuit.append("MR", code.z_ancilla_labels)

    for i in range(int(code.n/2)):
        circuit.append("DETECTOR", stim.target_rec(-int(code.n/2)+i), [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
    

    circuit.append("TICK")

    # define loop body circuit
    loop_body_circuit = stim.Circuit()
        
    for i, j in seq:
        if i == 0:
            loop_body_circuit.append("CNOT", x_cnot_pairs[j])
        else:
            loop_body_circuit.append("CNOT", z_cnot_pairs[j])
        
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])
    # measure and reset stabilizers
    loop_body_circuit.append("MRX", code.x_ancilla_labels)


    loop_body_circuit.append("MR", code.z_ancilla_labels)
    for i in range(int(code.n/2)):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(code.n/2)+i), stim.target_rec(-int(code.n+code.n/2)+i)], [code.z_ancilla_labels[i]//int(code.l*2),code.z_ancilla_labels[i]%int(code.l*2), 0])
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


