import pytest
import numpy as np
from math_utils.lyapunov import LyapunovFunction, StabilityAnalyzer, estimate_lyapunov_exponent

# Fixtures for a stable linear system: x_dot = A*x, where A is stable
@pytest.fixture
def stable_system():
    A = np.array([[-1, -1], [1, -1]])  # Eigenvalues with negative real parts
    P = np.array([[1, 0], [0, 1]])    # Identity matrix, positive definite
    lyapunov_func = LyapunovFunction(function_type='quadratic', P=P)
    system_dynamics = lambda x: A @ x
    return lyapunov_func, system_dynamics

# Fixtures for an unstable linear system
@pytest.fixture
def unstable_system():
    A = np.array([[1, 1], [-1, 1]]) # Eigenvalues with positive real parts
    P = np.array([[1, 0], [0, 1]])
    lyapunov_func = LyapunovFunction(function_type='quadratic', P=P)
    system_dynamics = lambda x: A @ x
    return lyapunov_func, system_dynamics

def test_lyapunov_function_quadratic_init():
    P = np.array([[2, 1], [1, 2]])
    lf = LyapunovFunction(function_type='quadratic', P=P)
    assert np.array_equal(lf.P, P)

    with pytest.raises(ValueError, match="Matrix P must be provided"):
        LyapunovFunction(function_type='quadratic')

    P_not_pd = np.array([[-1, 0], [0, -1]])
    with pytest.raises(ValueError, match="must be positive definite"):
        LyapunovFunction(function_type='quadratic', P=P_not_pd)

def test_lyapunov_function_evaluate_derivative_general():
    lf = LyapunovFunction(function_type='general')
    with pytest.raises(NotImplementedError):
        lf.evaluate(np.array([1, 1]))
    with pytest.raises(NotImplementedError):
        lf.derivative(np.array([1, 1]), np.array([1, 1]))

def test_lyapunov_function_evaluate_quadratic():
    P = np.array([[2, 1], [1, 2]])
    lf = LyapunovFunction(function_type='quadratic', P=P)
    x = np.array([1, 2])
    # V(x) = x.T * P * x = [1*2+2*1, 1*1+2*2] * [1,2].T = [4, 5] * [1,2].T = 4+10=14
    assert lf.evaluate(x) == 14

def test_lyapunov_function_derivative_quadratic(stable_system):
    lyapunov_func, system_dynamics = stable_system
    x = np.array([1, 1])
    x_dot = system_dynamics(x)
    # V_dot = x_dot.T*P*x + x.T*P*x_dot
    # x_dot = [-2, 0].T
    # V_dot = [-2, 0]*[[1,0],[0,1]]*[1,1].T + [1,1]*[[1,0],[0,1]]*[-2,0].T = -2 + -2 = -4
    assert lyapunov_func.derivative(x, x_dot) == -4

def test_stability_analyzer_asymptotically_stable(stable_system):
    lyapunov_func, system_dynamics = stable_system
    analyzer = StabilityAnalyzer(lyapunov_func, system_dynamics)
    x = np.array([1, 0])
    assert analyzer.check_stability(x) == 'asymptotically stable'

def test_stability_analyzer_unstable(unstable_system):
    lyapunov_func, system_dynamics = unstable_system
    analyzer = StabilityAnalyzer(lyapunov_func, system_dynamics)
    x = np.array([1, 0])
    assert analyzer.check_stability(x) == 'unstable'

def test_stability_analyzer_stable():
    # System where V_dot is zero
    A = np.array([[0, -1], [1, 0]]) # Rotational system
    P = np.eye(2)
    lyapunov_func = LyapunovFunction(function_type='quadratic', P=P)
    system_dynamics = lambda x: A @ x
    analyzer = StabilityAnalyzer(lyapunov_func, system_dynamics)
    x = np.array([1, 0])
    # V_dot should be 0
    assert analyzer.check_stability(x) == 'stable'

def test_stability_analyzer_estimate_rate(stable_system):
    lyapunov_func, system_dynamics = stable_system
    analyzer = StabilityAnalyzer(lyapunov_func, system_dynamics)
    x = np.array([1, 1])
    rate = analyzer.estimate_stability_rate(x)
    # V(x) = x.T*P*x = 2
    # V_dot(x) = -4
    # rate = -V_dot/V = 4/2 = 2
    assert pytest.approx(rate) == 2.0

def test_stability_analyzer_validate_trajectory(stable_system):
    lyapunov_func, system_dynamics = stable_system
    analyzer = StabilityAnalyzer(lyapunov_func, system_dynamics)
    # Generate a trajectory for the stable system
    x0 = np.array([2, 2])
    trajectory = [x0]
    dt = 0.1
    for _ in range(10):
        x_next = trajectory[-1] + system_dynamics(trajectory[-1]) * dt
        trajectory.append(x_next)
    assert analyzer.validate_trajectory(trajectory) == True

    # Manually create an unstable trajectory
    unstable_traj = [np.array([1,1]), np.array([2,2])]
    assert analyzer.validate_trajectory(unstable_traj) == False

def test_estimate_lyapunov_exponent():
    # Converging (stable) trajectory
    stable_traj = np.array([10, 5, 2.5, 1.25])
    # log ratios are approx ln(0.5) = -0.693
    assert estimate_lyapunov_exponent(stable_traj) < 0

    # Diverging (unstable/chaotic) trajectory
    unstable_traj = np.array([1, 2, 4, 8])
    # log ratios are approx ln(2) = 0.693
    assert estimate_lyapunov_exponent(unstable_traj) > 0

    # Zero handling
    zero_traj = np.array([1, 0, 1])
    assert np.isfinite(estimate_lyapunov_exponent(zero_traj))

    # Empty trajectory
    assert estimate_lyapunov_exponent(np.array([])) == 0.0
