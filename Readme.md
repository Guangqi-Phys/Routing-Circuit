# Routing Circuit Simulations on BB Codes and Surface Codes (with stim)

## Overview

This project provides simulations for routing circuits using BB codes and Surface codes. The simulations are implemented using the  [`Stim`](https://github.com/quantumlib/Stim) library.

## Directory Structure

- **BB_codes/**: Contains the implementation and resources related to BB codes.
  - **test/**: Main simulation programs for BB code.
  - **src/**: Source code for BB code simulations.
  - **circ_gen/**: Circuit generation scripts for BB codes.
  - **noise_model/**: Noise models
  - **parameters/**: Configuration and parameter files for BB code simulations.

- **Surface_codes/**: Contains the implementation and resources related to Surface codes.
  - **test/**: Main simulation programs for Surface code.
  - **circ_gen/**: Circuit generation scripts for Surface codes.
  - **noise_model/**: Noise models.
  - **parameters/**: Configuration and parameter files for Surface code simulations.
  - **src/**: Source code for Surface code simulations.

## Getting Started

### Prerequisites

- see `requirements.txt`



### Usage

1. Navigate to the desired code directory (e.g., `BB_codes/test` or `Surface_codes/test`).
2. Run the simulation scripts:
   ```bash
   python <script-name>.py
   ```


## Acknowledgments

- Thanks to the developers of [`Stim`](https://github.com/quantumlib/Stim) for providing a powerful tool for quantum circuit simulations.

