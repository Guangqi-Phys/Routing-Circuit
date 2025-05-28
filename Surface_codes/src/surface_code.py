import stim

class SurfaceCode:
    """
    A class to represent a surface code.
    input_code_paras:
        lx: int, the size of the lattice in x direction
        ly: int, the size of the lattice in y direction

    Attributes:
        lx: int, the size of the lattice in x direction
        ly: int, the size of the lattice in y direction
        lattice_rows: int, the number of rows in the lattice
        lattice_cols: int, the number of columns in the lattice
        n: int, the number of data qubits
        d: int, the minimum of lx and ly
        data_qubits_set: list, the set of data qubits on the lattice
        x_stb_set: list, the set of X stabilizer qubits on the lattice
        z_stb_set: list, the set of Z stabilizer qubits on the lattice
        x_stabilizers: dict, the dictionary of X stabilizer qubits and their relative positions
        z_stabilizers: dict, the dictionary of Z stabilizer qubits and their relative positions
        x_logical_op: list, the list of X logical qubits
        z_logical_op: list, the list of Z logical qubits
    """
    def __init__(self, input_code_paras):
        self.lx = input_code_paras[0]
        self.ly = input_code_paras[1]
        self.lattice_rows = 2*self.ly + 1
        self.lattice_cols = 2*self.lx + 1
        self.n = self.lx*self.ly
        self.k = 1
        self.d = min(self.lx, self.ly)
        self.generate_rel_pos()
        self.gen_data_qubit_set()
        self.gen_stb_set()
        self.gen_logicals()
    

    def generate_rel_pos(self):
        """
        Generate relative position arrays for X and Z stabilizers based on input parameters.
        """
    
        # Define the relative positions
        # self.z_rel_pos = [[-1,1], [1,1], [-1,-1], [1,-1]]
        # self.x_rel_pos = [[-1,1], [-1,-1], [1,1], [1,-1]]

        self.z_rel_pos = [[-1,-1], [1,-1], [-1,1], [1,1]]
        self.x_rel_pos = [[-1,-1], [-1,1], [1,-1], [1,1]]

    def qubit_label(self, i, j):
        """
        Qubit label is a function that returns the label of the qubit at position (i, j).
        Qubits are on 2D lattice of size (2*self.lx, 2*self.ly) (Gottesman paper layout)
        """
        i = i % (self.lattice_rows)
        j = j % (self.lattice_cols)
        return (i * self.lattice_cols) + j

    def gen_data_qubit_set(self):
        """
        Generate the set of data qubits on the lattice.
        """
        self.data_qubits_set = []
        for i in range(1, self.lattice_rows, 2):
            for j in range(1, self.lattice_cols, 2):
                self.data_qubits_set.append(self.qubit_label(i,j))


    def gen_stb_set(self):
        """
        Generate the set of stabilizer qubits on the lattice.
        """



        # following is the structure of stabilizers for gidney's 3-coupler but two different surface code in the same circuit, and some stabilizers are weird, as the be set and measured as the x stabilizers but the cnot is applied as the z stabilizers, we defined them as weird stabilizers here.

        self.x_stabilizers_g = {}
        self.z_stabilizers_g = {}
        self.x_stb_set_g = []
        self.z_stb_set_g = []
        self.weird_x_stb_g1 = []
        self.weird_z_stb_g1 = []
        self.weird_x_stb_g2 = []
        self.weird_z_stb_g2 = []



        for i in range(2, self.lattice_rows, 2):
            if i == self.lattice_rows - 1:
                for j in range(2, self.lattice_cols - 1, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.x_stb_set_g.append(x_ancilla)
                    self.weird_x_stb_g2.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.x_stabilizers_g[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.x_stabilizers_g[(x_ancilla, k)] = -1
                for j in range(4, self.lattice_cols, 4):
                    z_ancilla = self.qubit_label(i,j)
                    self.z_stb_set_g.append(z_ancilla)
                    self.weird_z_stb_g1.append(z_ancilla)
                    for k in range(4):
                        z_qubit_coord = self.qubit_label(i+self.z_rel_pos[k][0],  j+self.z_rel_pos[k][1])
                        if z_qubit_coord in self.data_qubits_set:
                            self.z_stabilizers_g[(z_ancilla, k)] = z_qubit_coord
                        else:
                            self.z_stabilizers_g[(z_ancilla, k)] = -1
            elif int(i / 2 ) % 2 == 1:
                for j in range(4, self.lattice_cols, 4):
                    z_ancilla = self.qubit_label(i,j)
                    self.z_stb_set_g.append(z_ancilla)
                    for k in range(4):
                        z_qubit_coord = self.qubit_label(i+self.z_rel_pos[k][0],  j+self.z_rel_pos[k][1])
                        if z_qubit_coord in self.data_qubits_set:
                            self.z_stabilizers_g[(z_ancilla, k)] = z_qubit_coord
                        else:
                            self.z_stabilizers_g[(z_ancilla, k)] = -1
                for j in range(2, self.lattice_cols, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.x_stb_set_g.append(x_ancilla)
                    if j == self.lattice_cols-1:
                        self.weird_x_stb_g1.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.x_stabilizers_g[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.x_stabilizers_g[(x_ancilla, k)] = -1
            elif int( i / 2) % 2 == 0:
                for j in range(2, self.lattice_cols, 4):
                    z_ancilla = self.qubit_label(i,j)
                    self.z_stb_set_g.append(z_ancilla)
                    if j == self.lattice_cols-1:
                        self.weird_z_stb_g2.append(z_ancilla)
                    for k in range(4):
                        z_qubit_coord = self.qubit_label(i+self.z_rel_pos[k][0],  j+self.z_rel_pos[k][1])
                        if z_qubit_coord in self.data_qubits_set:
                            self.z_stabilizers_g[(z_ancilla, k)] = z_qubit_coord
                        else:
                            self.z_stabilizers_g[(z_ancilla, k)] = -1
                for j in range(4, self.lattice_cols, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.x_stb_set_g.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.x_stabilizers_g[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.x_stabilizers_g[(x_ancilla, k)] = -1

        # following is the structure of normal rotated surface code
        self.x_stabilizers = {}
        self.z_stabilizers = {}
        self.x_stb_set = []
        self.z_stb_set = []

        for i in range(0, self.lattice_rows, 2):
            if i == 0:
                for j in range(2, self.lattice_cols - 1, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.x_stabilizers[(x_ancilla, k)] = -1
            elif i == self.lattice_rows - 1:
                for j in range(4, self.lattice_cols, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.x_stabilizers[(x_ancilla, k)] = -1
            elif int(i / 2 ) % 2 == 1:
                for j in range(2, self.lattice_cols, 4):
                    z_ancilla = self.qubit_label(i,j)
                    self.z_stb_set.append(z_ancilla)
                    for k in range(4):
                        z_qubit_coord = self.qubit_label(i+self.z_rel_pos[k][0],  j+self.z_rel_pos[k][1])
                        if z_qubit_coord in self.data_qubits_set:
                            self.z_stabilizers[(z_ancilla, k)] = z_qubit_coord
                        else:
                            self.z_stabilizers[(z_ancilla, k)] = -1
                for j in range(4, self.lattice_cols - 1, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.x_stabilizers[(x_ancilla, k)] = -1
            elif int( i / 2) % 2 == 0:
                for j in range(0, self.lattice_cols, 4):
                    z_ancilla = self.qubit_label(i,j)
                    self.z_stb_set.append(z_ancilla)
                    for k in range(4):
                        z_qubit_coord = self.qubit_label(i+self.z_rel_pos[k][0],  j+self.z_rel_pos[k][1])
                        if z_qubit_coord in self.data_qubits_set:
                            self.z_stabilizers[(z_ancilla, k)] = z_qubit_coord
                        else:
                            self.z_stabilizers[(z_ancilla, k)] = -1
                for j in range(2, self.lattice_cols - 1, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.x_stabilizers[(x_ancilla, k)] = -1



        # following is the structure of dual rotated surface code, here dual means the x and z stabilizer are exchanged oin the bulk, but same at boundary (same means same type at different boundary, but at same boundary the exact position not same)
        self.dual_x_stabilizers = {}
        self.dual_z_stabilizers = {}
        self.dual_x_stb_set = []
        self.dual_z_stb_set = []

        for i in range(0, self.lattice_rows, 2):
            if i == 0:
                for j in range(4, self.lattice_cols, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.dual_x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.dual_x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.dual_x_stabilizers[(x_ancilla, k)] = -1
            elif i == self.lattice_rows - 1:
                for j in range(2, self.lattice_cols - 1, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.dual_x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.dual_x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.dual_x_stabilizers[(x_ancilla, k)] = -1
            elif int(i / 2 ) % 2 == 0:
                for j in range(2, self.lattice_cols, 4):
                    z_ancilla = self.qubit_label(i,j)
                    self.dual_z_stb_set.append(z_ancilla)
                    for k in range(4):
                        z_qubit_coord = self.qubit_label(i+self.z_rel_pos[k][0],  j+self.z_rel_pos[k][1])
                        if z_qubit_coord in self.data_qubits_set:
                            self.dual_z_stabilizers[(z_ancilla, k)] = z_qubit_coord
                        else:
                            self.dual_z_stabilizers[(z_ancilla, k)] = -1
                for j in range(4, self.lattice_cols, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.dual_x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.dual_x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.dual_x_stabilizers[(x_ancilla, k)] = -1
            elif int( i / 2) % 2 == 1:
                for j in range(0, self.lattice_cols - 1, 4):
                    z_ancilla = self.qubit_label(i,j)
                    self.dual_z_stb_set.append(z_ancilla)
                    for k in range(4):
                        z_qubit_coord = self.qubit_label(i+self.z_rel_pos[k][0],  j+self.z_rel_pos[k][1])
                        if z_qubit_coord in self.data_qubits_set:
                            self.dual_z_stabilizers[(z_ancilla, k)] = z_qubit_coord
                        else:
                            self.dual_z_stabilizers[(z_ancilla, k)] = -1
                for j in range(2, self.lattice_cols - 1, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.dual_x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.dual_x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.dual_x_stabilizers[(x_ancilla, k)] = -1


        # following is the data structure used for our new surface code circuit, it's same as normal surface code in the bulk, but at boundary, we need extra ancilla qubits to measure via routing.
        self.new_x_stabilizers = {}
        self.new_z_stabilizers = {}
        self.new_x_stb_set = []
        self.new_z_stb_set = []

        for i in range(0, self.lattice_rows, 2):
            if i == 0:
                for j in range(2, self.lattice_cols - 1, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.new_x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.new_x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.new_x_stabilizers[(x_ancilla, k)] = -1
            elif i == self.lattice_rows - 1:
                for j in range(4, self.lattice_cols - 1, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.new_x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.new_x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.new_x_stabilizers[(x_ancilla, k)] = -1

                for j in range(2, self.lattice_cols - 1, 4):
                    z_ancilla = self.qubit_label(i,j)
                    self.new_z_stb_set.append(z_ancilla)
                    for k in range(4):
                        z_qubit_coord = self.qubit_label(i+self.z_rel_pos[k][0],  j+self.z_rel_pos[k][1])
                        if z_qubit_coord in self.data_qubits_set:
                            self.new_z_stabilizers[(z_ancilla, k)] = z_qubit_coord
                        else:
                            self.new_z_stabilizers[(z_ancilla, k)] = -1
            elif int(i / 2 ) % 2 == 1:
                for j in range(2, self.lattice_cols, 4):
                    z_ancilla = self.qubit_label(i,j)
                    self.new_z_stb_set.append(z_ancilla)
                    for k in range(4):
                        z_qubit_coord = self.qubit_label(i+self.z_rel_pos[k][0],  j+self.z_rel_pos[k][1])
                        if z_qubit_coord in self.data_qubits_set:
                            self.new_z_stabilizers[(z_ancilla, k)] = z_qubit_coord
                        else:
                            self.new_z_stabilizers[(z_ancilla, k)] = -1
                for j in range(4, self.lattice_cols - 1, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.new_x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.new_x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.new_x_stabilizers[(x_ancilla, k)] = -1
            elif int( i / 2) % 2 == 0:
                for j in range(0, self.lattice_cols, 4):
                    z_ancilla = self.qubit_label(i,j)
                    self.new_z_stb_set.append(z_ancilla)
                    for k in range(4):
                        z_qubit_coord = self.qubit_label(i+self.z_rel_pos[k][0],  j+self.z_rel_pos[k][1])
                        if z_qubit_coord in self.data_qubits_set:
                            self.new_z_stabilizers[(z_ancilla, k)] = z_qubit_coord
                        else:
                            self.new_z_stabilizers[(z_ancilla, k)] = -1
                for j in range(2, self.lattice_cols, 4):
                    x_ancilla = self.qubit_label(i,j)
                    self.new_x_stb_set.append(x_ancilla)
                    for k in range(4):
                        x_qubit_coord = self.qubit_label(i+self.x_rel_pos[k][0],  j+self.x_rel_pos[k][1])
                        if x_qubit_coord in self.data_qubits_set:
                            self.new_x_stabilizers[(x_ancilla, k)] = x_qubit_coord
                        else:
                            self.new_x_stabilizers[(x_ancilla, k)] = -1
                            
        full_qubit = self.data_qubits_set + self.x_stb_set + self.z_stb_set
        ## this is a stim target only used to appling idling error
        self.full_qubit_set = [stim.GateTarget(index) for index in full_qubit]




    def gen_logicals(self):

        # gen x logicals
        self.x_logical_op = []
        j = 1
        for i in range(1, self.lattice_rows - 1, 2):
            qubit = self.qubit_label(i, j)
            if qubit in self.data_qubits_set:
                self.x_logical_op.append(qubit)

        # gen z logicals
        self.z_logical_op = []
        i = 1
        for j in range(1, self.lattice_cols - 1, 2):
            qubit = self.qubit_label(i, j)
            if qubit in self.data_qubits_set:
                self.z_logical_op.append(qubit)

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