# Copyright © 2021 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration.  All Rights Reserved.

from scipy.integrate import solve_ivp

def euler_next_state(model, x, u, dt: float):
    """
    State transition equation using simple euler integration: Calls next_state(), calculating the next state, and then adds noise and applies limits

    Parameters
    ----------
    x : StateContainer
        state, with keys defined by model.states \n
        e.g., x = m.StateContainer({'abc': 332.1, 'def': 221.003}) given states = ['abc', 'def']
    u : InputContainer
        Inputs, with keys defined by model.inputs \n
        e.g., u = m.InputContainer({'i':3.2}) given inputs = ['i']
    dt : float
        Timestep size in seconds (≥ 0) \n
        e.g., dt = 0.1

    Returns
    -------
    x : StateContainer
        Next state, with keys defined by model.states
        e.g., x = m.StateContainer({'abc': 332.1, 'def': 221.003}) given states = ['abc', 'def']

    See Also
    --------
    PrognosticsModel.next_state
    """
    dx = model.dx(x, u)
    return model.StateContainer(
        {key: x[key] + dx[key]*dt for key in dx.keys()})


def rk4_next_state(model, x, u, dt: float):
    """
    State transition equation using rungekutta4 integration: Calls next_state(), calculating the next state, and then adds noise and applies limits

    Parameters
    ----------
    x : StateContainer
        state, with keys defined by model.states \n
        e.g., x = m.StateContainer({'abc': 332.1, 'def': 221.003}) given states = ['abc', 'def']
    u : InputContainer
        Inputs, with keys defined by model.inputs \n
        e.g., u = m.InputContainer({'i':3.2}) given inputs = ['i']
    dt : float
        Timestep size in seconds (≥ 0) \n
        e.g., dt = 0.1

    Returns
    -------
    x : StateContainer
        Next state, with keys defined by model.states
        e.g., x = m.StateContainer({'abc': 332.1, 'def': 221.003}) given states = ['abc', 'def']

    See Also
    --------
    PrognosticsModel.next_state
    """
    dx1 = model.StateContainer(model.dx(x, u))
    x2 = model.StateContainer(x.matrix + dx1.matrix*dt/2)
    dx2 = model.dx(x2, u)

    x3 = model.StateContainer(
        {key: x[key] + dt*dx_i/2 for key, dx_i in dx2.items()})
    dx3 = model.dx(x3, u)
    
    x4 = model.StateContainer(
        {key: x[key] + dt*dx_i for key, dx_i in dx3.items()})
    dx4 = model.dx(x4, u)

    x = model.StateContainer(
        {key: x[key] + dt/3*(dx1[key]/2 + dx2[key] + dx3[key] + dx4[key]/2) for key in dx1.keys()})
    return x


class SciPyIntegrateNextState():
    """
    State transition equation using scipy.integrate.solve_ivp integration: Calls dx(), calculating the next state using the scip.integrate.solve_ivp function, and then adds noise and applies limits

    Args:
        m (PrognosticsModel): PrognosticsModel object
        **kwargs: Keyword arguments to pass to scipy.integrate.solve_ivp

    Examples:
        >>> from prog_models.utils import SciPyIntegrateNextState
        >>> next_state = SciPyIntegrateNextState(m, sp.integrate.RK45)
        >>> next_state(x, u, dt)
    """
    def __init__(self, m, method):

        def f(_, x, u=m.InputContainer({})):
            return m.dx(m.StateContainer(x), m.InputContainer(u)).matrix.T[0]

        self.f = f
        self.method = method

    def __call__(self, m, x, u, dt: float):
        next_state = solve_ivp(
            self.f,
            t_span=(0, dt),
            y0=x.matrix.T[0],
            args=(u),
            method=self.method,
            **m.parameters.get('integrator_config', {}))

        return m.StateContainer(next_state.y.T[-1])

next_state_functions = {
    'euler': euler_next_state,
    'rk4': rk4_next_state
}
