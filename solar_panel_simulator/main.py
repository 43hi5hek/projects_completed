"""
SOLAR WATER HEATER SIMULATION
"""


"""
ASSUMPTIONS:

- Pump has not been modeled. It is abstracted by only considering a constant fluid velocity throughout.
- All quantities are in SI units
- Sunrise/Sunset modeled as a sine wave (see function get_solar_rad())
- Ambient temperature is constant (shouldn't matter much, because convection losses are arbitrary)
- Heat loss in pipes is not modeled
- Convection losses are arbirary. If modeled, it only introduces a ton of extra variables like Grasshof's number, Nusselt's number
- Fluid properties remain constant with temperature
- Specific assumptions listed wherever necessary

"""



import numpy as np
import math
import matplotlib.pyplot as plt




"""
Helper Functions
"""

def Kelvin(T):
    return (T + 273)

def get_solar_rad(solar_rad, time, cycle):
    """
    :param solar_rad: max solar radiation per square meter
    :param time: seconds passed since sunrise
    :param cycle: True if you want to implement sunrise-sunset effect
    :return: total incident solar radiation per square meter at a given time
    """
    if cycle:
        a = math.sin((2*math.pi*time)/86400)
        return (solar_rad * a) if (a>0) else 0
    else:
        return solar_rad


"""
Solar Panel
- Keeps track of physical parameters
"""

class SolarPanel:

    def __init__(self, T=25, effi=0.5, emmi=0.4, pipe_len=5, pipe_dia=0.025, panel_area=1, panel_thickness=0.06, C=500):
        """
        :param T: temp of the panel/pipe
        :param effi: how well does panel transfer heat to pipes
        :param emmi: panel emissivity in radiation
        :param pipe_len: length of pipe in the panel
        :param pipe_dia: pipe diameter
        :param panel_area: panel area exposed to the sun
        :param panel_thickness: panel thickness
        :param C: specific heat capacity of panel

        I have assumed that the solar panel is a solid block of metal. Pipe runs through this block.
        Inner wall of the pipe is the same material as the block.
        """
        self.T = T
        self.effi = effi
        self.pipe_len = pipe_len
        self.pipe_dia = pipe_dia
        self.pipe_area = (math.pi * (self.pipe_dia)**2) / 4
        self.panel_area = panel_area
        self.panel_thickness = panel_thickness
        self.C = C
        self.emmi = emmi

    def UpdateTemp(self):
        """
        function: updates the temperature of pipes after each timestep
        :return: temperature of pipe inside panel

        In one time-step, the panel receives solar radiation, transfers some of it to the pipes (instantaneously),
        the pipes use that heat to increase their temperature
        """

        # panel gets solar radiation
        radiation_in = get_solar_rad(solar_rad, time, cycle) * self.effi * self.panel_area

        # panel radiates heat to surrounding and loses heat by convection
        radiation_loss = sigma * self.panel_area * self.emmi * ((Kelvin(self.T))**4 - (Kelvin(T_amb))**4) * dt
        convection_loss = 0.2 * radiation_loss # arbitrary
        panel_available_heat = radiation_in - (radiation_loss + convection_loss)

        # panel/pipe absorbs available heat and increases its temp
        panel_mass = self.panel_thickness * self.panel_area * 7800
        self.T = self.T + (panel_available_heat / (self.C * panel_mass))

        return self.T



"""
Fluid
- Keeps track of fluid's physical properties
"""
class Fluid:
    def __init__(self, solarpanel, tank_volume=2, T_panel_out=25, T_tank_out=25, C=4180, rho=1000, velocity=0.05, ht_coeff=300):
        """
        :param solarpanel: SolarPanel object
        :param tank_volume: volume of storage tank (and the contained water)
        :param T_panel_out: temperature at panel outlet (= temperature at tank inlet)
        :param T_tank_out: temperature at tank outlet (= temperature at panel inlet)
        :param C: specific heat capacity of fluid
        :param rho: fuild density
        :param velocity: fluid velocity in the circuit
        :param ht_coeff: fluid-pipe effective heat transfer coefficient

        """
        self.rho = rho
        self.velocity = velocity
        self.C = C
        self.ht_coeff = ht_coeff
        self.T_panel_out = T_panel_out
        self.T_tank_out = T_tank_out
        self.alpha = (4 * self.ht_coeff) / (self.C * self.rho * self.velocity * solarpanel.pipe_dia)
        self.len = solarpanel.pipe_len
        self.pipe_area = solarpanel.pipe_area
        self.tank_volume = tank_volume

    def UpdateTemp(self, pipe_temp_updated):
        """
        function: updates the fluid temperatures at tank outlet and panel outlet
        :param pipe_temp_updated: updated pipe temperature at the current timestep
        :return: panel outlet temperature, tank outlet temperature

        In one timestep, a fluid pocket travels some distance through the pipes,
        fluid temperature coming out of the pipes increases, this hot fluid is mixed with the tank fluid,
        tank fluid temperature increases
        """

        # temp of fluid after it travels through the panel and comes out (see attached note 1)
        self.T_panel_out = pipe_temp_updated + ((self.T_tank_out - pipe_temp_updated) * math.exp(-self.alpha * self.len))

        # increase in the temperature of tank after hot water is mixed into it (see attached note 2)
        m = self.rho * self.pipe_area * self.velocity * dt
        M = self.tank_volume * self.rho
        self.T_tank_out = (m * self.T_panel_out + M * self.T_tank_out) / (m + M)

        return self.T_panel_out, self.T_tank_out






"""
MAIN LOOP
keeping track of 3 temperatures:
- pipes in solar panel
- temperature of water at panel output
- temperature of water at tank output
"""
if __name__ == "__main__":
    cycle = False # True -> enable sunrise/sunset
    dt = 1 # sec
    steps = 500000
    T_amb = 25  # Ambient temperature in C

    solar_rad = 1000 # source: Internet
    sigma = 5.67e-8

    Panel = SolarPanel()
    Water = Fluid(solarpanel=Panel)

    time_array = dt * np.arange(steps)
    tank_outlet_temps = []
    panel_outlet_temps = []
    pipe_temps = []

    for i in range(steps):
        # seconds passed since sunrise
        time = dt*i

        # solar radiation -> pipes heat up
        pipe_temp_updated = Panel.UpdateTemp()

        # water absorbs heat -> water goes in tank -> tank temp increases
        panel_out_temp_updated, tank_out_temp_updated = Water.UpdateTemp(pipe_temp_updated)

        # for plotting
        pipe_temps.append(pipe_temp_updated)
        tank_outlet_temps.append(tank_out_temp_updated)
        panel_outlet_temps.append(panel_out_temp_updated)

    timearray_hrs = time_array/3600
    plt.plot(timearray_hrs, pipe_temps, label="pipe temp")
    plt.plot(timearray_hrs, panel_outlet_temps, label="panel outlet temp")
    plt.plot(timearray_hrs, tank_outlet_temps, label="tank outlet temp")
    plt.legend(loc="lower right")
    plt.xlabel("time (hrs)")
    plt.ylabel("temperature (C)")
    plt.show()



