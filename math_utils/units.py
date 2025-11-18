import numpy as np
from collections import Counter

class Unit:
    """
    A simple class to represent a physical unit and its dimensions.
    Dimensions are stored as a Counter of base dimension powers, e.g., {'L': 1, 'T': -2}.
    """
    def __init__(self, name, dimension, scale=1.0):
        self.name = name
        self.dimension = Counter(dimension)
        self.scale = scale  # Conversion factor to the base SI unit

    def __repr__(self):
        return f"{self.name}"

    def __mul__(self, other):
        new_dim = self.dimension + other.dimension
        new_scale = self.scale * other.scale
        new_name = f"({self.name}*{other.name})"
        return Unit(new_name, new_dim, new_scale)

    def __truediv__(self, other):
        new_dim = self.dimension - other.dimension
        new_scale = self.scale / other.scale
        new_name = f"({self.name}/{other.name})"
        return Unit(new_name, new_dim, new_scale)

    def __pow__(self, power):
        new_dim = {k: v * power for k, v in self.dimension.items()}
        new_scale = self.scale ** power
        new_name = f"({self.name}^{power})"
        return Unit(new_name, Counter(new_dim), new_scale)

    def is_compatible(self, other):
        return self.dimension == other.dimension

class UnitRegistry:
    """A registry for managing units and conversions."""
    def __init__(self):
        self.units = {}

    def add_unit(self, unit):
        self.units[unit.name] = unit

    def get_unit(self, name):
        if name in self.units:
            return self.units[name]
        # Basic support for compound units
        if '*' in name:
            parts = name.split('*')
            unit = self.get_unit(parts[0])
            for part in parts[1:]:
                unit *= self.get_unit(part)
            return unit
        if '/' in name:
            parts = name.split('/')
            unit = self.get_unit(parts[0])
            for part in parts[1:]:
                unit /= self.get_unit(part)
            return unit
        raise ValueError(f"Unit '{name}' not found.")

# Example SI unit system
si_registry = UnitRegistry()
si_registry.add_unit(Unit('m', {'L': 1}, 1.0))
si_registry.add_unit(Unit('s', {'T': 1}, 1.0))
si_registry.add_unit(Unit('kg', {'M': 1}, 1.0))

# Derived units
si_registry.add_unit(Unit('N', {'M': 1, 'L': 1, 'T': -2}, 1.0)) # Newton
si_registry.add_unit(Unit('J', {'M': 1, 'L': 2, 'T': -2}, 1.0)) # Joule

class Quantity:
    """Represents a value with a unit."""
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def to(self, target_unit):
        """Converts the quantity to a different unit."""
        if not self.unit.is_compatible(target_unit):
            raise ValueError("Incompatible dimensions for conversion.")

        converted_value = self.value * self.unit.scale / target_unit.scale
        return Quantity(converted_value, target_unit)

    def __repr__(self):
        return f"{self.value} {self.unit.name}"

    def __add__(self, other):
        if not self.unit.is_compatible(other.unit):
            raise ValueError("Incompatible units for addition.")

        other_val_converted = other.to(self.unit).value
        return Quantity(self.value + other_val_converted, self.unit)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Quantity(self.value * other, self.unit)
        new_value = self.value * other.value
        new_unit = self.unit * other.unit
        return Quantity(new_value, new_unit)
