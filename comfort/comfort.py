import math

class Comfort(object):

    @classmethod
    def get_comfort_indices(temp_air=25.0, temp_radiant=25.0, air_vel=0.1, rel_humidity=50, met=1.2, clo=0.5, wme=0.0):
        """
        Args:
            temp_air (float): air temperature
            temp_radiant (float): radiant temperature
            air_vel (float): air/wind velocity
            rel_humidity (float): relative humidity
            met (float): metabolic equivalent
            clo (float): clothing level
            wme (float): external work

        Returns: 
            [pmv, ppd]
                pmv (float): predicted mean vote, range from -N to +N. 0 is neutral.
                ppd (float): percentage of dissatisfaction, range from 0 to 100.
        """
        pa = rel_humidity * 10 * math.exp(16.6536 - 4030.183 / (temp_air + 235))
        icl = 0.155 * clo # thermal insulation of the clothing in M2K/W
        m = met * 58.15 # metabolic rate in W/M2
        w = wme * 58.15 # external work in W/M2
        mw = m - w #internal heat production in the human body

        if icl <= 0.078:
            fcl = 1 + (1.29 * icl)
        else:
            fcl = 1.05 + (0.645 * icl)
            
        #heat transfer coefficient by forced convection
        hcf = 12.1 * math.sqrt(air_vel)
        taa = temp_air + 273
        tra = temp_radiant + 273
        tcla = taa + (35.5 - temp_air) / (3.5 * icl + 0.1)

        p1 = icl * fcl
        p2 = p1 * 3.96
        p3 = p1 * 100
        p4 = p1 * taa
        p5 = 308.7 - 0.028 * mw + p2 * math.pow(tra / 100, 4)

        xn = tcla / 100
        xf = tcla / 50
        eps = 0.00015

        n = 0
        while abs(xn - xf) > eps:
            xf = (xf + xn) / 2
            hcn = 2.38 * math.pow(abs(100.0 * xf - taa), 0.25)
            if hcf > hcn:
                hc = hcf
            else:
                hc = hcn
            xn = (p5 + p4 * hc - p2 * math.pow(xf, 4)) / (100 + p3 * hc)
            n = n + 1
            if n > 150:
                print("Max iteractions exceeded")
                break
        tcl = 100 * xn - 273
        hl1 = 3.05 * 0.001 * (5733 - (6.99 * mw) - pa)

        # hl2: evaporation via sweat secreation
        if mw > 58.15:
            hl2 = 0.42 * (mw - 58.15)
        else:
            hl2 = 0
        hl3 = 1.7 * 0.00001 * m * (5867 - pa)
        hl4 = 0.0014 * m * (34 - temp_air)
        hl5 = 3.96 * fcl * (math.pow(xn, 4) - math.pow(tra / 100, 4))
        hl6 = fcl * hc * (tcl - temp_air)

        ts = 0.303 * math.exp(-0.036 * m) + 0.028

        pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)
        ppd = 100.0 - 95.0 * math.exp(-0.03353 * math.pow(pmv, 4.0) - 0.2179 * math.pow(pmv, 2.0))

        return pmv, ppd