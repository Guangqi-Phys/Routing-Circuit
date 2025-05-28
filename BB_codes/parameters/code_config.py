"""
Code Configuration Module for Quantum Error Correction

This module provides a structured approach to managing code configurations
for quantum error correction codes. It defines standard parameter sets and
utilities for working with these configurations.

Each configuration specifies:
- Lattice dimensions (ell, m)
- Polynomial parameters (a, b, c, d)

We assume the code polynomials have form:
A = 1 + y + x^a*y^b
B = 1 + x + x^c*y^d

These parameters define the structure and properties of the quantum code.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np


@dataclass
class CodeConfig:
    """
    Data class representing a quantum code configuration.
    
    Attributes:
        name (str): Descriptive name of the configuration
        ell (int): First lattice dimension
        m (int): Second lattice dimension
        a (int): First polynomial parameter
        b (int): Second polynomial parameter
        c (int): Third polynomial parameter
        d (int): Fourth polynomial parameter
    """
    name: str
    ell: int
    m: int
    a: int
    b: int
    c: int
    d: int
    
    def get_params(self) -> Tuple[int, int, int, int, int, int]:
        """
        Get the normalized parameters with polynomial parameters taken modulo
        the appropriate lattice dimensions.
        
        Returns:
            Tuple[int, int, int, int, int, int]: Normalized (ell, m, a, b, c, d)
        """
        return (
            self.ell,
            self.m,
            self.a,
            self.b,
            self.c,
            self.d 
        )
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return (f"{self.name}: ell={self.ell}, m={self.m}, "
                f"a={self.a}, b={self.b}, c={self.c}, d={self.d}")


# Standard code configurations
STANDARD_CONFIGS: Dict[int, CodeConfig] = {
        1: CodeConfig(
        name="Balanced 6×6 Code",
        ell=6, m=6,
        a=3, b=-1, c=-1, d=3
    ),
    2: CodeConfig(
        name="Rectangular 3×15 Code",
        ell=3, m=15,
        a=0, b=5, c=-1, d=3
    ),
    3: CodeConfig(
        name="Balanced 7×7 Code",
        ell=7, m=7,
        a=1, b=-3, c=-3, d=1
    ),
    4: CodeConfig(
        name="Rectangular 9×6 Code",
        ell=9, m=6,
        a=3, b=-1, c=-1, d=3
    ),
    5: CodeConfig(
        name="Rectangular 12×6 Code",
        ell=12, m=6,
        a=3, b=-1, c=-1, d=3
    )
}


def get_config(config_id: int) -> CodeConfig:
    """
    Get a standard code configuration by ID.
    
    Args:
        config_id (int): The configuration ID
        
    Returns:
        CodeConfig: The requested configuration
        
    Raises:
        ValueError: If the configuration ID is invalid
    """
    if config_id not in STANDARD_CONFIGS:
        valid_ids = ", ".join(str(k) for k in sorted(STANDARD_CONFIGS.keys()))
        raise ValueError(
            f"Invalid configuration ID: {config_id}. "
            f"Valid options are: {valid_ids}"
        )
    
    return STANDARD_CONFIGS[config_id]


def create_custom_config(
    name: str,
    ell: int,
    m: int,
    a: int,
    b: int,
    c: int,
    d: int
) -> CodeConfig:
    """
    Create a custom code configuration.
    
    Args:
        name (str): Descriptive name for the configuration
        ell (int): First lattice dimension
        m (int): Second lattice dimension
        a (int): First polynomial parameter
        b (int): Second polynomial parameter
        c (int): Third polynomial parameter
        d (int): Fourth polynomial parameter
        
    Returns:
        CodeConfig: The custom configuration
    """
    return CodeConfig(name=name, ell=ell, m=m, a=a, b=b, c=c, d=d)


def list_available_configs() -> str:
    """
    Get a formatted string listing all available standard configurations.
    
    Returns:
        str: Formatted string with configuration details
    """
    result = "Available standard configurations:\n"
    for config_id, config in sorted(STANDARD_CONFIGS.items()):
        result += f"{config_id}: {config}\n"
    return result


if __name__ == "__main__":
    # Example usage
    print(list_available_configs())
    
    # Get a standard configuration
    config = get_config(1)
    print(f"\nSelected configuration: {config}")
    
    # Get normalized parameters
    ell, m, a, b, c, d = config.get_normalized_params()
    print(f"Normalized parameters: ell={ell}, m={m}, a={a}, b={b}, c={c}, d={d}")
    
    # Create a custom configuration
    custom = create_custom_config(
        name="Custom 5×5 Code",
        ell=5, m=5,
        a=2, b=1, c=1, d=2
    )
    print(f"\nCustom configuration: {custom}") 