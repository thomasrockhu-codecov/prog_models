"""
"""

# IMPORTS
# ========
# from utilities.imports_ import np
import numpy as np


# FUNCTIONS
# ========
def rotorcraft_cam(n, l, b, d, constrained=False):
    """
    Generate control allocation matrix (CAM) to transform rotor's angular velocity into thrust and torques around three main body axis.
    
        [T, Mx, My, Mz]^{\top} = \Gamma [\Omega_1^2, \Omega_2^2, ..., \Omega_n^2]^{\top}
    
    Where:
        [T, Mx, My, Mz]^{\top} is the (4 x 1) column vector containing thrust (T) and moments along main body axis (Mx, My, Mz)
        \Gamma is the (4 x n) CAM
        [\Omega_1^2, \Omega_2^2, ..., \Omega_n^2]^{\top} is the (n x 1) column vector of the rotor angular speed squared.
    
    The control allocation matrix is built under the assumption of symmetric rotor configuration, for generality.
    Special CAM should be built ad-hoc per UAV model.

    :param n:           number of rotors
    :param l:           rotor arm's length (from center of mass to rotor center)
    :param b:           thrust constant, function of rotor type
    :param d:           torque constant, function of rotor type
    :return:            control allocation matrix of dimensions (4, n) and its pseudo-inverse of dimensions (n, 4)
    """
    
    Gamma = np.empty((4, n))
    optional = {}
    if n == 8 and not constrained:
        l_b        = l * b
        l_b_sq2o2 = l_b * np.sqrt(2.0)/2.0
        # This CAM is assuming there's no rotor pointing towards the drone forward direction (x-axis)
        # See Dmitry Luchinsky's report for details (TO BE VERIFIED)
        Gamma = np.array([ [   b,           b,     b,          b,     b,          b,    b,         b],
                           [  l_b,  l_b_sq2o2,   0.0, -l_b_sq2o2,  -l_b, -l_b_sq2o2,  0.0, l_b_sq2o2], 
                           [  0.0, -l_b_sq2o2,  -l_b, -l_b_sq2o2,   0.0,  l_b_sq2o2,  l_b, l_b_sq2o2],
                           [   -d,          d,    -d,          d,    -d,          d,   -d,         d]])
    if n == 8 and constrained:
        bl = b * l
        b2 = 2.0 * b
        d2 = 2.0 * d
        blsqrt2 = np.sqrt(2.0) * bl

        Gamma = np.array([ [ b2,       b2,  b2,      b2],
                           [ bl,      0.0, -bl,     0.0],
                           [-bl, -blsqrt2,  bl, blsqrt2],
                           [-d2,       d2, -d2,      d2] ])
        optional['selector'] = np.array([ [1, 0, 1, 0, 0, 0, 0, 0],
                                          [0, 1, 0, 1, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 1, 0, 1, 0],
                                          [0, 0, 0, 0, 0, 1, 0, 1]]).T

    return Gamma, np.linalg.pinv(Gamma), optional

"""
def profile2input(m, Ix, Iy, Iz, acc_x, acc_y, acc_z, phi, theta, psi, p, q, r, t, g, type='rotorcraft'):
    if type=='rotorcraft':
        u = rotorcraft_profile2input(m, Ix, Iy, Iz, acc_x, acc_y, acc_z, phi, theta, psi, p, q, r, t, g)
    else:
        raise Exception("Aircraft types other than rotorcraft not implemented (yet).")
    return u


def rotorcraft_profile2input(mass, Ixx, Iyy, Izz, xddot, yddot, zddot, phi, theta, psi, p, q, r, t, g):

    sin_phi   = np.sin(phi)
    sin_theta = np.sin(theta)
    sin_psi   = np.sin(psi)
    cos_phi   = np.cos(phi)
    cos_theta = np.cos(theta)
    cos_psi   = np.cos(psi)

    Tdes_x = xddot * mass / (sin_theta * cos_psi * cos_phi + sin_phi * sin_psi)
    Tdes_y = yddot * mass / (sin_theta * sin_psi * cos_phi - sin_phi * cos_psi)
    Tdes_z = (g + zddot) * mass / (cos_phi * cos_theta)
    
    Tdes_x = np.nan_to_num(Tdes_x)
    Tdes_y = np.nan_to_num(Tdes_y)
    Tdes_z = np.nan_to_num(Tdes_z)
    # Find the maximum of 3 force estimates obtained from accelerations
    Tdes_ = np.max(np.hstack((Tdes_x.reshape((-1,1)),
                              Tdes_y.reshape((-1,1)),
                              Tdes_z.reshape((-1,1)))), axis=1)
    
    pdot = np.insert(np.diff(p) / np.diff(t), 0, 0.0)
    qdot = np.insert(np.diff(q) / np.diff(t), 0, 0.0)
    rdot = np.insert(np.diff(r) / np.diff(t), 0, 0.0)

    Mdes_x = (pdot - (Iyy - Izz) / Ixx * q * r) * Ixx
    Mdes_y = (qdot - (Izz - Ixx) / Iyy * p * r) * Iyy
    Mdes_z = (rdot - (Ixx - Iyy) / Izz * p * q) * Izz

    Udes = np.hstack((Tdes_.reshape((-1,1)), Mdes_x.reshape((-1,1)), Mdes_y.reshape((-1,1)), Mdes_z.reshape((-1,1))))
    return Udes


    
def omega2throttle(omega_des, low=0.25):
    slope     = 769.1126750114285   # from steady-state powertrain model (see powertrain.py)
    intercept = 1.320435489285785   # from steady-state powertrain model (see powertrain.py)
    throttle_des  = (omega_des - intercept) / slope
    return np.fmax(low, np.fmin(1.0, throttle_des))  # set limits for throttle



def test_control_allocation_function():
    import matplotlib.pyplot as plt
    radps2rpm = 9.5493

    print(" Control Allocation ")
    g = 9.81    # m/s^2, gravity
    m = 6.0     # kg, mass
    n = 8       # number of rotors
    b = 0.4     # length of each arm

    kt = 4e-5
    km = 5e-5
    
    hover_rpm = 4095.5 # taken for granted

    B, Binv, _ = rotorcraft_cam(n, b, kt, km)

    T = m * g

    U = np.array([T, 0.0, 0.0, 0.0]).reshape((-1,))

    omega_squared = Binv @ U
    omega = np.sqrt(omega_squared)

    print('\n')
    for ii in range(n):
        print(f'Rotor {ii+1}: {np.round(omega[ii] * radps2rpm,2)} RPM -- {100.0*np.round((omega[ii]*radps2rpm)/hover_rpm, 2)}% of hovering')
    plt.show()
    return
"""
"""
if __name__ == '__main__':


    import numpy as np
    import matplotlib.pyplot as plt

    n = 8
    l = 0.365
    b = 1.e-2
    d = 5.e-3
    G, Ginv, _ = rotorcraft_cam(n, l, b, d, constrained=False)

    print('CAM')
    print(np.round(G, 3))
    print('inverse')
    print(Ginv)


    plt.show()
    # =======
    # END
    """
    