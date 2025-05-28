class BposdParameters:
    """
    Parameters for the BPOSD algorithm.
    """
    def __init__(self):
        self.max_iter = 20 #the maximum number of iterations for BP
        self.ms_scaling_factor = 0 #the min sum scaling factor. If set to zero the variable scaling factor method is used
        self.osd_method = "osd_cs" #the OSD method. Choose from:  1) "osd_e", "osd_cs", "osd0"
        self.bp_method = "ms"
        self.osd_order = 20 #the OSD search depth.

    def get_params(self):
        return self.max_iter, self.ms_scaling_factor, self.osd_method, self.bp_method, self.osd_order
