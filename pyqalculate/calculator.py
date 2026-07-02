"""Calculator - the main entry point for PyQalculate.

Mirrors libqalculate's Calculator class. This is the central object
that manages definitions, parsing, calculation, and output.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from pyqalculate.parser import Parser
from pyqalculate.types import (
    ApproximationMode,
    EvaluationOptions,
    ParseOptions,
    PrintOptions,
    DEFAULT_PRECISION,
    ExpressionItemType,
)

if TYPE_CHECKING:
    from pyqalculate.expression_item import ExpressionItem
    from pyqalculate.function import MathFunction
    from pyqalculate.math_structure import MathStructure
    from pyqalculate.unit import Unit
    from pyqalculate.variable import Variable


# ---------------------------------------------------------------------------
# Path to the data directory
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).resolve().parent.parent / "pyqalculate_data"


class Calculator:
    """The main calculator object.

    Manages all definitions (functions, variables, units, prefixes),
    parsing of expressions, calculation, and formatting of results.

    Usage:
        calc = Calculator()
        calc.load_definitions()
        result = calc.calculate("1 + 1")
        print(result)
    """

    def __init__(self) -> None:
        self._precision = DEFAULT_PRECISION
        self._precision_is_set = False  # True when user explicitly calls set_precision()
        self._parser = Parser(self)
        self._functions: dict[str, MathFunction] = {}
        self._variables: dict[str, Variable] = {}
        self._units: dict[str, Unit] = {}
        self._unit_names: dict[str, list[str]] = {}  # lowercase name -> list of unit keys
        self._prefixes: list = []
        self._datasets: dict[str, object] = {}
        self._categories: list[str] = []
        self._exchange_rates_loaded = False
        self._definitions_loaded = False

    # -- Precision --

    def get_precision(self) -> int:
        """Return the current precision (number of significant digits)."""
        return self._precision

    def set_precision(self, precision: int) -> None:
        """Set the precision for calculations."""
        self._precision = max(1, precision)
        self._precision_is_set = True

    # -- Definition management --

    def add_function(self, func: MathFunction) -> None:
        """Register a mathematical function."""
        func.set_registered(True)
        self._functions[func.name().lower()] = func

    def add_variable(self, var: Variable) -> None:
        """Register a variable."""
        var.set_registered(True)
        self._variables[var.name().lower()] = var
        # Index all names for lookup
        for i in range(1, var.count_names() + 1):
            ename = var.get_name(i)
            if ename is not None and ename.name:
                lower = ename.name.lower()
                if lower not in self._variables:
                    self._variables[lower] = var

    def add_unit(self, unit: Unit) -> None:
        """Register a unit."""
        unit.set_registered(True)
        key = unit.name()
        self._units[key] = unit

        # Index all names for lookup
        for n in unit._names:
            lower = n.name.lower()
            if lower not in self._unit_names:
                self._unit_names[lower] = []
            if key not in self._unit_names[lower]:
                self._unit_names[lower].append(key)

    def add_prefix(self, prefix: object) -> None:
        """Register a prefix."""
        self._prefixes.append(prefix)

    def get_function(self, name: str) -> MathFunction | None:
        """Look up a function by name (case-insensitive)."""
        return self._functions.get(name.lower())

    def get_variable(self, name: str) -> Variable | None:
        """Look up a variable by name (case-insensitive)."""
        return self._variables.get(name.lower())

    def get_unit(self, name: str) -> Unit | None:
        """Look up a unit by name.

        Priority order:
        1. Exact (case-sensitive) direct lookup
        2. Prefix decomposition with EXACT remainder (e.g., MJ = M + J)
        3. Case-insensitive full-name fallback (e.g., cal → cal_th)
        4. Prefix decomposition with case-insensitive remainder (e.g., kcal = k + cal)
        """
        # Step 1: Exact (case-sensitive) direct lookup
        if name in self._units:
            return self._units[name]

        # Step 1.5: Check if the full name is a known alias (case-insensitive).
        # If so, skip prefix decomposition to avoid "days" → da+ys misparse.
        lower = name.lower()
        alias_keys = self._unit_names.get(lower, [])
        if alias_keys:
            for key in alias_keys:
                if key == name:
                    return self._units.get(key)
            return self._units.get(alias_keys[0])

        # Step 2: Prefix decomposition with exact remainder.
        # Sort prefixes by short name length (longest first) for greedy match.
        for prefix in sorted(self._prefixes, key=lambda p: len(p.short_name()), reverse=True):
            pfx_name = prefix.short_name()
            if not pfx_name:
                continue
            if name.startswith(pfx_name) and len(name) > len(pfx_name):
                remainder = name[len(pfx_name):]
                if remainder in self._units:
                    return self._units[remainder]

        # Step 3: Case-insensitive full-name fallback
        lower = name.lower()
        keys = self._unit_names.get(lower, [])
        if keys:
            for key in keys:
                if key == name:
                    return self._units.get(key)
            return self._units.get(keys[0])

        # Step 4: Prefix decomposition with case-insensitive remainder.
        # This catches "kcal" = k(ilo) + cal(orie) when "cal" is not an exact key
        # but IS found via case-insensitive lookup. Runs AFTER step 3 so that
        # "cal" itself is found first (avoids "cal" → c(enti)+aL bug).
        for prefix in sorted(self._prefixes, key=lambda p: len(p.short_name()), reverse=True):
            pfx_name = prefix.short_name()
            if not pfx_name:
                continue
            if name.startswith(pfx_name) and len(name) > len(pfx_name):
                remainder = name[len(pfx_name):]
                lower_rem = remainder.lower()
                rem_keys = self._unit_names.get(lower_rem, [])
                if rem_keys:
                    return self._units.get(rem_keys[0])

        return None

    def get_item(self, name: str) -> ExpressionItem | None:
        """Look up any expression item by name.

        When both a unit and a variable match, the unit takes precedence
        to prevent variables (e.g., speed of light 'c') from shadowing
        units (e.g., Coulomb 'C') during parsing.
        """
        unit = self.get_unit(name)
        var = self.get_variable(name)
        # If both match, prefer the unit with an exact (case-sensitive) key
        if unit is not None and var is not None:
            if name in self._units:
                return unit
            return var
        if var is not None:
            return var
        func = self.get_function(name)
        if func is not None:
            return func
        return unit

    def has_function(self, name: str) -> bool:
        return name.lower() in self._functions

    def has_variable(self, name: str) -> bool:
        return name.lower() in self._variables

    def has_unit(self, name: str) -> bool:
        return self.get_unit(name) is not None

    # -- Count --

    def count_functions(self) -> int:
        return len(self._functions)

    def count_variables(self) -> int:
        return len(self._variables)

    def count_units(self) -> int:
        return len(self._units)

    # -- Definition loading --

    def load_definitions(self) -> None:
        """Load all built-in definitions (functions, variables, units, prefixes)."""
        global _calculator
        self._load_builtin_functions()
        self._load_builtin_variables()
        self._load_builtin_units()
        self._load_builtin_prefixes()
        self._definitions_loaded = True
        # Set as global calculator so variable expression resolution works
        # (KnownVariable expressions reference other variables that need evaluation)
        _calculator = self

    def load_global_definitions(self) -> None:
        """Load global definitions from JSON data files.

        Loads all variables from variables.json (166+ variables/constants)
        and datasets from elements.json and planets.json.
        """
        if not _DATA_DIR.is_dir():
            return
        self._load_variables_from_json()
        self._load_elements_dataset()
        self._load_planets_dataset()
        self._definitions_loaded = True

    def load_exchange_rates(self) -> None:
        """Load currency exchange rates."""
        # TODO: load from rates.json or fetch online
        self._exchange_rates_loaded = True

    def _load_builtin_functions(self) -> None:
        """Register builtin mathematical functions."""
        from pyqalculate.builtin_functions import get_default_registry
        registry = get_default_registry()
        for name in registry.names():
            func = registry.get_by_name(name)
            if func is not None:
                self.add_function(func)

    def _load_builtin_variables(self) -> None:
        """Register builtin variables (pi, e, etc.)."""
        from pyqalculate.variable import KnownVariable
        # Pi
        pi_var = KnownVariable("Constants", "pi", "3.14159265358979323846",
                               "Pi - ratio of circumference to diameter")
        pi_var.add_name("\u03c0")
        self.add_variable(pi_var)
        # e
        e_var = KnownVariable("Constants", "e", "2.71828182845904523536",
                              "Euler's number - base of natural logarithm")
        self.add_variable(e_var)

    def _load_builtin_units(self) -> None:
        """Register builtin units from JSON definitions."""
        from pyqalculate.definitions import load_prefixes, load_units, load_currencies
        load_prefixes(self)
        load_units(self)
        load_currencies(self)

    def _load_builtin_prefixes(self) -> None:
        """Register builtin prefixes (already loaded with units)."""
        pass  # Prefixes are loaded together with units

    def _load_variables_from_json(self) -> None:
        """Load ALL variables from pyqalculate_data/variables.json.

        Handles the full JSON structure including:
        - Nested category arrays (Physical Constants has sub-categories)
        - builtin_variable entries (pi, e, euler, catalan, i, etc.)
        - unknown entries (x, y, z)
        - variable entries with dict values (containing @unit, #text)
        - Unicode multiplication sign × replaced with *
        """
        json_path = _DATA_DIR / "variables.json"
        if not json_path.is_file():
            return

        from pyqalculate.variable import KnownVariable, UnknownVariable

        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return

        for category_block in data:
            cat_title = category_block.get("title", "")
            self._process_variable_category(cat_title, category_block)

    def _process_variable_category(self, cat_title: str, block: dict) -> None:
        """Process a single category block from variables.json.

        Recursively handles nested categories.
        """
        from pyqalculate.variable import KnownVariable, UnknownVariable

        # Process "variable" entries (simple key-value)
        for var_def in block.get("variable", []):
            title = var_def.get("title", "")
            names_raw = var_def.get("names", "")
            value_raw = var_def.get("value", "")
            names_str = self._extract_names_str(names_raw)
            if not names_str:
                continue

            # Extract value string from dict or string
            value_str = self._extract_value_str(value_raw)
            if not value_str:
                continue

            # Extract @unit if present (stored for unit-aware evaluation)
            unit_str = ""
            if isinstance(value_raw, dict):
                unit_str = value_raw.get("@unit", "")

            # Clean up Unicode characters
            value_str = value_str.replace("×", "*").replace("−", "-")

            primary_name = self._parse_primary_name(names_str)
            if not primary_name:
                continue

            var = KnownVariable(cat_title, primary_name, value_str, title)
            # Store unit for leaf variables (direct numeric values, not expressions)
            # This allows unit-aware evaluation (e.g., boltzmann * 300 K → J)
            if unit_str and not any(c in value_str for c in "*/^()"):
                var.set_unit(unit_str)
            # Register additional names
            for name_entry in names_str.split(","):
                name_entry = name_entry.strip()
                if ":" in name_entry:
                    prefix, name = name_entry.split(":", 1)
                    if name and name != primary_name:
                        var.add_name(name)
                elif name_entry and name_entry != primary_name:
                    var.add_name(name_entry)

            self.add_variable(var)

        # Process "builtin_variable" entries (pi, e, euler, catalan, etc.)
        builtin_vars = block.get("builtin_variable", [])
        if isinstance(builtin_vars, dict):
            builtin_vars = [builtin_vars]
        for var_def in builtin_vars:
            builtin_name = var_def.get("@name", "")
            title = var_def.get("title", "")
            names_raw = var_def.get("names", "")
            names_str = self._extract_names_str(names_raw)

            if not builtin_name:
                continue

            # These are builtin variables that may already be loaded
            # Add additional names if they exist
            existing = self.get_variable(builtin_name)
            if existing is not None and names_str:
                for name_entry in names_str.split(","):
                    name_entry = name_entry.strip()
                    if ":" in name_entry:
                        _, name = name_entry.split(":", 1)
                        if name and name.lower() != builtin_name.lower():
                            existing.add_name(name)
                    elif name_entry and name_entry.lower() != builtin_name.lower():
                        existing.add_name(name_entry)

        # Process "unknown" entries (x, y, z)
        unknown_vars = block.get("unknown", [])
        if isinstance(unknown_vars, dict):
            unknown_vars = [unknown_vars]
        for var_def in unknown_vars:
            names_raw = var_def.get("names", "")
            names_str = self._extract_names_str(names_raw)
            if not names_str:
                continue

            primary_name = self._parse_primary_name(names_str)
            if not primary_name:
                continue

            var = UnknownVariable(cat_title, primary_name, title=var_def.get("title", ""))
            # Register additional names
            for name_entry in names_str.split(","):
                name_entry = name_entry.strip()
                if ":" in name_entry:
                    prefix, name = name_entry.split(":", 1)
                    if name and name != primary_name:
                        var.add_name(name)
                elif name_entry and name_entry != primary_name:
                    var.add_name(name_entry)

            self.add_variable(var)

        # Process nested "category" arrays (Physical Constants has sub-categories)
        for sub_cat in block.get("category", []):
            sub_title = sub_cat.get("title", cat_title)
            self._process_variable_category(sub_title, sub_cat)

    @staticmethod
    def _extract_names_str(names_raw: str | dict) -> str:
        """Extract the names string from either a plain string or a {#text, @translatable} dict."""
        if isinstance(names_raw, str):
            return names_raw
        if isinstance(names_raw, dict):
            return names_raw.get("#text", "")
        return ""

    @staticmethod
    def _extract_value_str(value_raw: str | dict) -> str:
        """Extract the value string from either a plain string or a dict with #text, @unit, etc.

        Handles formats:
        - Simple string: "3.14159"
        - Dict with #text: {"#text": "6.62607015E-34", "@unit": "J*s"}
        - Dict with #text and @uncertainty: {"#text": "7.29735256434E-3", "@uncertainty": "1.13E-12"}
        """
        if isinstance(value_raw, str):
            return value_raw
        if isinstance(value_raw, dict):
            return value_raw.get("#text", "")
        return ""

    @staticmethod
    def _parse_primary_name(names_str: str) -> str:
        """Parse a names string and return the primary name.

        Names format: "r:name1,a:name2,au:name3"
        Prefixes: r=reference, a=abbreviation, au=abbreviation unicode
        Returns the reference name if present, otherwise the first name.
        """
        ref_name = ""
        first_name = ""
        for entry in names_str.split(","):
            entry = entry.strip()
            if not entry:
                continue
            if ":" in entry:
                prefix, name = entry.split(":", 1)
                name = name.strip()
                if not name:
                    continue
                if prefix == "r":
                    return name
                if not first_name:
                    first_name = name
            else:
                if not first_name:
                    first_name = entry
        return first_name or ref_name

    # -- Dataset loading --

    def _load_elements_dataset(self) -> None:
        """Load chemical elements dataset from elements.json.

        Creates a DataSet with 118 elements and properties like
        symbol, number, weight, boiling, melting, density, etc.
        """
        json_path = _DATA_DIR / "elements.json"
        if not json_path.is_file():
            return

        import json as _json
        from pyqalculate.dataset import DataSet, DataObject, DataProperty
        from pyqalculate.types import PropertyType

        try:
            with open(json_path, encoding="utf-8") as f:
                data = _json.load(f)
        except (_json.JSONDecodeError, OSError):
            return

        if not isinstance(data, list):
            return

        # Create the dataset
        ds = DataSet(category="Data Sets", name="elements",
                     title="Chemical Elements",
                     description="Periodic table of elements")

        # Define properties
        prop_name = DataProperty(ds, "name", "Name", "Element name")
        prop_name.set_key(True)
        prop_name.set_property_type(PropertyType.STRING)
        ds.add_property(prop_name)

        prop_symbol = DataProperty(ds, "symbol", "Symbol", "Chemical symbol")
        ds.add_property(prop_symbol)

        prop_number = DataProperty(ds, "number", "Number", "Atomic number")
        ds.add_property(prop_number)

        prop_weight = DataProperty(ds, "weight", "Weight", "Atomic weight")
        ds.add_property(prop_weight)

        prop_class = DataProperty(ds, "class", "Class", "Element class")
        ds.add_property(prop_class)

        for field in ("boiling", "melting", "density", "x_pos", "y_pos"):
            title = field.replace("_", " ").title()
            dp = DataProperty(ds, field, title, f"Element {title}")
            if field in ("x_pos", "y_pos"):
                dp.set_hidden(True)
            ds.add_property(dp)

        # Add objects
        for elem in data:
            if not isinstance(elem, dict):
                continue
            obj = DataObject(ds)
            obj.set_property("name", elem.get("name", ""))
            obj.set_property("symbol", elem.get("@symbol", ""))
            obj.set_property("number", elem.get("@number", ""))
            obj.set_property("weight", elem.get("weight", ""))
            obj.set_property("class", elem.get("class", ""))
            for field in ("boiling", "melting", "density", "x_pos", "y_pos"):
                val = elem.get(field, "")
                if val:
                    obj.set_property(field, str(val))
            ds.add_object(obj)

        ds.set_objects_loaded(True)
        ds.set_default_property("symbol")
        self._datasets["elements"] = ds
        self.add_function(ds)

    def _load_planets_dataset(self) -> None:
        """Load planets dataset from planets.json.

        Creates a DataSet with 10 planets/solar system bodies and properties
        like mass, radius, density, gravity, temperature, etc.
        """
        json_path = _DATA_DIR / "planets.json"
        if not json_path.is_file():
            return

        import json as _json
        import re as _re
        from pyqalculate.dataset import DataSet, DataObject, DataProperty
        from pyqalculate.types import PropertyType

        try:
            with open(json_path, encoding="utf-8") as f:
                data = _json.load(f)
        except (_json.JSONDecodeError, OSError):
            return

        if not isinstance(data, list):
            return

        # Create the dataset
        ds = DataSet(category="Data Sets", name="planet",
                     title="Planets",
                     description="Solar system planets and bodies")
        ds._calculator = self  # back-reference for unit lookup

        # Define properties
        prop_name = DataProperty(ds, "name", "Name", "Planet name")
        prop_name.set_key(True)
        prop_name.set_property_type(PropertyType.STRING)
        ds.add_property(prop_name)

        planet_fields = [
            ("year", "Orbital Period", "Orbital period in days"),
            ("speed", "Orbital Speed", "Orbital speed in km/s"),
            ("eccentricity", "Eccentricity", "Orbital eccentricity"),
            ("inclination", "Inclination", "Orbital inclination in degrees"),
            ("satellites", "Satellites", "Number of satellites"),
            ("mass", "Mass", "Mass in kg"),
            ("density", "Density", "Mean density in g/cm³"),
            ("area", "Surface Area", "Surface area in km²"),
            ("gravity", "Surface Gravity", "Surface gravity in m/s²"),
            ("temperature", "Temperature", "Mean temperature in K"),
            ("radius", "Radius", "Mean radius in km"),
        ]

        for field, title, desc in planet_fields:
            dp = DataProperty(ds, field, title, desc)
            if field == "satellites":
                dp.set_property_type(PropertyType.NUMBER)
            ds.add_property(dp)

        # Add objects
        for planet in data:
            if not isinstance(planet, dict):
                continue
            obj = DataObject(ds)
            name = planet.get("name", "")
            # Clean up name: remove "!planets!" prefix
            if name.startswith("!"):
                parts = name.split("!")
                name = parts[-1] if parts else name
            obj.set_property("name", name)
            for field, _, _ in planet_fields:
                val = planet.get(field, "")
                if val:
                    obj.set_property(field, str(val))
            # Also store any extra fields (e.g., *_unit, distance_from_earth)
            known = {f for f, _, _ in planet_fields} | {"name"}
            for key, val in planet.items():
                if key not in known and val:
                    obj.set_property(key, str(val))
            ds.add_object(obj)

        ds.set_objects_loaded(True)
        ds.set_default_property("name")
        self._datasets["planet"] = ds
        self.add_function(ds)

    def get_dataset(self, name: str):
        """Look up a dataset by name."""
        from pyqalculate.dataset import DataSet
        result = self._datasets.get(name.lower())
        if isinstance(result, DataSet):
            return result
        return None

    # -- Parsing --

    def parse(
        self,
        expression: str,
        po: ParseOptions | None = None,
    ) -> MathStructure:
        """Parse an expression string into a MathStructure."""
        return self._parser.parse(expression, po)

    # -- Calculation --

    def calculate(
        self,
        expression: str,
        timeout_ms: int = 0,
        eo: EvaluationOptions | None = None,
    ) -> MathStructure:
        """Parse and calculate an expression.

        Args:
            expression: The expression string.
            timeout_ms: Timeout in milliseconds (0 = no timeout).
            eo: Evaluation options.

        Returns:
            A MathStructure with the result.
        """
        if eo is None:
            eo = EvaluationOptions()
        mstruct = self.parse(expression)

        # Handle unit conversion: "expr to unit"
        if mstruct.is_unit_conversion() and len(mstruct) == 2:
            # Check for base conversion targets: "to hex", "to bin", "to oct", "to roman", "to bases"
            target = mstruct[1]
            # Determine target name — may be single symbol or multi-word (partial fraction)
            if target.is_symbolic():
                base_func_name = target.symbol.lower()
            elif target.is_multiplication():
                # Multi-word target like "partial fraction" parsed as "partial" * "fraction"
                # Also handles "base N" parsed as symbol "base" * N
                parts = []
                for child in target:
                    if child.is_symbolic():
                        parts.append(child.symbol.lower())
                    elif child.is_unit() and child.unit is not None:
                        parts.append(child.unit.name().lower())
                base_func_name = " ".join(parts) if parts else ""
                # Check for "base N" pattern: symbol "base" * number/expression
                if (len(target) >= 2 and target[0].is_symbolic()
                        and target[0].symbol.lower() == "base"):
                    base_func = self.get_function("base")
                    if base_func is not None:
                        value_result = mstruct[0].evaluate(eo)
                        base_arg = target[1]
                        # Evaluate the base argument (handles sqrt(2), etc.)
                        base_result = base_arg.evaluate(eo)
                        # If base is not a number (e.g., sqrt(2) → POWER),
                        # force numeric approximation
                        if not base_result.is_number():
                            try:
                                import sympy as sp
                                sp_val = base_result.to_sympy()
                                if sp_val is not None:
                                    from pyqalculate.math_structure import MathStructure as MS
                                    from pyqalculate.number import Number as Num
                                    float_val = float(sp.N(sp_val, 15))
                                    base_result = MS.from_number(Num(float_val))
                            except Exception:
                                pass
                        return base_func.calculate([value_result, base_result], eo)
            else:
                base_func_name = ""

            if base_func_name:
                base_func_map = {
                    "hex": "hex", "octal": "oct", "oct": "oct",
                    "bin": "bin", "binary": "bin",
                    "roman": "roman", "bases": "bases",
                    "float": "float",
                }
                if base_func_name in base_func_map:
                    func = self.get_function(base_func_map[base_func_name])
                    if func is not None:
                        # Evaluate the value expression first
                        value_result = mstruct[0].evaluate(eo)
                        return func.calculate([value_result], eo)
                # Handle "to binN" pattern (e.g., "to bin16", "to bin8")
                import re
                bin_width_match = re.match(r'^bin(\d+)$', base_func_name)
                if bin_width_match:
                    width = int(bin_width_match.group(1))
                    bin_func = self.get_function("bin")
                    if bin_func is not None:
                        value_result = mstruct[0].evaluate(eo)
                        from pyqalculate.math_structure import MathStructure as MS
                        width_struct = MS(width)
                        return bin_func.calculate([value_result, width_struct], eo)
                # Handle "to fraction" as a special display command
                if base_func_name == "fraction":
                    from pyqalculate.types import NumberFractionFormat
                    from pyqalculate.number import Number as NumType
                    from pyqalculate.math_structure import MathStructure as MS2
                    value_result = mstruct[0].evaluate(eo)
                    if value_result.is_number() and value_result.number is not None:
                        num = value_result.number
                        # Convert float to rational if needed
                        if not num.is_rational():
                            try:
                                from fractions import Fraction
                                frac = Fraction(num.to_float()).limit_denominator(10000)
                                num = NumType.from_rational(frac.numerator, frac.denominator)
                                value_result = MS2.from_number(num)
                            except Exception:
                                pass
                        # Return the number with fraction format flag
                        value_result._number_fraction_format = NumberFractionFormat.COMBINED
                        return value_result
                # Handle "to factors" — polynomial factorization
                if base_func_name == "factors":
                    import sympy as sp
                    from pyqalculate.math_structure import MathStructure as MS2
                    value_result = mstruct[0].evaluate(eo)
                    try:
                        sympy_expr = value_result.to_sympy()
                        factored = sp.factor(sympy_expr)
                        return MS2.from_sympy(factored)
                    except Exception:
                        return value_result
                # Handle "to partial fraction" — partial fraction decomposition
                if base_func_name in ("partial fraction", "partial_fraction", "apart"):
                    import sympy as sp
                    from pyqalculate.math_structure import MathStructure as MS2
                    value_result = mstruct[0].evaluate(eo)
                    try:
                        sympy_expr = value_result.to_sympy()
                        apart = sp.apart(sympy_expr)
                        return MS2.from_sympy(apart)
                    except Exception:
                        return value_result
                # Handle "to time" — format as HH:MM
                if base_func_name == "time":
                    return self._handle_to_time(mstruct[0], eo)
                # Handle "to utc", "to utc+N", "to gmt", "to gmt+N"
                if base_func_name in ("utc", "gmt") or (
                    len(base_func_name) > 3
                    and base_func_name[:3] in ("utc", "gmt")
                    and base_func_name[3] in "+-"
                ):
                    return self._handle_to_timezone(mstruct[0], base_func_name, eo)
                # Handle "to calendars"
                if base_func_name == "calendars":
                    return self._handle_to_calendars(mstruct[0], eo)
            return self._evaluate_unit_conversion(mstruct, eo)

        # Handle WHERE clause: "equation where condition"
        if mstruct.is_where() and len(mstruct) >= 2:
            import sympy as sp
            from pyqalculate.math_structure import MathStructure as MS2
            from pyqalculate.types import ComparisonType
            main_expr = mstruct[0]
            conditions = [mstruct[i] for i in range(1, len(mstruct))]
            try:
                sympy_eq = main_expr.to_sympy()
                # If the main expression is an equation, solve it
                if isinstance(sympy_eq, sp.Eq):
                    # Find the variable to solve for
                    free = sympy_eq.free_symbols
                    if len(free) == 1:
                        var = free.pop()
                        solutions = sp.solve(sympy_eq, var)
                        # Filter solutions by conditions
                        for cond_s in conditions:
                            cond_sympy = cond_s.to_sympy()
                            filtered = []
                            for sol in solutions:
                                # Check if solution satisfies condition
                                test = cond_sympy.subs(var, sol)
                                try:
                                    test_result = bool(test == sp.true)
                                    if not test_result and hasattr(test, 'doit'):
                                        test_result = bool(test.doit() == sp.true)
                                    if test_result:
                                        filtered.append(sol)
                                except Exception:
                                    filtered.append(sol)
                            solutions = filtered
                        if len(solutions) == 1:
                            # Return "x = val" form
                            return MS2.comparison(
                                MS2.from_symbol(str(var)),
                                MS2.from_sympy(solutions[0]),
                                ComparisonType.EQUALS,
                            )
                        elif solutions:
                            return MS2.vector(*[MS2.from_sympy(s) for s in solutions])
            except Exception:
                pass
            # Fallback: evaluate main expression
            return main_expr.evaluate(eo)

        # Handle date arithmetic: "2024-06-15 + 100 days"
        date_result = self._try_date_arithmetic(mstruct, eo)
        if date_result is not None:
            return date_result

        result = mstruct.evaluate(eo)

        # Post-processing: if the result contains units with fractional exponents
        # (e.g., K^0.5 from sqrt(constant * K)), the unit algebra can't simplify.
        # In approximate mode, strip the fractional-unit part and return the numeric value.
        # This handles cases like "planck / sqrt(2 * pi * m_e * k_B * 300 K)"
        # where K^0.5 prevents simplification but the numeric value is correct.
        if eo.approximation == ApproximationMode.APPROXIMATE:
            result = self._strip_fractional_units(result)

        return result

    def _strip_fractional_units(self, mstruct: "MathStructure") -> "MathStructure":
        """Strip units with fractional exponents from a result, returning the numeric value.

        If the structure is a multiplication containing units with non-integer exponents,
        compute the pure numeric value and return it as a number. This handles cases where
        unit algebra fails due to fractional powers (e.g., K^0.5 from sqrt expressions).
        """
        from pyqalculate.math_structure import MathStructure as MS
        from pyqalculate.types import StructureType as ST

        if not mstruct.is_multiplication():
            return mstruct

        # Check if any child has a fractional unit exponent
        has_fractional_unit = self._has_fractional_unit(mstruct)
        if not has_fractional_unit:
            return mstruct

        # Compute the pure numeric value
        raw_num = self._compute_pure_numeric(mstruct)
        if raw_num is not None:
            return MS(raw_num)
        return mstruct

    def _has_fractional_unit(self, mstruct: "MathStructure") -> bool:
        """Check if a structure contains any unit with a fractional exponent."""
        from pyqalculate.types import StructureType as ST

        if mstruct.type == ST.UNIT:
            return False  # Simple unit (exponent 1) is not fractional

        if mstruct.type == ST.POWER and len(mstruct) == 2:
            # Check if base is a unit or symbol and exponent is fractional
            base = mstruct[0]
            exp = mstruct[1]
            if (base.is_unit() or base.is_symbolic()) and exp.is_number() and exp.number is not None:
                exp_val = exp.number.to_float()
                if exp_val != int(exp_val):
                    return True

        if mstruct.type == ST.INVERSE and len(mstruct) == 1:
            return self._has_fractional_unit(mstruct[0])

        if mstruct.is_multiplication():
            return any(self._has_fractional_unit(c) for c in mstruct)

        return False

    def calculate_and_print(
        self,
        expression: str,
        timeout_ms: int = 0,
        eo: EvaluationOptions | None = None,
        po: PrintOptions | None = None,
    ) -> str:
        """Parse, calculate, and print an expression.

        Args:
            expression: The expression string.
            timeout_ms: Timeout in milliseconds (0 = no timeout).
            eo: Evaluation options.
            po: Print options (exact/approximate flags affect evaluation).

        Returns:
            The result as a formatted string.
        """
        if po is None:
            po = PrintOptions()
        if eo is None:
            eo = EvaluationOptions()

        # Propagate calculator precision to print options so that symbolic
        # results (e.g. tanh(40), sqrt(2)) are evaluated numerically.
        # Only when the user explicitly called set precision.
        if po.precision == 0 and self._precision_is_set:
            po.precision = self._precision

        # Adjust evaluation mode from print options
        if po.exact:
            eo.approximation = ApproximationMode.EXACT
        elif po.approximate or po.is_approximate:
            eo.approximation = ApproximationMode.APPROXIMATE

        result = self.calculate(expression, timeout_ms, eo)
        if result.is_undefined():
            msg = result._error_message or "Division by zero"
            return f"Error: {msg}"
        return result.print(po)

    # -- Printing --

    def print_result(
        self,
        mstruct: MathStructure,
        po: PrintOptions | None = None,
    ) -> str:
        """Format and print a MathStructure."""
        if po is None:
            po = PrintOptions()
        # Propagate calculator precision to print options
        if po.precision == 0 and self._precision_is_set:
            po.precision = self._precision
        return mstruct.print(po)

    # -- Localization --

    def unlocalize_expression(self, expression: str) -> str:
        """Convert a localized expression to standard format."""
        # TODO: handle localized decimal points, etc.
        return expression

    # -- Utility --

    def terminate(self) -> None:
        """Terminate any ongoing calculations."""
        pass

    # -- Unit conversion --

    def find_unit(self, name: str):
        """Look up a unit by name, trying various forms (abbreviation, plural, etc.).

        Searches by:
        1. Exact match (case-sensitive then insensitive)
        2. Checking all names via the name index
        3. Prefix decomposition (e.g., "kg" = "k" prefix + "g" unit)
        """
        # Direct lookup via name index
        unit = self.get_unit(name)
        if unit is not None:
            return unit

        # Try prefix decomposition
        # Sort prefixes by short name length (longest first) for greedy matching
        for prefix in sorted(self._prefixes, key=lambda p: len(p.short_name()), reverse=True):
            pfx_name = prefix.short_name()
            if not pfx_name:
                continue
            if name.startswith(pfx_name) and len(name) > len(pfx_name):
                remainder = name[len(pfx_name):]
                base_unit = self.get_unit(remainder)
                if base_unit is not None:
                    # Return the base unit - the prefix is handled separately
                    return base_unit

        return None

    def convert(
        self,
        value: float,
        from_unit,
        to_unit,
        from_exp: int = 1,
        to_exp: int = 1,
    ) -> float | None:
        """Convert a value from one unit to another.

        Follows the alias chain to a common base, computing the
        conversion factor at each step. Handles dimensional exponents
        (e.g., fl_oz = relation * in^3) and affine transforms
        (e.g., temperature: F = C * 9/5 + 32).

        Args:
            value: The numeric value to convert.
            from_unit: The source Unit object.
            to_unit: The target Unit object.

        Returns:
            The converted value, or None if conversion fails.
        """
        from pyqalculate.unit import AliasUnit, CompositeUnit, UnitSubtype

        # If units are the same, no conversion needed
        if from_unit is to_unit:
            return value

        # For composite units, convert through math structure
        if (from_unit.subtype() == UnitSubtype.COMPOSITE_UNIT or
                to_unit.subtype() == UnitSubtype.COMPOSITE_UNIT):
            return self._convert_composite(value, from_unit, to_unit)

        # Both must be alias or base units with the same base
        # Find common base by following chains

        # Forward: from_unit → base, tracking (scale, offset, exponent)
        from_scale, from_offset, from_final_exp, from_base = self._chain_to_base(from_unit)
        to_scale, to_offset, to_final_exp, to_base = self._chain_to_base(to_unit)

        if from_scale is None or to_scale is None:
            return None
        if to_scale == 0:
            return None

        # Both chains should end at the same base unit
        if from_base is not to_base:
            from pyqalculate.unit import CompositeUnit
            # Try composite conversion when at least one base is a CompositeUnit
            # (e.g., Hz=s^-1 vs rpm=turn/min, or lbf/in² vs N/m²)
            if isinstance(from_base, CompositeUnit) or isinstance(to_base, CompositeUnit):
                return self._convert_composite(
                    value * from_scale / to_scale,
                    from_unit, to_unit,
                )
            return None  # Different base units, can't convert

        if from_final_exp != to_final_exp:
            return None  # Different dimensions

        # Convert: from_unit → base → to_unit
        # from: base_value = value * from_scale + from_offset
        # to:   value = (base_value - to_offset) / to_scale
        base_value = value * from_scale + from_offset
        result = (base_value - to_offset) / to_scale
        return result

    def _chain_to_base(self, unit) -> tuple[float | None, float, int, object]:
        """Follow alias chain to base, computing cumulative (scale, offset).

        For multiplicative units: offset stays 0, scale accumulates.
        For affine units (temperatures): offset is non-zero.
            e.g. Celsius: scale=1, offset=273.15  (K = C*1 + 273.15)
            e.g. Fahrenheit: scale=5/9, offset=255.372... (K = (F+459.67)*5/9)

        Returns (scale, offset, final_exponent, base_unit) or (None, 0, 0, None).
        """
        from pyqalculate.unit import UnitSubtype, _eval_numeric_expression, _eval_nonlinear

        scale = 1.0
        offset = 0.0
        exponent = 1
        current = unit
        visited = set()

        while current is not None and current.subtype() == UnitSubtype.ALIAS_UNIT:
            if id(current) in visited:
                break
            visited.add(id(current))

            if current.has_nonlinear_expression():
                # Nonlinear (affine) transform: relation uses \\x
                # e.g. "\\x + 273.15" means base = value + 273.15
                # e.g. "(\\x+459.67)*5/9" means base = (value+459.67)*5/9
                # We need to compute: result = eval(relation with \\x=value)
                # For chain composition: new_value = eval(relation with \\x=current_value)
                # current_value = scale * original_value + offset
                # So we need to compose the affine transforms.
                #
                # If relation is f(x) = a*x + b (affine), and current = scale*x + offset:
                # f(current) = a*(scale*x + offset) + b = a*scale*x + (a*offset + b)
                # So new_scale = a*scale, new_offset = a*offset + b
                #
                # To extract a and b from the relation, evaluate at x=0 and x=1:
                # f(0) = b, f(1) = a + b, so a = f(1) - f(0)
                try:
                    f0 = _eval_nonlinear(current.expression(), 0.0)
                    f1 = _eval_nonlinear(current.expression(), 1.0)
                    a = f1 - f0  # scale factor
                    b = f0        # offset
                    new_scale = a * scale
                    new_offset = a * offset + b
                    scale = new_scale
                    offset = new_offset
                except (ValueError, ZeroDivisionError):
                    return None, 0, 0, None
            else:
                # Multiplicative transform
                try:
                    rel = _eval_numeric_expression(current.expression())
                except (ValueError, ZeroDivisionError):
                    return None, 0, 0, None

                # The relation is raised to the current exponent
                # This handles cases like: 231 in^3 * (0.0254)^3 = 0.003785 m^3
                scale *= rel ** exponent

            exponent *= current.exponent()
            current = current.base_unit()

        return scale, offset, exponent, current

    def _convert_composite(
        self,
        value: float,
        from_unit,
        to_unit,
    ) -> float | None:
        """Convert between composite units by expanding to base units."""
        from pyqalculate.unit import AliasUnit, CompositeUnit, Unit, UnitSubtype

        def _expand_to_base(unit) -> tuple[list, float]:
            """Expand a unit into its base unit components with exponents.

            Returns (list of (base_unit, exponent), multiplier).
            """
            if unit.subtype() == UnitSubtype.COMPOSITE_UNIT:
                multiplier = 1.0
                components = []
                for i in range(1, unit.count_units() + 1):
                    su = unit.get(i)
                    if su is None:
                        continue
                    bu = su.base_unit()
                    exp = su.exponent()
                    pfx = su.prefix()
                    if bu is not None:
                        if pfx is not None:
                            multiplier *= pfx.value(exp).to_float()
                        sub_components, sub_mult = _expand_to_base(bu)
                        multiplier *= sub_mult ** exp
                        for base_u, base_exp in sub_components:
                            components.append((base_u, base_exp * exp))
                return components, multiplier

            elif unit.subtype() == UnitSubtype.ALIAS_UNIT:
                # Follow chain to base, tracking cumulative exponent
                multiplier = 1.0
                cumulative_exp = 1
                current = unit
                visited = set()
                while current is not None and current.subtype() == UnitSubtype.ALIAS_UNIT:
                    if id(current) in visited:
                        break
                    visited.add(id(current))
                    try:
                        from pyqalculate.unit import _eval_numeric_expression
                        rel = _eval_numeric_expression(current.expression())
                        multiplier *= rel ** (1.0 / current.exponent()) if current.exponent() != 0 else 1.0
                    except (ValueError, ZeroDivisionError):
                        pass
                    cumulative_exp *= current.exponent()
                    current = current.base_unit()
                if current is not None:
                    # If the chain ends at a CompositeUnit, recursively expand it
                    if current.subtype() == UnitSubtype.COMPOSITE_UNIT:
                        sub_components, sub_mult = _expand_to_base(current)
                        multiplier *= sub_mult
                        return [(u, e * cumulative_exp) for u, e in sub_components], multiplier
                    return [(current, cumulative_exp)], multiplier
                return [], multiplier

            else:
                # Base unit
                return [(unit, 1)], 1.0

        from_components, from_mult = _expand_to_base(from_unit)
        to_components, to_mult = _expand_to_base(to_unit)

        # Check that components match, filtering out zero exponents
        from_dict: dict[int, int] = {}
        for bu, exp in from_components:
            from_dict[id(bu)] = from_dict.get(id(bu), 0) + exp
        from_dict = {k: v for k, v in from_dict.items() if v != 0}

        to_dict: dict[int, int] = {}
        for bu, exp in to_components:
            to_dict[id(bu)] = to_dict.get(id(bu), 0) + exp
        to_dict = {k: v for k, v in to_dict.items() if v != 0}

        if from_dict != to_dict:
            # Allow mismatch when one side has "counting" units (turn/cycle/revolution)
            # that the other lacks — these are dimensionless for frequency conversions.
            # e.g., Hz=s^-1 vs rpm=turn/min: ignore the turn component
            counting_names = {"turn", "rev", "revolution", "cycle", "cyc", "tr"}

            def _collect_chain_names(unit_obj) -> set[str]:
                """Collect all unit names from alias chain and composite parts."""
                names: set[str] = set()
                current = unit_obj
                visited: set[int] = set()
                while current is not None:
                    if id(current) in visited:
                        break
                    visited.add(id(current))
                    names.add(current.name().lower())
                    names |= {nm.name.lower() for nm in getattr(current, '_names', [])}
                    if current.subtype() == UnitSubtype.ALIAS_UNIT:
                        current = current.base_unit()
                    elif current.subtype() == UnitSubtype.COMPOSITE_UNIT:
                        # Also look inside composite parts
                        for i in range(1, current.count_units() + 1):
                            su = current.get(i)
                            if su is not None:
                                names.add(su.name().lower())
                                names |= {nm.name.lower() for nm in getattr(su, '_names', [])}
                                bu = su.base_unit()
                                if bu is not None:
                                    names.add(bu.name().lower())
                                    names |= {nm.name.lower() for nm in getattr(bu, '_names', [])}
                        break
                    else:
                        break
                return names

            from_chain_names = _collect_chain_names(from_unit)
            to_chain_names = _collect_chain_names(to_unit)

            from_has_counting = bool(from_chain_names & counting_names)
            to_has_counting = bool(to_chain_names & counting_names)

            if from_has_counting != to_has_counting:
                # One side has counting units, the other doesn't — filter them out.
                # Find the base units produced by counting units and their conversion
                # factors (e.g., turn=360*deg → factor=360, to adjust multiplier).
                counting_base_ids: set[int] = set()
                counting_factor = 1.0  # product of counting unit conversion factors
                counting_side = from_unit if from_has_counting else to_unit

                from pyqalculate.unit import _eval_numeric_expression

                def _find_counting_bases(unit_obj, visited=None):
                    """Find base units that come from counting units."""
                    nonlocal counting_factor
                    if visited is None:
                        visited = set()
                    if id(unit_obj) in visited:
                        return
                    visited.add(id(unit_obj))
                    if unit_obj.subtype() == UnitSubtype.ALIAS_UNIT:
                        unit_names = {unit_obj.name().lower()}
                        unit_names |= {nm.name.lower() for nm in getattr(unit_obj, '_names', [])}
                        if unit_names & counting_names:
                            # Follow the ENTIRE alias chain from this counting
                            # unit, accumulating all conversion factors until we
                            # reach a non-alias base.  The final base is what
                            # _expand_to_base would produce.
                            cur = unit_obj
                            chain_visited: set[int] = set()
                            while cur is not None and cur.subtype() == UnitSubtype.ALIAS_UNIT:
                                if id(cur) in chain_visited:
                                    break
                                chain_visited.add(id(cur))
                                try:
                                    counting_factor *= _eval_numeric_expression(
                                        cur.expression(),
                                    )
                                except (ValueError, ZeroDivisionError):
                                    pass
                                cur = cur.base_unit()
                            if cur is not None:
                                counting_base_ids.add(id(cur))
                        _find_counting_bases(unit_obj.base_unit(), visited)
                    elif unit_obj.subtype() == UnitSubtype.COMPOSITE_UNIT:
                        for i in range(1, unit_obj.count_units() + 1):
                            su = unit_obj.get(i)
                            if su is not None:
                                su_names = {su.name().lower()}
                                su_names |= {nm.name.lower() for nm in getattr(su, '_names', [])}
                                if su_names & counting_names:
                                    # Follow the ENTIRE chain from this sub-unit
                                    # through all aliases to reach the final base.
                                    cur = su
                                    chain_visited2: set[int] = set()
                                    while cur is not None and cur.subtype() == UnitSubtype.ALIAS_UNIT:
                                        if id(cur) in chain_visited2:
                                            break
                                        chain_visited2.add(id(cur))
                                        try:
                                            counting_factor *= (
                                                _eval_numeric_expression(
                                                    cur.expression(),
                                                )
                                            )
                                        except (ValueError, ZeroDivisionError):
                                            pass
                                        cur = cur.base_unit()
                                    if cur is not None:
                                        counting_base_ids.add(id(cur))
                                _find_counting_bases(su, visited)

                _find_counting_bases(counting_side)

                filtered_from = {k: v for k, v in from_dict.items()
                                 if k not in counting_base_ids}
                filtered_to = {k: v for k, v in to_dict.items()
                               if k not in counting_base_ids}
                if filtered_from == filtered_to:
                    # Adjust multiplier: divide out the counting unit's conversion
                    # factor (e.g., turn=2π·rad → divide by 2π) from whichever
                    # side carries the counting unit.
                    if to_has_counting and counting_factor != 0:
                        to_mult = to_mult / counting_factor
                    elif from_has_counting and counting_factor != 0:
                        from_mult = from_mult / counting_factor
                    return value * from_mult / to_mult

            return None  # Incompatible units

        return value * from_mult / to_mult

    def _resolve_unit_with_prefix(self, name: str) -> tuple:
        """Resolve a unit name that may have a prefix.

        Returns (unit, prefix, prefix_factor) tuple.
        If no prefix is found, prefix is None and prefix_factor is 1.0.

        Priority order:
        1. Exact (case-sensitive) direct lookup
        2. Prefix decomposition with exact prefix match (e.g., MJ = M + J)
        3. Case-insensitive fallback (only for unprefixed names)
        """
        # Step 1: Exact (case-sensitive) direct lookup
        if name in self._units:
            return self._units[name], None, 1.0

        # Step 1.5: Check if the full name is a known alias (case-insensitive).
        # If so, skip prefix decomposition to avoid "days" → da+ys misparse.
        lower = name.lower()
        alias_keys = self._unit_names.get(lower, [])
        if alias_keys:
            for key in alias_keys:
                if key == name:
                    return self._units.get(key), None, 1.0
            return self._units.get(alias_keys[0]), None, 1.0

        # Step 2: Prefix decomposition — sort by longest prefix first for greedy match
        # This MUST come before case-insensitive lookup to avoid "MJ" matching "mJ" (millijoule)
        for prefix in sorted(self._prefixes, key=lambda p: len(p.short_name()), reverse=True):
            pfx_name = prefix.short_name()
            if not pfx_name:
                continue
            if name.startswith(pfx_name) and len(name) > len(pfx_name):
                remainder = name[len(pfx_name):]
                # Try exact match on remainder first
                if remainder in self._units:
                    return self._units[remainder], prefix, prefix.value(1).to_float()
                # Try case-insensitive on remainder (but prefix must be exact)
                lower_remainder = remainder.lower()
                keys = self._unit_names.get(lower_remainder, [])
                if keys:
                    base_unit = self._units.get(keys[0])
                    if base_unit is not None:
                        return base_unit, prefix, prefix.value(1).to_float()

        # Step 3: Case-insensitive fallback (no prefix found)
        lower = name.lower()
        keys = self._unit_names.get(lower, [])
        if keys:
            # Prefer exact case match
            for key in keys:
                if key == name:
                    return self._units.get(key), None, 1.0
            return self._units.get(keys[0]), None, 1.0

        return None, None, 1.0

    def _evaluate_unit_conversion(
        self,
        mstruct: MathStructure,
        eo: EvaluationOptions,
    ) -> MathStructure:
        """Evaluate a unit conversion expression (e.g., '5 ft to m').

        Args:
            mstruct: A UNIT_CONVERSION MathStructure with [value_expr, target_unit_expr].
            eo: Evaluation options.

        Returns:
            A MathStructure with the converted value and target unit.
        """
        from pyqalculate.math_structure import MathStructure as MS
        from pyqalculate.types import StructureType as ST
        from pyqalculate.unit import AliasUnit, Unit

        value_struct = mstruct[0]
        target_struct = mstruct[1]

        # Extract the target unit name from the target structure
        target_unit_name = ""
        if target_struct.is_symbolic():
            target_unit_name = target_struct.symbol
        elif target_struct.is_unit() and target_struct.unit is not None:
            target_unit_name = target_struct.unit.name()
        elif target_struct.is_multiplication():
            # Compound target like km/h — try to build a composite unit
            target_composite = self._build_composite_from_struct(target_struct)
            if target_composite is not None:
                # Use composite target path
                return self._evaluate_compound_conversion(
                    value_struct, target_composite, eo
                )
            target_unit_name = target_struct.print()

        if not target_unit_name:
            return MS.undefined()

        # Handle timezone conversion for datetime expressions
        # e.g., "now to utc" or "today to utc"
        target_lower = target_unit_name.lower()
        if target_lower in ("utc", "gmt", "local"):
            # Evaluate the value expression first
            value_result = value_struct.evaluate(eo)
            if value_result.is_symbolic():
                # Try to parse as datetime
                import datetime as _dt
                try:
                    dt_str = value_result.symbol
                    if "T" in dt_str or len(dt_str) > 10:
                        dt = _dt.datetime.fromisoformat(dt_str)
                    else:
                        dt = _dt.datetime.fromisoformat(dt_str)
                    if target_lower in ("utc", "gmt"):
                        # Convert to UTC (assume local if naive)
                        if dt.tzinfo is None:
                            import time
                            # Get UTC offset
                            utc_offset = _dt.datetime.now().astimezone().utcoffset()
                            if utc_offset:
                                dt = dt - utc_offset
                        result_str = dt.strftime("%Y-%m-%dT%H:%M:%S")
                    else:
                        result_str = dt.strftime("%Y-%m-%dT%H:%M:%S")
                    return MS.from_symbol(result_str)
                except (ValueError, TypeError):
                    pass
            return MS.undefined()

        # Resolve target unit (with optional prefix)
        target_unit, target_prefix, target_prefix_factor = self._resolve_unit_with_prefix(target_unit_name)
        if target_unit is None:
            return MS.undefined()

        # Extract value and source unit from the value expression
        # Handle: 5 * ft, just ft, or compound like 100 m/s
        num_value = 1.0
        from_unit = None
        interval_number = None  # Track interval Number for uncertainty propagation

        # First, try to evaluate the value expression to simplify it
        # This handles cases like (2.5±0.3 m) / (1.2±0.1 s) which needs
        # to be simplified before extracting number and unit
        evaluated_value = value_struct.evaluate(eo)

        # Helper to recursively find interval numbers in a structure
        def _find_interval_number(ms):
            if ms.is_number() and ms.number is not None and ms.number.is_interval():
                return ms.number
            for child in ms:
                found = _find_interval_number(child)
                if found is not None:
                    return found
            return None

        # Helper to compute the combined numeric value as a Number (preserving intervals)
        def _compute_numeric_value(ms):
            """Multiply all numeric parts together, preserving interval info."""
            from pyqalculate.number import Number as NumType
            from pyqalculate.types import StructureType as ST
            result = NumType(1)
            if ms.is_number() and ms.number is not None:
                return ms.number
            if ms.is_multiplication():
                for child in ms:
                    if child.is_number() and child.number is not None:
                        result = result * child.number
                    elif child.type == ST.INVERSE and len(child) == 1:
                        inner = child[0]
                        if inner.is_number() and inner.number is not None:
                            result = result / inner.number
                        elif inner.is_multiplication():
                            # Extract number from inverse of multiplication
                            for subchild in inner:
                                if subchild.is_number() and subchild.number is not None:
                                    result = result / subchild.number
            return result

        if evaluated_value.is_multiplication():
            # Try to extract unit parts (but use Number arithmetic for numeric value)
            num_value, from_unit = self._extract_value_and_unit(evaluated_value)
            # Compute interval-aware numeric value
            interval_number = _find_interval_number(evaluated_value)
            if interval_number is not None:
                # Recompute num_value using interval-aware arithmetic
                computed_num = _compute_numeric_value(evaluated_value)
                if computed_num is not None and computed_num.is_interval():
                    interval_number = computed_num
                    # Update num_value to midpoint for the conversion factor calculation
                    num_value = computed_num.midpoint_value()

        elif evaluated_value.is_unit():
            from_unit = evaluated_value.unit

        elif evaluated_value.is_number():
            num_value = evaluated_value.float_value()
            if evaluated_value.number is not None and evaluated_value.number.is_interval():
                interval_number = evaluated_value.number

        # Fallback to original value if evaluation didn't help
        if from_unit is None and value_struct.is_multiplication():
            num_value, from_unit = self._extract_value_and_unit(value_struct)
            interval_number = _find_interval_number(value_struct)

        elif from_unit is None and value_struct.is_unit():
            from_unit = value_struct.unit

        elif from_unit is None and value_struct.is_number():
            num_value = value_struct.float_value()
            if value_struct.number is not None and value_struct.number.is_interval():
                interval_number = value_struct.number

        if from_unit is None:
            # Fallback: when the value is numeric (no unit) and the target unit
            # is an alias with a DIFFERENT base unit, try interpreting the value
            # as being in the root base unit. Walk the base_unit chain to find
            # the ultimate non-alias unit (e.g., ft→hand→in→m gives "m").
            if evaluated_value.is_number():
                num_value = evaluated_value.float_value()
                if hasattr(target_unit, 'base_unit'):
                    base = target_unit.base_unit()
                    # Walk the chain to the root base unit
                    visited_ids: set[int] = set()
                    while (base is not None
                           and base is not target_unit
                           and id(base) not in visited_ids
                           and hasattr(base, 'base_unit')):
                        visited_ids.add(id(base))
                        next_base = base.base_unit()
                        if next_base is None or next_base is base:
                            break
                        base = next_base
                    if base is not None and base is not target_unit:
                        from_unit = base
            if from_unit is None:
                return MS.undefined()

        # Convert between units
        converted = self.convert(num_value, from_unit, target_unit)
        if converted is None:
            # Conversion failed — try temperature aliases as fallback.
            # "C" resolves to Coulomb, "F" to Farad; temperature units are "oC"/"oF".
            converted = self._try_temperature_fallback(
                num_value, from_unit, target_unit,
            )
        if converted is None:
            # Fallback: if the value has units that don't directly convert to target,
            # try stripping all units and treating the numeric value as the target's
            # base unit. Only for alias units where base != target (e.g., eV→J).
            raw_num = self._compute_pure_numeric(evaluated_value)
            if raw_num is not None and raw_num != 0 and hasattr(target_unit, 'base_unit'):
                base = target_unit.base_unit()
                if base is not None and base is not target_unit:
                    converted = self.convert(raw_num, base, target_unit)
                    if converted is not None:
                        from_unit = base
                        num_value = raw_num
        if converted is not None:
            # Apply prefix factors
            if target_prefix_factor != 1.0:
                converted /= target_prefix_factor

            # If we have an interval number, propagate uncertainty through conversion
            if interval_number is not None:
                from pyqalculate.number import Number as NumType
                # The conversion factor is converted/num_value
                if num_value != 0:
                    conv_factor = converted / num_value
                    # Multiply interval by conversion factor (factor has no uncertainty)
                    factor_num = NumType(conv_factor)
                    result_num_obj = interval_number * factor_num
                    # Preserve plusminus flag
                    if interval_number.is_plusminus():
                        result_num_obj.set_plusminus(True)
                    result_num = MS.from_number(result_num_obj)
                else:
                    result_num = MS(converted)
                result_unit = MS.from_unit(target_unit, target_prefix)
                return MS.multiplication(result_num, result_unit)

            # Check for mixed unit output (e.g., 5 ft + 8.5 in)
            if (target_prefix is None and
                    isinstance(target_unit, AliasUnit) and
                    target_unit.mix_with_base() > 0 and
                    not float(converted).is_integer()):
                mixed = self._format_mixed_units(converted, target_unit)
                if mixed is not None:
                    return mixed

            # Format the result nicely
            result_num = MS(converted)
            result_unit = MS.from_unit(target_unit, target_prefix)
            return MS.multiplication(result_num, result_unit)

        return MS.undefined()

    # -- Temperature disambiguation --

    # Map of ambiguous single-letter unit names to their temperature aliases.
    # "C" → Coulomb, "F" → Farad in normal lookup; but "C to F" is temperature.
    _TEMP_ALIASES: dict[str, list[str]] = {
        "C": ["oC", "celsius"],
        "F": ["oF", "fahrenheit"],
        "K": ["K", "kelvin"],
        "R": ["oR", "rankine"],
    }

    def _try_temperature_fallback(
        self,
        value: float,
        from_unit: "Unit",
        to_unit: "Unit",
    ) -> float | None:
        """Retry conversion using temperature unit aliases.

        When 'C' resolves to Coulomb and 'F' to Farad, the conversion fails.
        This method checks if either unit name has a known temperature alias
        and retries with those.
        """
        from pyqalculate.unit import AliasUnit, UnitSubtype

        from_names = [n.name for n in from_unit._names]
        to_names = [n.name for n in to_unit._names]

        # Check if either unit name is in our temperature alias map
        from_aliases: list[str] = []
        to_aliases: list[str] = []
        for name in from_names:
            if name in self._TEMP_ALIASES:
                from_aliases = self._TEMP_ALIASES[name]
                break
        for name in to_names:
            if name in self._TEMP_ALIASES:
                to_aliases = self._TEMP_ALIASES[name]
                break

        if not from_aliases and not to_aliases:
            return None

        # Try each combination of temperature aliases
        for fa in (from_aliases or [""]):
            for ta in (to_aliases or [""]):
                fu = self.get_unit(fa) if fa else from_unit
                tu = self.get_unit(ta) if ta else to_unit
                if fu is None or tu is None:
                    continue
                # Only try if at least one has a nonlinear relation (temperature)
                if (fu.has_nonlinear_relation_to_base() or
                        tu.has_nonlinear_relation_to_base()):
                    result = self.convert(value, fu, tu)
                    if result is not None:
                        return result
        return None

    def _format_mixed_units(
        self,
        value: float,
        unit: "Unit",
    ) -> "MathStructure | None":
        """Format a value as mixed units (e.g., 5 ft + 8.5 in).

        When a unit has mix_with_base > 0, the integer part is shown in
        that unit and the fractional part is converted to the deepest
        sub-unit in the chain (e.g., ft → in, skipping hand).
        Chain depth is limited to prevent absurd conversions
        (e.g., miles → inches).
        """
        from pyqalculate.math_structure import MathStructure as MS
        from pyqalculate.unit import AliasUnit, UnitSubtype

        if not isinstance(unit, AliasUnit):
            return None

        # Split into integer (primary) + fractional
        int_part = int(value)
        frac = value - int_part

        # Don't trigger mixed display when integer part is zero
        if int_part == 0:
            return None

        if abs(frac) < 1e-12:
            return None  # No fractional part, no need for mixed display

        # Check mix_with_base_minimum: only show mixed if value >= minimum
        min_val = unit.mix_with_base_minimum()
        if min_val > 0 and abs(value) < min_val:
            return None

        # Walk the chain to find the final sub-unit and total conversion factor
        # Limit chain depth to 3 units to prevent absurd conversions
        # (e.g., mi→yd→ft→hand→in giving 63360 in/mi)
        MAX_CHAIN_DEPTH = 3
        chain_units: list[AliasUnit] = []
        current: AliasUnit = unit
        visited: set[int] = set()

        while (current is not None and
               isinstance(current, AliasUnit) and
               id(current) not in visited and
               len(chain_units) < MAX_CHAIN_DEPTH):
            visited.add(id(current))
            chain_units.append(current)
            bu = current.base_unit()
            if bu is None or not isinstance(bu, AliasUnit):
                break
            # Stop if the next unit has mix_with_base == 0 (leaf unit)
            if bu.mix_with_base() == 0:
                chain_units.append(bu)
                break
            current = bu

        if len(chain_units) < 2:
            return None

        # The primary unit and the final sub-unit
        primary = chain_units[0]   # e.g., ft
        leaf = chain_units[-1]     # e.g., in

        # Compute conversion factor from primary to leaf
        factor_to_leaf = 1.0
        for i in range(len(chain_units) - 1):
            cu = chain_units[i]
            from pyqalculate.unit import _eval_numeric_expression
            try:
                rel = _eval_numeric_expression(cu.expression())
                factor_to_leaf *= rel
            except (ValueError, ZeroDivisionError):
                return None

        leaf_value = frac * factor_to_leaf

        # Build: N primary + M leaf
        # Use integer for the primary part to avoid "5.0 ft" display
        primary_m = MS.multiplication(MS(int_part), MS.from_unit(primary))
        leaf_m = MS.multiplication(MS(leaf_value), MS.from_unit(leaf))
        return primary_m + leaf_m

    # -- Compound unit helpers --

    def _extract_value_and_unit(
        self,
        mstruct: "MathStructure",
    ) -> tuple[float, "Unit | None"]:
        """Extract numeric value and unit from a multiplication MathStructure.

        Handles:
        - number * unit  (simple: 5 ft)
        - number * unit * unit^-1 * ...  (compound: 100 m/s)
        - unit * unit^-1 * ...  (no number: m/s → 1 m/s)
        - nested multiplications: (100*m) * (1/s)

        Returns (numeric_value, unit_or_composite).
        """
        from pyqalculate.math_structure import MathStructure as MS
        from pyqalculate.types import StructureType as ST
        from pyqalculate.unit import CompositeUnit, Unit, UnitSubtype

        if not mstruct.is_multiplication():
            if mstruct.is_number():
                return mstruct.float_value(), None
            if mstruct.is_unit():
                return 1.0, mstruct.unit
            return 1.0, None

        num_value = 1.0
        unit_parts: list[tuple[Unit, int]] = []

        for child in mstruct:
            if child.is_number():
                num_value *= child.float_value()
            elif child.is_unit() and child.unit is not None:
                unit_parts.append((child.unit, 1))
            elif child.is_symbolic():
                # Try to resolve as unit (with prefix handling)
                u, pfx, pfx_factor = self._resolve_unit_with_prefix(child.symbol)
                if u is not None:
                    if pfx_factor != 1.0:
                        num_value *= pfx_factor
                    unit_parts.append((u, 1))
            elif child.type == ST.INVERSE and len(child) == 1:
                inner = child[0]
                if inner.is_unit() and inner.unit is not None:
                    unit_parts.append((inner.unit, -1))
                elif inner.is_symbolic():
                    u, pfx, pfx_factor = self._resolve_unit_with_prefix(inner.symbol)
                    if u is not None:
                        if pfx_factor != 1.0:
                            num_value /= pfx_factor
                        unit_parts.append((u, -1))
                elif inner.is_multiplication():
                    # Recursively extract from inverse of multiplication
                    sub_num, sub_unit = self._extract_value_and_unit(inner)
                    if sub_unit is not None:
                        unit_parts.append((sub_unit, -1))
                    if sub_num != 1.0:
                        num_value /= sub_num
            elif (child.type == ST.POWER and len(child) == 2
                  and child[0].is_unit() and child[0].unit is not None
                  and child[1].is_number()):
                # POWER(UNIT, number) — e.g., POWER(s, -1) from interval eval
                exp_val = child[1].float_value()
                unit_parts.append((child[0].unit, int(round(exp_val))))
            elif child.is_multiplication():
                # Nested multiplication (e.g., 100*m inside 100*m/s)
                sub_num, sub_unit = self._extract_value_and_unit(child)
                num_value *= sub_num
                if sub_unit is not None:
                    if sub_unit.subtype() == UnitSubtype.COMPOSITE_UNIT:
                        # Flatten composite sub-units
                        assert isinstance(sub_unit, CompositeUnit)
                        for i in range(1, sub_unit.count_units() + 1):
                            su = sub_unit.get(i)
                            if su is not None:
                                bu = su.base_unit()
                                if bu is not None:
                                    unit_parts.append((bu, su.exponent()))
                    else:
                        unit_parts.append((sub_unit, 1))

        if not unit_parts:
            return num_value, None

        if len(unit_parts) == 1 and unit_parts[0][1] == 1:
            return num_value, unit_parts[0][0]

        # Build a CompositeUnit
        composite = CompositeUnit("", "", "", is_local=True, is_builtin=False)
        for u, exp in unit_parts:
            composite.add(u, exp)
        return num_value, composite

    def _compute_pure_numeric(
        self,
        mstruct: "MathStructure",
    ) -> float | None:
        """Compute the pure numeric value of an expression, accounting for unit prefix factors.

        Recursively walks the expression tree, multiplying all numbers and
        unit prefix factors (e.g., nm → 1e-9), while ignoring the units themselves.
        Returns None if the expression contains non-numeric, non-unit elements.
        """
        from pyqalculate.types import StructureType as ST

        if mstruct.is_number():
            return mstruct.float_value()

        if mstruct.is_unit() and mstruct.unit is not None:
            # Unit: extract the conversion factor to base unit
            u = mstruct.unit
            # Check for prefix on the MathStructure node
            if hasattr(mstruct, '_prefix') and mstruct._prefix is not None:
                pfx = mstruct._prefix
                if hasattr(pfx, 'exponent'):
                    return 10 ** pfx.exponent()
            # Check for alias unit relation (e.g., nm has _relation = 1e-9)
            if hasattr(u, '_relation'):
                try:
                    return float(u._relation)
                except (ValueError, TypeError):
                    pass
            return 1.0

        if mstruct.is_symbolic():
            # Try to resolve as a unit with prefix
            u, pfx, pfx_factor = self._resolve_unit_with_prefix(mstruct.symbol)
            if u is not None:
                return pfx_factor
            return None

        if mstruct.type == ST.INVERSE and len(mstruct) == 1:
            inner_val = self._compute_pure_numeric(mstruct[0])
            if inner_val is not None and inner_val != 0:
                return 1.0 / inner_val
            return None

        if mstruct.is_multiplication():
            result = 1.0
            for child in mstruct:
                child_val = self._compute_pure_numeric(child)
                if child_val is None:
                    return None
                result *= child_val
            return result

        if mstruct.type == ST.POWER and len(mstruct) == 2:
            base_val = self._compute_pure_numeric(mstruct[0])
            exp_val = self._compute_pure_numeric(mstruct[1])
            if base_val is not None and exp_val is not None:
                return base_val ** exp_val
            return None

        return None

    def _build_composite_from_struct(
        self,
        mstruct: "MathStructure",
    ) -> "Unit | None":
        """Build a unit (simple or composite) from a MathStructure.

        Returns a Unit object, or None if the structure doesn't represent a unit.
        Handles prefixed units (e.g., km → m with k prefix).
        """
        from pyqalculate.math_structure import MathStructure as MS
        from pyqalculate.types import StructureType as ST
        from pyqalculate.unit import CompositeUnit, Unit, UnitSubtype

        if mstruct.is_unit() and mstruct.unit is not None:
            return mstruct.unit

        if mstruct.is_symbolic():
            unit, prefix, _factor = self._resolve_unit_with_prefix(mstruct.symbol)
            if unit is not None and prefix is not None:
                # Build a composite with prefix
                composite = CompositeUnit("", "", "", is_local=True, is_builtin=False)
                composite.add(unit, 1, prefix)
                return composite
            return unit

        if not mstruct.is_multiplication():
            return None

        unit_parts: list[tuple[Unit, int, object | None]] = []
        for child in mstruct:
            if child.is_unit() and child.unit is not None:
                unit_parts.append((child.unit, 1, None))
            elif child.is_symbolic():
                u, pfx, _f = self._resolve_unit_with_prefix(child.symbol)
                if u is not None:
                    unit_parts.append((u, 1, pfx))
            elif child.type == ST.INVERSE and len(child) == 1:
                inner = child[0]
                if inner.is_unit() and inner.unit is not None:
                    unit_parts.append((inner.unit, -1, None))
                elif inner.is_symbolic():
                    u, pfx, _f = self._resolve_unit_with_prefix(inner.symbol)
                    if u is not None:
                        unit_parts.append((u, -1, pfx))

        if not unit_parts:
            return None
        if len(unit_parts) == 1 and unit_parts[0][1] == 1 and unit_parts[0][2] is None:
            return unit_parts[0][0]

        composite = CompositeUnit("", "", "", is_local=True, is_builtin=False)
        for u, exp, pfx in unit_parts:
            composite.add(u, exp, pfx)  # type: ignore[arg-type]
        return composite

    def _evaluate_compound_conversion(
        self,
        value_struct: "MathStructure",
        target_unit: "Unit",
        eo: "EvaluationOptions",
    ) -> "MathStructure":
        """Evaluate a compound unit conversion (e.g., 100 m/s to km/h).

        Args:
            value_struct: The value expression (may contain compound units).
            target_unit: The resolved target unit (may be composite).
            eo: Evaluation options.

        Returns:
            A MathStructure with the converted value and target unit.
        """
        from pyqalculate.math_structure import MathStructure as MS
        from pyqalculate.types import StructureType as ST
        from pyqalculate.number import Number as NumType

        # Evaluate the value expression first
        evaluated_value = value_struct.evaluate(eo)

        # Extract numeric value and source unit
        num_value, from_unit = self._extract_value_and_unit(evaluated_value)

        if from_unit is None:
            return MS.undefined()

        # Find interval numbers for uncertainty propagation
        interval_number = None
        def _find_interval(ms):
            if ms.is_number() and ms.number is not None and ms.number.is_interval():
                return ms.number
            for child in ms:
                found = _find_interval(child)
                if found is not None:
                    return found
            return None

        # Compute interval-aware numeric value
        def _compute_numeric(ms):
            result = NumType(1)
            if ms.is_number() and ms.number is not None:
                return ms.number
            if ms.is_multiplication():
                for child in ms:
                    if child.is_number() and child.number is not None:
                        result = result * child.number
                    elif child._type == ST.INVERSE and len(child) == 1:
                        inner = child[0]
                        if inner.is_multiplication():
                            for subchild in inner:
                                if subchild.is_number() and subchild.number is not None:
                                    result = result / subchild.sub_number if hasattr(subchild, 'sub_number') else result / subchild.number
            return result

        interval_number = _find_interval(evaluated_value)
        if interval_number is not None:
            computed = _compute_numeric(evaluated_value)
            if computed.is_interval():
                interval_number = computed
                num_value = computed.midpoint_value()

        # Convert between units
        converted = self.convert(num_value, from_unit, target_unit)
        if converted is not None:
            # Apply prefix factors
            # (compound conversion doesn't have prefix handling, skip)

            # If we have an interval, propagate through conversion
            if interval_number is not None and num_value != 0:
                conv_factor = converted / num_value
                factor_num = NumType(conv_factor)
                result_num_obj = interval_number * factor_num
                if interval_number.is_plusminus():
                    result_num_obj.set_plusminus(True)
                result_num = MS.from_number(result_num_obj)
            else:
                result_num = MS(converted)
            result_unit = MS.from_unit(target_unit)
            return MS.multiplication(result_num, result_unit)

        return MS.undefined()

    # -- Date/Time conversion handlers --

    def _handle_to_time(
        self, value_struct: "MathStructure", eo: "EvaluationOptions",
    ) -> "MathStructure":
        """Handle 'to time': evaluate expression and format as HH:MM."""
        from pyqalculate.math_structure import MathStructure as MS
        value_result = value_struct.evaluate(eo)
        if value_result.is_number() and value_result.number is not None:
            total_minutes = int(round(value_result.number.to_float()))
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return MS.from_symbol(f"{hours:02d}:{minutes:02d}")
        # If result involves time units, try to convert to minutes
        if value_result.is_multiplication() or value_result.is_addition():
            total_seconds = self._extract_time_seconds(value_result)
            if total_seconds is not None:
                total_minutes = int(round(total_seconds / 60))
                hours = total_minutes // 60
                minutes = total_minutes % 60
                return MS.from_symbol(f"{hours:02d}:{minutes:02d}")
        return MS.undefined()

    def _extract_time_seconds(self, mstruct: "MathStructure") -> float | None:
        """Extract total seconds from a time-unit expression.

        Handles expressions like 10*h + 31*min, h*10 + min*31, etc.
        """
        from pyqalculate.math_structure import MathStructure as MS
        from pyqalculate.types import StructureType as ST

        _TIME_FACTORS = {
            "s": 1, "sec": 1, "second": 1, "seconds": 1,
            "min": 60, "minute": 60, "minutes": 60,
            "h": 3600, "hr": 3600, "hour": 3600, "hours": 3600,
        }

        def _get_time_factor(unit_name: str) -> float | None:
            return _TIME_FACTORS.get(unit_name.lower())

        def _extract_single_term(term: "MathStructure") -> float | None:
            """Extract seconds from a single term like 10*h or 31*min."""
            if term.is_unit() and term.unit is not None:
                factor = _get_time_factor(term.unit.name())
                if factor is not None:
                    return factor
                # Check unit names
                for n in term.unit._names:
                    factor = _get_time_factor(n.name)
                    if factor is not None:
                        return factor
            if term.is_multiplication():
                num_val = 1.0
                unit_factor = None
                for child in term:
                    if child.is_number() and child.number is not None:
                        num_val *= child.number.to_float()
                    elif child.is_unit() and child.unit is not None:
                        f = _get_time_factor(child.unit.name())
                        if f is None:
                            for n in child.unit._names:
                                f = _get_time_factor(n.name)
                                if f is not None:
                                    break
                        if f is not None:
                            unit_factor = f
                    elif child.is_symbolic():
                        f = _get_time_factor(child.symbol)
                        if f is not None:
                            unit_factor = f
                if unit_factor is not None:
                    return num_val * unit_factor
            return None

        if mstruct.is_addition():
            total = 0.0
            for child in mstruct:
                term_seconds = _extract_single_term(child)
                if term_seconds is None:
                    return None
                total += term_seconds
            return total
        return _extract_single_term(mstruct)

    def _handle_to_timezone(
        self, value_struct: "MathStructure", tz_name: str, eo: "EvaluationOptions",
    ) -> "MathStructure":
        """Handle 'to utc' or 'to utc+N': format datetime with timezone."""
        import datetime as _dt
        from pyqalculate.math_structure import MathStructure as MS

        value_result = value_struct.evaluate(eo)
        if not value_result.is_symbolic():
            return MS.undefined()

        dt_str = value_result.symbol
        try:
            # Parse the datetime string
            dt = _dt.datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return MS.undefined()

        # Parse timezone offset
        tz_lower = tz_name.lower()
        if tz_lower in ("utc", "gmt"):
            offset_hours = 0
        elif len(tz_lower) > 3 and tz_lower[3] in "+-":
            try:
                offset_hours = int(tz_lower[4:])
                if tz_lower[3] == "-":
                    offset_hours = -offset_hours
            except ValueError:
                return MS.undefined()
        else:
            return MS.undefined()

        # Convert: if datetime is naive (local), adjust to target timezone
        if dt.tzinfo is None:
            # Get local UTC offset
            local_offset = _dt.datetime.now().astimezone().utcoffset()
            if local_offset is not None:
                # Convert local naive → UTC, then apply target offset
                dt_utc = dt - local_offset
                tz_delta = _dt.timedelta(hours=offset_hours)
                dt_result = dt_utc + tz_delta
            else:
                dt_result = dt
        else:
            tz_delta = _dt.timedelta(hours=offset_hours)
            dt_result = dt.astimezone(_dt.timezone(tz_delta))

        # Format as ISO 8601
        if offset_hours == 0:
            result_str = dt_result.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            sign = "+" if offset_hours >= 0 else "-"
            abs_off = abs(offset_hours)
            result_str = dt_result.strftime("%Y-%m-%dT%H:%M:%S")
            result_str += f"{sign}{abs_off:02d}:00"

        return MS.from_symbol(result_str)

    def _handle_to_calendars(
        self, value_struct: "MathStructure", eo: "EvaluationOptions",
    ) -> "MathStructure":
        """Handle 'to calendars': show date in multiple calendar systems."""
        import datetime as _dt
        from pyqalculate.math_structure import MathStructure as MS

        value_result = value_struct.evaluate(eo)
        if not value_result.is_symbolic():
            return MS.undefined()

        dt_str = value_result.symbol
        try:
            d = _dt.date.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return MS.undefined()

        results = []
        # Gregorian (original)
        results.append(MS.from_symbol(f"Gregorian: {d.isoformat()}"))

        # ISO week date
        iso_year, iso_week, iso_day = d.isocalendar()
        results.append(MS.from_symbol(f"ISO: {iso_year}-W{iso_week:02d}-{iso_day}"))

        # Julian day number
        epoch = _dt.date(2000, 1, 1)
        julian_day = 2451545 + (d - epoch).days
        results.append(MS.from_symbol(f"Julian Day: {julian_day}"))

        # Day of year
        day_of_year = d.timetuple().tm_yday
        results.append(MS.from_symbol(f"Day of Year: {day_of_year}"))

        # Julian calendar approximation
        # (simplified: Julian calendar is Gregorian minus ~13 days in 21st century)
        julian_offset = 13  # days offset for 2000-2099
        julian_date = d - _dt.timedelta(days=julian_offset)
        results.append(MS.from_symbol(f"Julian: {julian_date.isoformat()}"))

        return MS.vector(*results)

    def _try_date_arithmetic(
        self, mstruct: "MathStructure", eo: "EvaluationOptions",
    ) -> "MathStructure | None":
        """Try to evaluate date arithmetic like '2024-06-15 + 100 days'.

        Returns a MathStructure if the expression is date arithmetic,
        or None if it's not date-related.
        """
        import datetime as _dt
        from pyqalculate.math_structure import MathStructure as MS
        from pyqalculate.types import StructureType as ST

        _DAY_FACTORS = {
            "day": 1, "days": 1,
            "week": 7, "weeks": 7,
        }

        if not mstruct.is_addition() or len(mstruct) < 2:
            return None

        # Look for a date symbol and a days term
        date_str: str | None = None
        total_days = 0
        has_date = False
        has_days = False

        for child in mstruct:
            # Check if child is a date symbol
            if child.is_symbolic():
                try:
                    _dt.date.fromisoformat(child.symbol)
                    date_str = child.symbol
                    has_date = True
                    continue
                except (ValueError, TypeError):
                    pass

            # Check if child is N * days
            days_val = self._extract_days_value(child)
            if days_val is not None:
                total_days += days_val
                has_days = True
                continue

            # Not a date or days term
            return None

        if not has_date or not has_days or date_str is None:
            return None

        try:
            d = _dt.date.fromisoformat(date_str)
            result_date = d + _dt.timedelta(days=total_days)
            return MS.from_symbol(result_date.isoformat())
        except (ValueError, TypeError):
            return None

    def _extract_days_value(self, mstruct: "MathStructure") -> float | None:
        """Extract a number of days from a term like 100*days or 2*weeks."""
        _DAY_NAMES = {"day", "days", "week", "weeks"}
        _DAY_FACTORS = {
            "day": 1, "days": 1,
            "week": 7, "weeks": 7,
        }

        def _get_day_factor(name: str) -> float | None:
            return _DAY_FACTORS.get(name.lower())

        def _is_day_unit(unit_obj) -> bool:
            """Check if a unit represents days (including by alias names)."""
            if unit_obj is None:
                return False
            if unit_obj.name().lower() in _DAY_NAMES:
                return True
            for n in unit_obj._names:
                if n.name.lower() in _DAY_NAMES:
                    return True
            return False

        if mstruct.is_unit():
            if _is_day_unit(mstruct.unit):
                return 1.0
            return None

        if mstruct.is_multiplication():
            num_val = 1.0
            unit_factor = None
            for child in mstruct:
                if child.is_number() and child.number is not None:
                    num_val *= child.number.to_float()
                elif child.is_unit():
                    if _is_day_unit(child.unit):
                        unit_factor = 1.0
                elif child.is_symbolic():
                    f = _get_day_factor(child.symbol)
                    if f is not None:
                        unit_factor = f
            if unit_factor is not None:
                return num_val * unit_factor

        return None

    # -- CSV Import/Export --

    def importCSV(
        self,
        filename: str,
        first_row: int = 1,
        headers: bool = True,
        delimiter: str = ",",
        to_matrix: bool = False,
        name: str = "",
    ) -> "MathStructure":
        """Import a CSV file as a matrix or vector of variables.

        Mirrors libqalculate's Calculator::importCSV().

        Args:
            filename: Path to the CSV file.
            first_row: First data row (1-indexed; rows before this are skipped).
            headers: If True, treat the first data row as column headers.
            delimiter: Column separator character.
            to_matrix: If True, return as a single matrix variable.
                       If False, create separate vector variables per column.
            name: Variable name prefix. Auto-derived from filename if empty.

        Returns:
            The imported MathStructure (matrix or vector).
        """
        import csv
        from pyqalculate.math_structure import MathStructure as MS
        from pyqalculate.number import Number
        from pyqalculate.variable import KnownVariable

        if not filename:
            return MS.undefined()

        try:
            with open(filename, newline="", encoding="utf-8-sig") as f:
                reader = csv.reader(f, delimiter=delimiter)
                all_rows = list(reader)
        except (OSError, csv.Error):
            return MS.undefined()

        if not all_rows:
            return MS.undefined()

        # Derive name from filename if not provided
        if not name:
            from pathlib import Path as _Path
            name = _Path(filename).stem

        # Determine data start and headers
        data_start = max(0, first_row - 1)  # Convert to 0-indexed
        col_headers: list[str] = []
        if headers and data_start < len(all_rows):
            col_headers = [c.strip() for c in all_rows[data_start]]
            data_start += 1

        data_rows = all_rows[data_start:]
        if not data_rows:
            return MS.undefined()

        def _parse_cell(cell: str) -> MathStructure:
            """Try to parse a cell as a number; fall back to symbolic."""
            cell = cell.strip()
            if not cell:
                return MS(0)
            try:
                return MS(float(cell))
            except ValueError:
                return MS.from_symbol(cell)

        if to_matrix:
            # Create a single matrix variable
            matrix_rows = []
            for row in data_rows:
                matrix_rows.append(MS.vector(*[_parse_cell(c) for c in row]))
            mstruct = MS.matrix(matrix_rows)

            if name:
                var = KnownVariable("CSV Data", name, mstruct, title=f"Imported from {filename}")
                self.add_variable(var)
            return mstruct
        else:
            # Create separate vector variables per column
            n_cols = max(len(r) for r in data_rows) if data_rows else 0
            col_vectors: list[MathStructure] = []
            for col_idx in range(n_cols):
                elements = []
                for row in data_rows:
                    elements.append(_parse_cell(row[col_idx]) if col_idx < len(row) else MS(0))
                col_vectors.append(MS.vector(*elements))

            # Register each column as a variable
            for i, vec in enumerate(col_vectors):
                col_name = col_headers[i] if i < len(col_headers) else f"col{i+1}"
                var_name = f"{name}_{col_name}" if name else col_name
                var = KnownVariable("CSV Data", var_name, vec,
                                    title=f"Column {col_name} from {filename}")
                self.add_variable(var)

            # Return the full matrix
            return MS.matrix(col_vectors)

    def importXLSX(
        self,
        filename: str,
        sheet: int | str = 0,
        headers: bool = True,
        first_row: int = 1,
        to_matrix: bool = False,
        name: str = "",
    ) -> "MathStructure":
        """Import an Excel .xlsx file as a matrix or vector of variables.

        Mirrors importCSV but uses openpyxl for .xlsx files.
        Requires: pip install pyqalculate[xlsx]

        Args:
            filename: Path to the .xlsx file.
            sheet: Worksheet index (int) or name (str). Default: first sheet (0).
            headers: If True, treat the first data row as column headers.
            first_row: First data row (1-indexed; rows before this are skipped).
            to_matrix: If True, return as a single matrix variable.
                       If False, create separate vector variables per column.
            name: Variable name prefix. Auto-derived from filename if empty.
        """
        try:
            import openpyxl
        except ImportError:
            from pyqalculate.math_structure import MathStructure as _MS
            return _MS.undefined()

        from pyqalculate.math_structure import MathStructure as MS
        from pyqalculate.number import Number
        from pyqalculate.variable import KnownVariable

        def _cell_to_str(value) -> str:
            """Convert openpyxl cell value to string for _parse_cell."""
            if value is None:
                return ""
            if isinstance(value, bool):
                return str(int(value))  # "1"/"0", not "True"/"False"
            return str(value)

        try:
            wb = openpyxl.load_workbook(filename, data_only=True)
            ws = wb[sheet] if isinstance(sheet, str) else wb.worksheets[sheet]
            all_rows = [
                [_cell_to_str(cell.value) for cell in row]
                for row in ws.iter_rows(min_row=first_row)
            ]
        except (OSError, IndexError, KeyError):
            return MS.undefined()

        if not all_rows:
            return MS.undefined()

        # Derive name from filename if not provided
        if not name:
            from pathlib import Path as _Path
            name = _Path(filename).stem

        # Simplified header/data slicing (first_row already consumed by iter_rows)
        data_rows = list(all_rows)
        col_headers: list[str] = []
        if headers and data_rows:
            col_headers = [c.strip() for c in data_rows[0]]
            data_rows = data_rows[1:]
        if not data_rows:
            return MS.undefined()

        def _parse_cell(cell: str) -> "MathStructure":
            """Try to parse a cell as a number; fall back to symbolic."""
            cell = cell.strip()
            if not cell:
                return MS(0)
            try:
                return MS(float(cell))
            except ValueError:
                return MS.from_symbol(cell)

        if to_matrix:
            matrix_rows = []
            for row in data_rows:
                matrix_rows.append(MS.vector(*[_parse_cell(c) for c in row]))
            mstruct = MS.matrix(matrix_rows)
            if name:
                var = KnownVariable("XLSX Data", name, mstruct, title=f"Imported from {filename}")
                self.add_variable(var)
            return mstruct
        else:
            n_cols = max(len(r) for r in data_rows) if data_rows else 0
            col_vectors = []
            for col_idx in range(n_cols):
                elements = []
                for row in data_rows:
                    elements.append(_parse_cell(row[col_idx]) if col_idx < len(row) else MS(0))
                col_vectors.append(MS.vector(*elements))
            for i, vec in enumerate(col_vectors):
                col_name = col_headers[i] if i < len(col_headers) else f"col{i+1}"
                var_name = f"{name}_{col_name}" if name else col_name
                var = KnownVariable("XLSX Data", var_name, vec,
                                    title=f"Column {col_name} from {filename}")
                self.add_variable(var)
            return MS.matrix(col_vectors)

    def exportCSV(
        self,
        mstruct: "MathStructure",
        filename: str,
        delimiter: str = ",",
    ) -> bool:
        """Export a MathStructure (matrix/vector) to a CSV file.

        Mirrors libqalculate's Calculator::exportCSV().

        Args:
            mstruct: The MathStructure to export (matrix, vector, or number).
            filename: Output CSV file path.
            delimiter: Column separator character.

        Returns:
            True on success, False on failure.
        """
        import csv

        try:
            rows: list[list[str]] = []

            if mstruct.is_matrix():
                for row in mstruct:
                    if row.is_vector():
                        rows.append([str(c) for c in row])
                    else:
                        rows.append([str(row)])
            elif mstruct.is_vector():
                # Export vector as a single column
                for elem in mstruct:
                    rows.append([str(elem)])
            else:
                # Single value
                rows.append([str(mstruct)])

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerows(rows)
            return True
        except (OSError, csv.Error):
            return False

    def exportXLSX(
        self,
        mstruct: "MathStructure",
        filename: str,
        sheet_name: str = "Sheet1",
    ) -> bool:
        """Export a MathStructure (matrix/vector) to an Excel .xlsx file.

        Mirrors exportCSV but uses openpyxl for .xlsx files.
        Requires: pip install pyqalculate[xlsx]

        Args:
            mstruct: The MathStructure to export (matrix, vector, or number).
            filename: Output .xlsx file path.
            sheet_name: Name of the worksheet. Default: "Sheet1".

        Returns:
            True on success, False on failure.
        """
        try:
            import openpyxl
        except ImportError:
            return False

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = sheet_name

            def _cell_value(val: "MathStructure") -> int | float | str:
                """Convert a MathStructure to an openpyxl-compatible cell value."""
                s = str(val)
                try:
                    return int(s)
                except ValueError:
                    pass
                try:
                    return float(s)
                except ValueError:
                    return s

            if mstruct.is_matrix():
                for row in mstruct:
                    if row.is_vector():
                        ws.append([_cell_value(c) for c in row])
                    else:
                        ws.append([_cell_value(row)])
            elif mstruct.is_vector():
                for elem in mstruct:
                    ws.append([_cell_value(elem)])
            else:
                ws.append([_cell_value(mstruct)])

            wb.save(filename)
            return True
        except (OSError, PermissionError):
            return False

    def __repr__(self) -> str:
        return (
            f"Calculator(functions={len(self._functions)}, "
            f"variables={len(self._variables)}, "
            f"units={len(self._units)})"
        )


# Global calculator instance
_calculator: Calculator | None = None


def get_calculator() -> Calculator:
    """Return the global Calculator instance."""
    global _calculator
    if _calculator is None:
        _calculator = Calculator()
    return _calculator
