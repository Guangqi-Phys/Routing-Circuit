## Noise models

*refer to Quantum 7, 1172 (2023).*

**Noise channels and the rules used to apply them:**

| Noisy Gate | Definition |
| :---: | :--- |
| AnyClifford ${ }_2(p)$ | Any two-qubit Clifford gate, followed by a two-qubit depolarizing channel of strength $p$. |
| AnyClifford $_1(p)$ | Any one-qubit Clifford gate, followed by a one-qubit depolarizing channel of strength $p$. |
| $\mathrm{R}_Z(p)$ | Initialize the qubit as $\|0\rangle$, followed by a bitflip channel of strength $p$. |
| $\mathrm{R}_X(p)$ | Initialize the qubit as $\|+\rangle$, followed by a phaseflip channel of strength $p$. |
| $M_Z(p, q)$ | Measure the qubit in the $Z$-basis, followed by a one-qubit depolarizing channel of strength $p$, and flip the value of the classical measurement result with probability $q$. |
| $M_X(p, q)$ | Measure the qubit in the $X$-basis, followed by a one-qubit depolarizing channel of strength $p$, and flip the value of the classical measurement result with probability $q$. |
| $M_{P P}(p, q)$ | Measure a Pauli product $P P$ on a pair of qubits, followed by a two-qubit depolarizing channel of strength $p$, and flip the classically reported measurement value with probability $q$. |
| Idle $(p)$ | If the qubit is not used in this time step, apply a one-qubit depolarizing channel of strength $p$. |
| ResonatorIdle $(p)$ | If the qubit is not measured or reset in a time step during which other qubits are being measured or reset, apply a one-qubit depolarizing channel of strength $p$. |


#### 1. Standard depolarizing noise model

| Standard Depolarizing |
| :--- |
| $\text{CX}(p)$ |
| $\text{AnyClifford~}_1(p)$ |
| $\mathrm{R}_{Z / X}(p)$ | 
| $M_{Z / X}(p, p)$ |
| $M_{P P}(p, p)$ |
| $\text{Idle}(p)$ |

#### 2. SI1000 noise model
- This noise model is inspired by the hardware errors experienced by superconducting transmon qubit arrays.

| Superconducting Inspired (SI1000) |
| :--- |
| $\mathrm{CZ}(p)$ |
| AnyClifford $_1(p / 10)$ |
| $\text{Init}_Z(2 p)$ |
| $M_Z(p, 5 p)$ |
| $M_{Z Z}(p, 5 p)$ |
| Idle $(p / 10)$ |
| ResonatorIdle $(2 p)$ |
