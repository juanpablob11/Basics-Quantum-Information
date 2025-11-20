from qiskit import QuantumCircuit

# ---------------------------------------------------------
# Public constants
# ---------------------------------------------------------

# Number of configuration bits for the Condor scheduler
N_CONFIG_BITS = 16

# Internal secret configuration (organisers only)
# x* = 1 0 1 1 1 0 1 0 1 1 0 1 0 1 0 1  (x_0 ... x_15)
SECRET_BITSTRING = "1011101011010101"


# ---------------------------------------------------------
# Internal oracle construction (reversible query f(x))
# ---------------------------------------------------------

def _build_internal_condor_oracle() -> QuantumCircuit:
    """
    Internal (n+1)-qubit circuit implementing the query oracle

        U_f |x, y> = |x, y ⊕ f(x)>,

    where f(x) = 1 iff x == SECRET_BITSTRING, and 0 otherwise.

    Qubits (Qiskit little-endian):
      0..15 : input bits x_0, ..., x_15
      16    : ancilla / output y
    """
    n = N_CONFIG_BITS
    qc = QuantumCircuit(n + 1, name="Uf_condor_internal")

    controls = list(range(n))
    anc = n

    # We want to flip ancilla iff the input matches SECRET_BITSTRING.
    # Standard pattern-matching trick:
    #   * For bits that should be '0', temporarily apply X so that
    #     the pattern "looks like" all-ones to the multi-controlled X.
    #   * Apply an n-controlled X on the ancilla.
    #   * Undo the temporary X gates.
    zeros = [i for i, b in enumerate(SECRET_BITSTRING) if b == "0"]

    # Pre-flip the '0' positions
    for i in zeros:
        qc.x(i)

    # Multi-controlled X on ancilla (controls = all 16 x-qubits)
    qc.mcx(controls, anc)

    # Undo the flips
    for i in zeros:
        qc.x(i)

    return qc


# ---------------------------------------------------------
# Public API for participants: build_Uf_condor()
# ---------------------------------------------------------

def build_Uf_condor() -> QuantumCircuit:
    """
    Public function for participants.

    Returns a 17-qubit QuantumCircuit that implements the query oracle

        U_f : |x>|y> -> |x>|y ⊕ f(x)>,

    where x ∈ {0,1}^16 encodes the scheduler configuration and
    y is a single ancilla qubit.

    The returned circuit consists of a single boxed gate "U_f"
    applied to the 17-qubit register, so its internal structure
    is hidden unless one explícitamente lo descomponga.
    """
    internal = _build_internal_condor_oracle()

    # Turn the internal circuit into a gate with a LaTeX label U_f
    Uf_gate = internal.to_gate(label=r"$U_f$")
    Uf_gate.name = "Uf_condor"

    # Wrap it in a 17-qubit circuit as a single box
    wrapper = QuantumCircuit(N_CONFIG_BITS + 1, name="Uf_condor")
    wrapper.append(Uf_gate, wrapper.qubits)

    return wrapper


__all__ = ["N_CONFIG_BITS", "build_Uf_condor"]
