import numpy as np
from src.bb_code_parameters import logical_operator_and_distance_compute, convert_logical_layout, compute_logical_operator, get_minimal_logical_length
from bposd.css import css_code
import random
import concurrent.futures
import multiprocessing
import stim



class BBCode:
    """
    BBCode is quantum stabilizer code.
    n, k, d are the parameters of the code.
    x_rel_pos, z_rel_pos are the relative positions of the X and Z stabilizers.
    We assume toric layout of the lattice.
    self.n, self.k, self.d are the parameters of the code.
    self.params = [self.n, self.k, self.d]
    self.x_stabilizers, self.z_stabilizers are the dictionaries of the X and Z stabilizers.
    self.hx, self.hz are the check matrices for the X and Z stabilizers.
    self.x_ancilla_labels, self.z_ancilla_labels are the lists of the X and Z ancilla qubits.
    self.corresponding_z_ancillas are the labels of the Z ancilla qubits that are connected to the X ancilla qubits. self.corresponding_x_ancillas are the labels of the X ancilla qubits that are connected to the Z ancilla qubits.
    self.l_data_qubits_set, self.r_data_qubits_set are the lists of the data qubits.
    self.data_qubits_set is the list of all data qubits.
    self.x_rel_pos, self.z_rel_pos are the relative positions of the X and Z stabilizers (according to data qubits).
    self.qcode is the CSS code structure.
    self.z_logical_operators are the Z-type logical operators.
    """
    def __init__(self, code_params):
        """
        Initialize the BBCode class.
        
        Args:
            code_params (list): List of parameters [l, m, a, b, c, d]
        """
        self.l = code_params[0]
        self.m = code_params[1]
        self.poly_params = code_params[2:]

        self.n = 2*self.l*self.m
        
        self.lattice_rows = 2 * self.l
        self.lattice_cols = 2 * self.m

        self.generate_rel_pos()
        self.gen_data_qubit_set()
        self.gen_stabilizer()
        self.gen_check_matrices()
        self.gen_k()
        # Remove z_logical_distance() from initialization
        # Initialize private attributes for lazy loading
        

        # the following distance is get from qcode, which may not be optimal, but is enough to do circuit level simulation, it is way faster.
        self.qcodedx = get_minimal_logical_length(self.qcode.lx)
        self.qcodedz = get_minimal_logical_length(self.qcode.lz)

        # self.d is the optimized distance of the code
        self._d = None
        self._z_logical_operators = None
        self._z_random_logical = None
        self._x_logical_operators = None


    def gen_check_matrices(self):
        """
        Generate check matrices for X and Z stabilizers.
        """
        # define cyclic shift matrices 
        I_ell = np.identity(self.l, dtype=int)
        I_m = np.identity(self.m, dtype=int)
        I = np.identity(self.l*self.m, dtype=int)
        x = {}
        y = {}
    
        for i in range(self.l):
            x[i] = np.kron(np.roll(I_ell, i, axis=1), I_m)
        for i in range(self.m):
            y[i] = np.kron(I_ell, np.roll(I_m, i, axis=1))

        # define check matrices
        A = (I + y[1] + np.dot(x[self.poly_params[0]%self.l], y[self.poly_params[1]%self.m])) % 2
        B = (I + x[1] + np.dot(x[self.poly_params[2]%self.l], y[self.poly_params[3]%self.m])) % 2
    
        AT = np.transpose(A)
        BT = np.transpose(B)
    
        # H_X and H_Z are the check matrices for the X and Z stabilizers
        self.hx = np.hstack((A, B))
        self.hz = np.hstack((BT, AT))

    def gen_k(self):
        """
        Generate code parameters based on input parameters.
        """
        self.qcode=css_code(self.hx,self.hz)
        self.k = self.qcode.lz.shape[0]
        
    def generate_rel_pos(self):
        """
        Generate relative position arrays for X and Z stabilizers based on input parameters.
        """
        # Calculate derived parameters
        a1 = 2*self.poly_params[0]
        b1 = 2*(self.poly_params[1]-1)+1
        c1 = 2*(self.poly_params[2]-1)+1
        d1 = 2*self.poly_params[3]
    
        # Define the relative positions
        self.x_rel_pos = [[0,-1], [1,0], [0,1], [-1,0], [c1,d1], [a1,b1]]
        self.z_rel_pos = [[0,-1], [1,0], [0,1], [-1,0], [-a1,-b1], [-c1,-d1]]

    def qubit_label(self, i, j):
        """
        Qubit label is a function that returns the label of the qubit at position (i, j).
        Qubits are on 2D lattice of size (2*self.l, 2*self.m) (Gottesman paper layout)
        """
        i = i % (2*self.l)
        j = j % (2*self.m)
        return i * self.lattice_cols + j

    def gen_data_qubit_set(self):
        """
        Generate the set of data qubits on the lattice.
        """
        self.l_data_qubits_set = []
        self.r_data_qubits_set = []
        self.data_qubits_set = []
        for i in range(self.l):
            for j in range(self.m):
                l_data_qubit = self.qubit_label(2*i,2*j)
                r_data_qubit = self.qubit_label(2*i+1, 2*j+1)
                self.l_data_qubits_set.append(l_data_qubit)
                self.r_data_qubits_set.append(r_data_qubit)
        self.data_qubits_set = sorted(self.l_data_qubits_set + self.r_data_qubits_set)

        
    def gen_stabilizer(self):
        """
        Generate a dictionary of stabilizer with above qubit label.
        The key is (ancilla qubit label, polynomial term)
        
        This method creates two dictionaries:
        1. x_stabilizers: Maps X-type stabilizer ancilla qubits to their connected data qubits
        2. z_stabilizers: Maps Z-type stabilizer ancilla qubits to their connected data qubits
        
        Each stabilizer is a 6-qubit operator corresponding to the 6 relative positions
        defined in x_rel_pos and z_rel_pos.
        """

        # Initialize dictionary for X-type stabilizers and list to store ancilla qubit labels
        self.x_stabilizers = {}
        self.x_ancilla_labels = []
        self.corresponding_z_ancillas = []
        self.corresponding_z_ancillas_50per = []
        
        # Iterate through the l×m grid of X-type stabilizers
        for i in range(self.l):
            for j in range(self.m):
                # Calculate the label for the X-type ancilla qubit at position (2i+1, 2j)
                # X-type ancilla qubits are placed at odd-even coordinates
                x_ancilla_label = self.qubit_label(2 * i + 1, 2 * j)

                # corresponding z stabilizer for the current x stabilizer, the correspondance is defined by they form a nonlocal loop via long range interaction in the BB code
                corr_z_ancilla = self.qubit_label(
                    2*i+1+self.x_rel_pos[4][0]-self.z_rel_pos[4][0],
                    2*j+self.x_rel_pos[4][1]-self.z_rel_pos[4][1]
                )
                corr_z_ancilla_50per = self.qubit_label(
                    2*i+1+self.x_rel_pos[5][0]-self.z_rel_pos[3][0],
                    2*j+self.x_rel_pos[5][1]-self.z_rel_pos[3][1]
                )
                
                # For each of the 6 data qubits connected to this stabilizer
                for k in range(6):
                    # Calculate the label of the connected data qubit using relative positions
                    # Store mapping from (ancilla, position_index) to data qubit label
                    self.x_stabilizers[(x_ancilla_label, k)] = self.qubit_label(
                        2 * i+1+self.x_rel_pos[k][0],  # Row coordinate with offset
                        2 * j+self.x_rel_pos[k][1]     # Column coordinate with offset
                    )
                # Add this ancilla qubit to the list of X-type ancilla qubits
                self.x_ancilla_labels.append(x_ancilla_label)
                self.corresponding_z_ancillas.append(corr_z_ancilla)
                self.corresponding_z_ancillas_50per.append(corr_z_ancilla_50per)
        # Initialize dictionary for Z-type stabilizers and list to store ancilla qubit labels
        self.z_stabilizers = {}
        self.z_ancilla_labels = []
        self.corresponding_x_ancillas = []
        self.corresponding_x_ancillas_50per = []


        
        # Iterate through the l×m grid of Z-type stabilizers
        for i in range(self.l):
            for j in range(self.m):
                # Calculate the label for the Z-type ancilla qubit at position (2i, 2j+1)
                # Z-type ancilla qubits are placed at even-odd coordinates
                z_ancilla_label = self.qubit_label(2 * i, 2 * j + 1)

                # corresponding x stabilizer for the current z stabilizer, the correspondance is defined by they form a nonlocal loop via long range interaction in the BB code
                corr_x_ancilla = self.qubit_label(
                    2*i+self.z_rel_pos[4][0]-self.x_rel_pos[4][0],
                    2*j+1+self.z_rel_pos[4][1]-self.x_rel_pos[4][1]
                )
                corr_x_ancilla_50per = self.qubit_label(
                    2*i+self.z_rel_pos[5][0]-self.x_rel_pos[2][0],
                    2*j+1+self.z_rel_pos[5][1]-self.x_rel_pos[2][1]
                )
                
                
                # For each of the 6 data qubits connected to this stabilizer
                for k in range(6):
                    # Calculate the label of the connected data qubit using relative positions
                    # Store mapping from (ancilla, position_index) to data qubit label
                    self.z_stabilizers[(z_ancilla_label, k)] = self.qubit_label(
                        2 * i+self.z_rel_pos[k][0],    # Row coordinate with offset
                        2 * j+1+self.z_rel_pos[k][1]   # Column coordinate with offset
                    )
                # Add this ancilla qubit to the list of Z-type ancilla qubits
                self.z_ancilla_labels.append(z_ancilla_label)
                self.corresponding_x_ancillas.append(corr_x_ancilla)
                self.corresponding_x_ancillas_50per.append(corr_x_ancilla_50per)

   
        full_qubit = self.data_qubits_set + self.x_ancilla_labels + self.z_ancilla_labels
        ## this is a stim target andd only used for appling idling error
        self.full_qubit_set = [stim.GateTarget(index) for index in full_qubit]


    # Add property getters and setters for d and z_logical_operators
    @property
    def d(self):
        """
        Getter for the code distance.
        Computes the distance only when accessed if not already computed.
        
        Returns:
            int: The code distance
        """
        if self._d is None:
            self._compute_z_logicals_and_distance()
        return self._d

    
    @property
    def z_logical_operators(self):
        """
        Getter for the Z-type logical operators.
        Computes the logical operators only when accessed if not already computed.
        
        Returns:
            list: The Z-type logical operators
        """
        if self._z_logical_operators is None:
            self._compute_z_logicals_and_distance()
        return self._z_logical_operators
    
    @property
    def x_logical_operators(self):
        """
        Getter for the X-type logical operators.
        """
        if self._x_logical_operators is None:
            self._compute_x_logicals()
        return self._x_logical_operators
    



    @property
    def params(self):
        """
        Getter for the code parameters [n, k, d].
        Ensures d is computed if needed.
        
        Returns:
            list: The code parameters [n, k, d]
        """
        return [self.n, self.k, self.d]
    
    def _compute_z_logicals_and_distance(self):
        """
        Private method to compute the minimum distance of Z-type logical operators.
        This is called internally when d or z_logical_operators are accessed.
        Uses multiprocessing to compute logical operators in parallel, bypassing the GIL.
        """
        # Initialize with maximum possible distance

        if self.k == 0:
            self._d = 0
            self._z_logical_operators = []
            return
        self._d = self.n
        self._z_logical_operators = [None] * self.k
        
        args_list = [
            (self.hx, self.qcode.lx[i,:], self.m, self.n, i) 
            for i in range(self.k)
        ]
        
        # Use ProcessPoolExecutor to parallelize the computation
        # This creates separate processes that bypass the GIL
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=min(multiprocessing.cpu_count(), self.k)
        ) as executor:
            # Process results as they complete
            for i, w, converted_logical in executor.map(compute_logical_operator, args_list):
                self._d = min(self._d, w)
                self._z_logical_operators[i] = converted_logical


    def _compute_x_logicals(self):
        """
        Private method to compute the minimum distance of Z-type logical operators.
        This is called internally when d or z_logical_operators are accessed.
        Uses multiprocessing to compute logical operators in parallel, bypassing the GIL.
        """
        # Initialize with maximum possible distance
        # self._d = self.n
        self._x_logical_operators = [None] * self.k
        
        args_list = [
            (self.hz, self.qcode.lz[i,:], self.m, self.n, i) 
            for i in range(self.k)
        ]
        
        # Use ProcessPoolExecutor to parallelize the computation
        # This creates separate processes that bypass the GIL
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=min(multiprocessing.cpu_count(), self.k)
        ) as executor:
            # Process results as they complete
            for i, w, converted_logical in executor.map(compute_logical_operator, args_list):
                # self._d = min(self._d, w)
                self._x_logical_operators[i] = converted_logical

    @property
    def z_random_logical(self):
        """
        Getter for the random Z-type logical operator.
        Computes the random logical operator only when accessed if not already computed.
        
        Returns:
            list: A randomly selected Z-type logical operator
        """
        if self._z_random_logical is None:
            self._compute_random_z_logical()
        return self._z_random_logical
    

    
    def _compute_random_z_logical(self):
        """
        Private method to compute a random Z-type logical operator.
        This is called internally when z_random_logical is accessed.
        """
        # Generate a random integer between 0 and self.k-1
        v = random.randint(0, self.k-1)
        
        # Compute the minimum-weight Z-type logical operator for the selected logical qubit
        w, z_logical = logical_operator_and_distance_compute(self.hx, self.qcode.lx[v,:])
        
        # Convert logical operator to match the code layout
        converted_logical = convert_logical_layout(z_logical, self.m, self.n)
        
        # Store the result
        self._z_random_logical = converted_logical
