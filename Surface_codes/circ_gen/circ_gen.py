import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.surface_code import SurfaceCode
from src.surface_code import transform_dictionary
import stim

def gen_cnot_pairs(code: SurfaceCode):
    """
    Construct a list of cnot pairs between ancilla qubits and data qubits
    """

    x_cnot_pairs = []
    z_cnot_pairs = []

    for k in range(4):
        x_pair_k = []
        z_pair_k = []
        for q in code.x_stb_set:
            if code.x_stabilizers[(q, k)] != -1:
                x_pair_k += [q, code.x_stabilizers[(q, k)]]
        for q in code.z_stb_set:
            if code.z_stabilizers[(q, k)] != -1:
                z_pair_k += [code.z_stabilizers[(q, k)], q]
        x_cnot_pairs.append(x_pair_k)
        z_cnot_pairs.append(z_pair_k)
    return x_cnot_pairs, z_cnot_pairs

def gen_dual_cnot_pairs(code: SurfaceCode):
    """
    Construct a list of cnot pairs between ancilla qubits and data qubits
    """

    x_cnot_pairs = []
    z_cnot_pairs = []

    for k in range(4):
        x_pair_k = []
        z_pair_k = []
        for q in code.dual_x_stb_set:
            if code.dual_x_stabilizers[(q, k)] != -1:
                x_pair_k += [q, code.dual_x_stabilizers[(q, k)]]
        for q in code.dual_z_stb_set:
            if code.dual_z_stabilizers[(q, k)] != -1:
                z_pair_k += [code.dual_z_stabilizers[(q, k)], q]
        x_cnot_pairs.append(x_pair_k)
        z_cnot_pairs.append(z_pair_k)
    return x_cnot_pairs, z_cnot_pairs


def gen_cnot_pairs_3_coupler_gidney(code: SurfaceCode):
    """
    Construct a list of cnot pairs between ancilla qubits and data qubits
    """

    x_cnot_pairs = []
    z_cnot_pairs = []

    for k in range(2):
        x_pair_k = []
        z_pair_k = []
        for q in code.x_stb_set_g:
            if code.x_stabilizers_g[(q, k)] != -1:
                x_pair_k += [q, code.x_stabilizers_g[(q, k)]]
        for q in code.z_stb_set_g:
            if code.z_stabilizers_g[(q, k)] != -1:
                z_pair_k += [code.z_stabilizers_g[(q, k)], q]
        x_cnot_pairs.append(x_pair_k)
        z_cnot_pairs.append(z_pair_k)

    x_pair_3 = []
    z_pair_3 = []
    for q in code.x_stb_set_g:
        if code.x_stabilizers_g[(q, 2)]!= -1:
            x_pair_3 += [code.x_stabilizers_g[(q, 2)], q]
    for q in code.z_stb_set_g:
        if code.z_stabilizers_g[(q, 2)]!= -1:
            z_pair_3 += [q, code.z_stabilizers_g[(q, 2)]]

    x_cnot_pairs.append(x_pair_3)
    z_cnot_pairs.append(z_pair_3)

    x_pair_4 = []
    z_pair_4 = []
    for q in code.x_stb_set_g:
        if code.x_stabilizers_g[(q, 0)]!= -1:
            x_pair_4 += [code.x_stabilizers_g[(q, 0)], q]
    for q in code.z_stb_set_g:
        if code.z_stabilizers_g[(q, 0)]!= -1:
            z_pair_4 += [q, code.z_stabilizers_g[(q, 0)]]

    x_cnot_pairs.append(x_pair_4)
    z_cnot_pairs.append(z_pair_4)

    return x_cnot_pairs, z_cnot_pairs


def gen_cnot_pairs_3_coupler_new(code: SurfaceCode):
    """
    Construct a list of cnot pairs between ancilla qubits and data qubits
    """

    x_cnot_pairs = []
    z_cnot_pairs = []

    z_measure_order = [1, 0, 2]
    x_measure_order = [1, 0, 2]

    # z measure, first round
    k = z_measure_order[0]
    z_pair_1 = []
    x_pair_1 = []
    for q in code.z_stb_set:
        if code.z_stabilizers[(q, k)] != -1:
            z_pair_1 += [code.z_stabilizers[(q, k)], q]
        q_prime = q + 2
        if q_prime in code.new_x_stb_set:
            if code.new_x_stabilizers[(q_prime, 2)]!= -1:
                x_pair_1 += [code.new_x_stabilizers[(q_prime, 2)], q_prime]

    x_cnot_pairs.append(x_pair_1)
    z_cnot_pairs.append(z_pair_1)

    # z measure, second round
    k = z_measure_order[1]
    z_pair_2 = []
    x_pair_2 = []
    for q in code.z_stb_set:
        if code.z_stabilizers[(q, k)] != -1:
            z_pair_2 += [code.z_stabilizers[(q, k)], q]
        q_prime = q + 2
        if q_prime in code.new_x_stb_set:
            if code.new_x_stabilizers[(q_prime, 0)]!= -1:
                x_pair_2 += [q_prime, code.new_x_stabilizers[(q_prime, 0)]]

    x_cnot_pairs.append(x_pair_2)
    z_cnot_pairs.append(z_pair_2)

    # z measure, third round
    k = z_measure_order[2]
    z_pair_3 = []
    x_pair_3 = []
    for q in code.z_stb_set:
        if code.z_stabilizers[(q, k)] != -1:
            z_pair_3 += [code.z_stabilizers[(q, k)], q]

    x_cnot_pairs.append(x_pair_3)
    z_cnot_pairs.append(z_pair_3)

    # z measure, fourth round
    z_pair_4 = []
    x_cnot_pairs.append(x_pair_2)
    z_cnot_pairs.append(z_pair_4)

    # z measure, fifth round
    z_pair_5 = []
    x_cnot_pairs.append(x_pair_1)
    z_cnot_pairs.append(z_pair_5)


    # x measure, round 6
    k = x_measure_order[0]
    z_pair_6 = []
    x_pair_6 = []
    for q in code.x_stb_set:
        if code.x_stabilizers[(q, k)] != -1:
            x_pair_6 += [q, code.x_stabilizers[(q, k)]]
        q_prime = q + code.lattice_rows*2
        if q_prime in code.new_z_stb_set:
            if code.new_z_stabilizers[(q_prime, 2)]!= -1:
                z_pair_6 += [q_prime, code.new_z_stabilizers[(q_prime, 2)]]

    x_cnot_pairs.append(x_pair_6)
    z_cnot_pairs.append(z_pair_6)

    # x measure, round 7
    k = x_measure_order[1]
    z_pair_7 = []
    x_pair_7 = []
    for q in code.x_stb_set:
        if code.x_stabilizers[(q, k)] != -1:
            x_pair_7 += [q, code.x_stabilizers[(q, k)]]
        q_prime = q + code.lattice_rows*2
        if q_prime in code.new_z_stb_set:
            if code.new_z_stabilizers[(q_prime, 0)]!= -1:
                z_pair_7 += [code.new_z_stabilizers[(q_prime, 0)], q_prime]

    x_cnot_pairs.append(x_pair_7)
    z_cnot_pairs.append(z_pair_7)

    # x measure, round 8
    k = x_measure_order[2]
    z_pair_8 = []
    x_pair_8 = []
    for q in code.x_stb_set:
        if code.x_stabilizers[(q, k)] != -1:
            x_pair_8 += [q, code.x_stabilizers[(q, k)]]

    x_cnot_pairs.append(x_pair_8)
    z_cnot_pairs.append(z_pair_8)

    # x measure, round 9
    x_pair_9 = []
    x_cnot_pairs.append(x_pair_9)
    z_cnot_pairs.append(z_pair_7)

    # x measure, round 10
    x_pair_10 = []
    x_cnot_pairs.append(x_pair_10)
    z_cnot_pairs.append(z_pair_6)



    return x_cnot_pairs, z_cnot_pairs

def gen_circ(code: SurfaceCode, sround):

    # seq = [(i,j) for i in [0, 1] for j in range(4)]
    # np.random.shuffle(seq)
    circuit = stim.Circuit()

    # annotate qubit coordinates

    for i in range(code.lattice_rows):
        for j in range(code.lattice_cols):
            circuit.append("QUBIT_COORDS", code.qubit_label(i, j), [i, j])

    # circuit.append("TICK")

    #reset data qubits
    circuit.append("R", code.data_qubits_set)

    # circuit.append("TICK")
    
    # reset ancilla qubits
    circuit.append("RX", code.x_stb_set)
    circuit.append("R", code.z_stb_set)

    circuit.append("TICK")

    x_cnot_pairs, z_cnot_pairs = gen_cnot_pairs(code)

    for i in range(4):
        circuit.append("CNOT", x_cnot_pairs[i])
        circuit.append("CNOT", z_cnot_pairs[i])
        
        circuit.append("TICK")

    # measure
    circuit.append("MRX", code.x_stb_set)
    circuit.append("MR", code.z_stb_set)

    for i in range(int(len(code.z_stb_set))):
        circuit.append("DETECTOR", stim.target_rec(-int(len(code.z_stb_set))+i), [code.z_stb_set[i]//int(code.lattice_cols),code.z_stb_set[i]%int(code.lattice_cols), 0])
    

    circuit.append("TICK")

    # # define loop body circuit
    loop_body_circuit = stim.Circuit()
        
    for i in range(4):
        loop_body_circuit.append("CNOT", x_cnot_pairs[i])
        loop_body_circuit.append("CNOT", z_cnot_pairs[i])
        
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])
    # measure and reset stabilizers
    loop_body_circuit.append("MRX", code.x_stb_set)
    # for i in range(int(len(code.x_stb_set))):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.x_stb_set))+i), stim.target_rec(-int(len(code.x_stb_set)*3)+i)], [code.x_stb_set[i]//int(code.lattice_cols),code.x_stb_set[i]%int(code.lattice_cols), 0])


    loop_body_circuit.append("MR", code.z_stb_set)
    for i in range(int(len(code.z_stb_set))):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.x_stb_set))+i), stim.target_rec(-int(len(code.x_stb_set)*3)+i)], [code.z_stb_set[i]//int(code.lattice_cols),code.z_stb_set[i]%int(code.lattice_cols), 0])
    loop_body_circuit.append("TICK")

    
    # adding loop body circuit to the main circuit
    circuit.append(stim.CircuitRepeatBlock(
    body=loop_body_circuit,
    repeat_count=sround))

    # # final measurements and detector setting
    circuit.append("M", code.data_qubits_set)

    for i in code.z_stb_set:
        ii = code.z_stb_set.index(i)
        data_qubits_stb = [value for (key1, key2), value in code.z_stabilizers.items() if key1 == i]
        # print("data qubits stb: ", data_qubits_stb)
        detector_final = [stim.target_rec(-int(len(code.z_stb_set)+code.n)+ii)]
        for k in range(4):
            if data_qubits_stb[k] != -1:
                detector_final.append(stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[k])))
        # print("detector final: ", detector_final)
        circuit.append("DETECTOR", detector_final, [i//int(code.lattice_cols),i%int(code.lattice_cols), 1])


    z_logical_ops = code.z_logical_op
    circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(code.data_qubits_set.index(idx)-code.n) for idx in z_logical_ops], [0])



    return circuit


def gen_circ_dual(code: SurfaceCode, sround):

    # seq = [(i,j) for i in [0, 1] for j in range(4)]
    # np.random.shuffle(seq)
    circuit = stim.Circuit()

    # annotate qubit coordinates

    for i in range(code.lattice_rows):
        for j in range(code.lattice_cols):
            circuit.append("QUBIT_COORDS", code.qubit_label(i, j), [i, j])

    # circuit.append("TICK")

    #reset data qubits
    circuit.append("R", code.data_qubits_set)

    # circuit.append("TICK")
    
    # reset ancilla qubits
    circuit.append("RX", code.dual_x_stb_set)
    circuit.append("R", code.dual_z_stb_set)

    circuit.append("TICK")

    x_cnot_pairs, z_cnot_pairs = gen_dual_cnot_pairs(code)

    for i in range(4):
        circuit.append("CNOT", x_cnot_pairs[i])
        circuit.append("CNOT", z_cnot_pairs[i])
        
        circuit.append("TICK")

    # measure
    circuit.append("MRX", code.dual_x_stb_set)
    circuit.append("MR", code.dual_z_stb_set)

    for i in range(int(len(code.dual_z_stb_set))):
        circuit.append("DETECTOR", stim.target_rec(-int(len(code.dual_z_stb_set))+i), [code.dual_z_stb_set[i]//int(code.lattice_cols),code.dual_z_stb_set[i]%int(code.lattice_cols), 0])
    

    circuit.append("TICK")

    # # define loop body circuit
    loop_body_circuit = stim.Circuit()
        
    for i in range(4):
        loop_body_circuit.append("CNOT", x_cnot_pairs[i])
        loop_body_circuit.append("CNOT", z_cnot_pairs[i])
        
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])
    # measure and reset stabilizers
    loop_body_circuit.append("MRX", code.dual_x_stb_set)
    for i in range(int(len(code.dual_x_stb_set))):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.dual_x_stb_set))+i), stim.target_rec(-int(len(code.dual_x_stb_set)*3)+i)], [code.dual_x_stb_set[i]//int(code.lattice_cols),code.dual_x_stb_set[i]%int(code.lattice_cols), 0])


    loop_body_circuit.append("MR", code.dual_z_stb_set)
    for i in range(int(len(code.dual_z_stb_set))):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.dual_x_stb_set))+i), stim.target_rec(-int(len(code.dual_x_stb_set)*3)+i)], [code.dual_z_stb_set[i]//int(code.lattice_cols),code.dual_z_stb_set[i]%int(code.lattice_cols), 0])
    loop_body_circuit.append("TICK")

    
    # adding loop body circuit to the main circuit
    circuit.append(stim.CircuitRepeatBlock(
    body=loop_body_circuit,
    repeat_count=sround))

    # # final measurements and detector setting
    circuit.append("M", code.data_qubits_set)

    for i in code.dual_z_stb_set:
        ii = code.dual_z_stb_set.index(i)
        data_qubits_stb = [value for (key1, key2), value in code.dual_z_stabilizers.items() if key1 == i]
        # print("data qubits stb: ", data_qubits_stb)
        detector_final = [stim.target_rec(-int(len(code.dual_z_stb_set)+code.n)+ii)]
        for k in range(4):
            if data_qubits_stb[k] != -1:
                detector_final.append(stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[k])))
        # print("detector final: ", detector_final)
        circuit.append("DETECTOR", detector_final, [i//int(code.lattice_cols),i%int(code.lattice_cols), 1])


    z_logical_ops = code.z_logical_op
    circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(code.data_qubits_set.index(idx)-code.n) for idx in z_logical_ops], [0])



    return circuit



def gen_circ_3_coupler_gidney(code: SurfaceCode, sround):

    # seq = [(i,j) for i in [0, 1] for j in range(4)]
    # np.random.shuffle(seq)
    circuit = stim.Circuit()

    # annotate qubit coordinates

    for i in range(code.lattice_rows):
        for j in range(code.lattice_cols):
            circuit.append("QUBIT_COORDS", code.qubit_label(i, j), [i, j])

    circuit.append("TICK")

    #reset data qubits
    circuit.append("R", code.data_qubits_set)

    circuit.append("TICK")
    
    # reset ancilla qubits
    x_stb_reset = code.weird_z_stb_g1 + [q for q in code.x_stb_set_g if q not in code.weird_x_stb_g1]
    z_stb_reset = code.weird_x_stb_g1 + [q for q in code.z_stb_set_g if q not in code.weird_z_stb_g1]

    x_stb_reset_1 = code.weird_z_stb_g2 + [q for q in code.x_stb_set_g if q not in code.weird_x_stb_g2]
    z_stb_reset_1 = code.weird_x_stb_g2 + [q for q in code.z_stb_set_g if q not in code.weird_z_stb_g2]


    x_stb_reset = sorted(x_stb_reset)
    z_stb_reset = sorted(z_stb_reset)
    x_stb_reset_1 = sorted(x_stb_reset_1)
    z_stb_reset_1 = sorted(z_stb_reset_1)



    circuit.append("RX", x_stb_reset)
    circuit.append("R", z_stb_reset)

    circuit.append("TICK")

    x_cnot_pairs, z_cnot_pairs = gen_cnot_pairs_3_coupler_gidney(code)

    for i in range(4):
        circuit.append("CNOT", x_cnot_pairs[i])
        circuit.append("CNOT", z_cnot_pairs[i])
        
        circuit.append("TICK")

    # measure
    circuit.append("MR", x_stb_reset_1)

    for i in range(int(code.n/2)):
        circuit.append("DETECTOR", stim.target_rec(-int(len(code.z_stb_set))+i), [x_stb_reset[i]//int(code.lattice_cols),x_stb_reset[i]%int(code.lattice_cols), 0])
    
    circuit.append("MRX", z_stb_reset_1)

    circuit.append("TICK")

    for i in range(3,-1,-1):
        circuit.append("CNOT", x_cnot_pairs[i])
        circuit.append("CNOT", z_cnot_pairs[i])
        
        circuit.append("TICK")

    # measure




    circuit.append("MR", z_stb_reset)
    for i in range(int(code.n/2)):
        circuit.append("DETECTOR", stim.target_rec(-int(len(code.z_stb_set))+i), [z_stb_reset[i]//int(code.lattice_cols),z_stb_reset[i]%int(code.lattice_cols), 1])
    

    circuit.append("MRX", x_stb_reset)


    circuit.append("TICK")

    # # define loop body circuit
    loop_body_circuit = stim.Circuit()
        
    for i in range(4):
        loop_body_circuit.append("CNOT", x_cnot_pairs[i])
        loop_body_circuit.append("CNOT", z_cnot_pairs[i])
        
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])
    # measure and reset stabilizers
    loop_body_circuit.append("MR", x_stb_reset_1)
    for i in range(int(len(code.x_stb_set))):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.x_stb_set))+i), stim.target_rec(-int(len(code.x_stb_set)*5)+i)], [x_stb_reset[i]//int(code.lattice_cols),x_stb_reset[i]%int(code.lattice_cols), 0])


    loop_body_circuit.append("MRX", z_stb_reset_1)
    # for i in range(int(len(code.z_stb_set))):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.x_stb_set))+i), stim.target_rec(-int(len(code.x_stb_set)*3)+i)], [code.z_stb_set[i]//int(code.lattice_cols),code.z_stb_set[i]%int(code.lattice_cols), 0])
    # loop_body_circuit.append("TICK")

    for i in range(3,-1,-1):
        loop_body_circuit.append("CNOT", x_cnot_pairs[i])
        loop_body_circuit.append("CNOT", z_cnot_pairs[i])
        
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])
    # measure and reset stabilizers

    loop_body_circuit.append("MR", z_stb_reset)
    for i in range(int(len(code.z_stb_set))):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.x_stb_set))+i), stim.target_rec(-int(len(code.x_stb_set)*5)+i)], [z_stb_reset[i]//int(code.lattice_cols),z_stb_reset[i]%int(code.lattice_cols), 1])

    loop_body_circuit.append("MRX", x_stb_reset)
    # for i in range(int(len(code.x_stb_set))):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.x_stb_set))+i), stim.target_rec(-int(len(code.x_stb_set)*5)+i)], [code.x_stb_set[i]//int(code.lattice_cols),code.x_stb_set[i]%int(code.lattice_cols), 0])


    loop_body_circuit.append("TICK")

    
    # adding loop body circuit to the main circuit
    circuit.append(stim.CircuitRepeatBlock(
    body=loop_body_circuit,
    repeat_count=sround))

    # # final measurements and detector setting
    circuit.append("M", code.data_qubits_set)

    # print("z_stb_reset", z_stb_reset)
    # print("z_stb", code.z_stb_set)

    # for i in z_stb_reset:
    #     # print("i: ", i)
    #     ii = z_stb_reset.index(i)
    #     i_re = code.z_stb_set[ii]
    #     data_qubits_stb = [value for (key1, key2), value in code.z_stabilizers.items() if key1 == i_re]
    #     # print("data qubits stb: ", data_qubits_stb)
    #     detector_final = [stim.target_rec(-int(len(z_stb_reset)*2+code.n)+ii)]
    #     for k in range(4):
    #         if data_qubits_stb[k] != -1:
    #             detector_final.append(stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[k])))
    #     # print("detector final: ", detector_final)
    #     circuit.append("DETECTOR", detector_final, [i//int(code.lattice_cols),i%int(code.lattice_cols), 1])

    print("x_stb_reset_1", x_stb_reset_1)
    print("dual_z_stb", code.dual_z_stb_set)
    for i in x_stb_reset_1:
        # print("i: ", i)
        ii = x_stb_reset_1.index(i)
        i_re = code.dual_z_stb_set[ii]
        # print("z_set", code.dual_z_stb_set)
        # print("i_re: ", i_re)
        data_qubits_stb = [value for (key1, key2), value in code.dual_z_stabilizers.items() if key1 == i_re]
        # print("data qubits stb: ", data_qubits_stb)
        detector_final = [stim.target_rec(-int(len(x_stb_reset_1)*4+code.n)+ii)]
        for k in range(4):
            if data_qubits_stb[k] != -1:
                detector_final.append(stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[k])))
        # print("detector final: ", detector_final)
        circuit.append("DETECTOR", detector_final, [i//int(code.lattice_cols),i%int(code.lattice_cols), 1])


    z_logical_ops = code.z_logical_op
    circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(code.data_qubits_set.index(idx)-code.n) for idx in z_logical_ops], [0])

    return circuit

def gen_circ_3_coupler_new(code: SurfaceCode, sround):

    # seq = [(i,j) for i in [0, 1] for j in range(4)]
    # np.random.shuffle(seq)
    circuit = stim.Circuit()

    # annotate qubit coordinates

    for i in range(code.lattice_rows):
        for j in range(code.lattice_cols):
            circuit.append("QUBIT_COORDS", code.qubit_label(i, j), [i, j])

    circuit.append("TICK")

    #reset data qubits
    circuit.append("R", code.data_qubits_set)

    circuit.append("TICK")
    
    # reset ancilla qubits
    stabilizers_reset = code.new_x_stb_set + code.new_z_stb_set
    circuit.append("R", stabilizers_reset)

    circuit.append("TICK")

    x_cnot_pairs, z_cnot_pairs = gen_cnot_pairs_3_coupler_new(code)

    for i in range(5):
        circuit.append("CNOT", z_cnot_pairs[i])
        circuit.append("CNOT", x_cnot_pairs[i])
        
        circuit.append("TICK")

    # measure
    new_stb_set = code.new_x_stb_set + code.new_z_stb_set

    circuit.append("M", new_stb_set)

    # for i in range(int(code.n/2)):
    #     circuit.append("DETECTOR", stim.target_rec(-int(len(new_stb_set))+i), [code.new_x_stb_set[i]//int(code.lattice_cols),code.new_x_stb_set[i]%int(code.lattice_cols), 0])

    for i in range(int(code.n/2)):
        circuit.append("DETECTOR", stim.target_rec(-int(len(code.new_z_stb_set))+i), [code.new_z_stb_set[i]//int(code.lattice_cols),code.new_z_stb_set[i]%int(code.lattice_cols), 0])


    # circuit.append("M", code.new_x_stb_set)
    # for i in range(int(code.n/2)):
    #     circuit.append("DETECTOR", stim.target_rec(-int(len(code.new_x_stb_set))+i), [code.new_x_stb_set[i]//int(code.lattice_cols),code.new_x_stb_set[i]%int(code.lattice_cols), 0])
 

    # circuit.append("M", code.new_z_stb_set)

    # for i in range(int(code.n/2)):
    #     circuit.append("DETECTOR", stim.target_rec(-int(len(code.new_z_stb_set))+i), [code.new_z_stb_set[i]//int(code.lattice_cols),code.new_z_stb_set[i]%int(code.lattice_cols), 0])
    

    circuit.append("TICK")

    circuit.append("RX", stabilizers_reset)


    circuit.append("TICK")

    for i in range(5,10,1):
        circuit.append("CNOT", x_cnot_pairs[i])
        circuit.append("CNOT", z_cnot_pairs[i])
        
        circuit.append("TICK")

    # measure
    circuit.append("MX", new_stb_set)

    circuit.append("TICK")



    # # define loop body circuit
    loop_body_circuit = stim.Circuit()

    loop_body_circuit.append("R", stabilizers_reset)

    loop_body_circuit.append("TICK")
         
    for i in range(5):
        loop_body_circuit.append("CNOT", x_cnot_pairs[i])
        loop_body_circuit.append("CNOT", z_cnot_pairs[i])
        
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])
    # measure and reset stabilizers

    loop_body_circuit.append("M", new_stb_set)

    # for i in range(int(len(code.new_x_stb_set))):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(new_stb_set))+i), stim.target_rec(-int(len(new_stb_set)*3)+i)], [code.new_x_stb_set[i]//int(code.lattice_cols),code.new_x_stb_set[i]%int(code.lattice_cols), 0])

    for i in range(int(len(code.new_z_stb_set))):
        loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.new_z_stb_set))+i), stim.target_rec(-int(len(code.new_z_stb_set)*5)+i)], [code.new_z_stb_set[i]//int(code.lattice_cols),code.new_z_stb_set[i]%int(code.lattice_cols), 0])

    # loop_body_circuit.append("M", code.new_x_stb_set)
    # # for i in range(int(len(code.new_z_stb_set))):
    # #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.new_x_stb_set))+i), stim.target_rec(-int(len(code.new_x_stb_set)*5)+i)], [code.new_x_stb_set[i]//int(code.lattice_cols),code.new_z_stb_set[i]%int(code.lattice_cols), 0])
    # # loop_body_circuit.append("TICK")
    # for i in range(int(len(code.new_x_stb_set))):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.new_x_stb_set))+i)], [code.new_x_stb_set[i]//int(code.lattice_cols),code.new_x_stb_set[i]%int(code.lattice_cols), 0])
    # # loop_body_circuit.append("TICK")

    # loop_body_circuit.append("M", code.new_z_stb_set)
    # for i in range(int(len(code.new_z_stb_set))):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.new_z_stb_set))+i), stim.target_rec(-int(len(code.new_z_stb_set)*5)+i)], [code.new_z_stb_set[i]//int(code.lattice_cols),code.new_z_stb_set[i]%int(code.lattice_cols), 0])


    loop_body_circuit.append("TICK")


    loop_body_circuit.append("RX", stabilizers_reset)

    loop_body_circuit.append("TICK")


    for i in range(5,10):
        loop_body_circuit.append("CNOT", x_cnot_pairs[i])
        loop_body_circuit.append("CNOT", z_cnot_pairs[i])
        
        loop_body_circuit.append("TICK")

    loop_body_circuit.append("SHIFT_COORDS", [], [0,0,1])
    # measure and reset stabilizers

    loop_body_circuit.append("MX", new_stb_set)

    # loop_body_circuit.append("MX", code.new_x_stb_set)
    # # for i in range(int(len(code.new_x_stb_set))):
    # #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.new_x_stb_set))+i), stim.target_rec(-int(len(code.new_x_stb_set)*5)+i)], [code.new_x_stb_set[i]//int(code.lattice_cols),code.new_x_stb_set[i]%int(code.lattice_cols), 0])

    # loop_body_circuit.append("MX", code.new_z_stb_set)
    # for i in range(int(len(code.new_z_stb_set))):
    #     loop_body_circuit.append("DETECTOR", [stim.target_rec(-int(len(code.new_z_stb_set))+i), stim.target_rec(-int(len(code.new_z_stb_set)*5)+i)], [code.new_z_stb_set[i]//int(code.lattice_cols),code.new_z_stb_set[i]%int(code.lattice_cols), 0])

    
    # adding loop body circuit to the main circuit
    circuit.append(stim.CircuitRepeatBlock(
    body=loop_body_circuit,
    repeat_count=sround))

    # # final measurements and detector setting
    circuit.append("M", code.data_qubits_set)

    for i in code.z_stb_set:
        ii = code.new_z_stb_set.index(i)
        data_qubits_stb = [value for (key1, key2), value in code.z_stabilizers.items() if key1 == i]
        # print("data qubits stb: ", data_qubits_stb)
        detector_final = [stim.target_rec(-int(len(code.new_z_stb_set)*3+code.n)+ii)]
        for k in range(4):
            if data_qubits_stb[k] != -1:
                detector_final.append(stim.target_rec(-int(code.n)+code.data_qubits_set.index(data_qubits_stb[k])))
        # print("detector final: ", detector_final)
        circuit.append("DETECTOR", detector_final, [i//int(code.lattice_cols),i%int(code.lattice_cols), 1])


    z_logical_ops = code.z_logical_op
    circuit.append("OBSERVABLE_INCLUDE", [stim.target_rec(code.data_qubits_set.index(idx)-code.n) for idx in z_logical_ops], [0])



    return circuit



if __name__ == "__main__":

    input_code_paras = [5,5]
    code = SurfaceCode(input_code_paras)

    # print("code.new_z_stb_set: ", code.new_z_stb_set)
    # print("new_z_stabilizers", code.new_z_stabilizers)
     
    rounds = 1

    circ = gen_circ_3_coupler_new(code, rounds)

    print(circ)

    svg_text = str(circ.diagram('detslice-with-ops-svg'))
    with open("figures/circuit_det_3coupler_new.svg", "w") as f:
        f.write(svg_text)

