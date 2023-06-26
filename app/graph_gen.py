import time

import matplotlib.pyplot as plt
import numpy as np

from app.evaluation import evaluation_function


def docker_exp():
    plt.scatter(['250', '300', '350', '500', '1000', '5000'], [0.71, 0.70, 0.69, 0.70, 0.70, 0.68])
    plt.xlabel("Memory (MB)")
    plt.ylabel("Seconds(s)")
    plt.show()


def correctraynolds(mode = None):
    answer, params = 'Density, Velocity, Viscosity, Length', {"mode": mode}
    correct_responses = [
        'density,velocity,viscosity,length',
        'Density,Velocity,Viscosity,Length',
        'density,characteristic velocity,viscosity,characteristic length',
        'Density,Velocity,Shear viscosity,Length',
        'density,velocity,viscosity,lengthscale',
        'density,velocity,shear viscosity,length',
        'density,characteristic velocity,shear viscosity,characteristic lengthscale',
        'density,velocity,shear viscosity,characteristic lengthscale',
        'density,velocity,viscosity,length scale',
        'pressure,characteristic velocity of flow,shear viscosity,characteristic length scale',
    ]

    vals = []

    for response in correct_responses:
        result = evaluation_function(response, answer, params)
        vals.append(result["result"]["similarity_value"])

    plt.scatter(range(1, len(correct_responses) + 1), vals)
    plt.xlabel("String Id")
    plt.xticks(range(1, len(correct_responses) + 1))
    plt.ylabel("Confidence%")
    plt.ylim(0, 1.2)
    plt.show()

def incorrectraynolds(mode = None):
    answer, params = 'Density, Velocity, Viscosity, Length', {"mode": mode}
    incorrect_responses = [
        'density,,,',
        'rho,u,mu,L',
        'density, viscosity, airplane',
        'length, density, angle, mode',
        'velocity, speed, angle, size',
        'Density, Velocity, Viscosity',
        'Unrelated answer with density and velocity referenced, as well as length'
    ]

    vals = []

    for response in incorrect_responses:
        result = evaluation_function(response, answer, params)
        vals.append(result["result"]["similarity_value"])

    plt.scatter(range(11, len(incorrect_responses) + 11), vals)
    plt.xlabel("String Id")
    plt.xticks(range(11, len(incorrect_responses) + 11))
    plt.ylabel("Confidence%")
    plt.ylim(0, 1.2)
    plt.show()

def docker():
    answer = "The density of the film is uniform and constant, therefore the flow is incompressible. Since we have " \
             "incompressible flow, uniform viscosity, Newtonian fluid, the most appropriate set of equations for the " \
             "solution of the problem is the Navier-Stokes equations. The Navier-Stokes equations in Cartesian " \
             "coordinates are used: mass conservation and components of the momentum balance"
    response = "Navier-Stokes in a Cartesian reference coordinates would be chosen for this particular flow. This is " \
               "due to the reason that the flow is Newtonian, the viscosity is uniform and constant. Additionally, " \
               "the density is uniform and constant; implying that it is an incompressible flow. This flow obeys the " \
               "main assumptions in order to employ the Navier Stokes equations."
    params = {
        "keystrings": [
            {"string": "Navier-Stokes equations", "mode": "bow"},
            {"string": "mass conservation", "mode": "w2v"},
            {"string": "momentum balance", "mode": "transformer"},
            {"string": "incompressible flow", "mode": "bow"},
            {"string": "uniform viscosity", "mode": "w2v"},
            {"string": "Newtonian fluid", "mode": "transformer"}
        ],
        "mode": "transformer"
    }

def navier_stokes_comparison():
    answer = "The density of the film is uniform and constant, therefore the flow is incompressible. Since we have " \
             "incompressible flow, uniform viscosity, Newtonian fluid, the most appropriate set of equations for the " \
             "solution of the problem is the Navier-Stokes equations. The Navier-Stokes equations in Cartesian " \
             "coordinates are used: mass conservation and components of the momentum balance"
    response = "Navier-Stokes in a Cartesian reference coordinates would be chosen for this particular flow. This is " \
               "due to the reason that the flow is Newtonian, the viscosity is uniform and constant. Additionally, " \
               "the density is uniform and constant; implying that it is an incompressible flow. This flow obeys the " \
               "main assumptions in order to employ the Navier Stokes equations."

    for mode in ["w2v", "bow", "transformer"]:
        params = {
            "keystrings": [
                {"string": "Navier-Stokes equations", "mode": mode},
                {"string": "mass conservation", "mode": mode},
                {"string": "momentum balance", "mode": mode},
                {"string": "incompressible flow", "mode": mode},
                {"string": "uniform viscosity", "mode": mode},
                {"string": "Newtonian fluid", "mode": mode},
            ],
            "mode": "transformer"
        }
        result = evaluation_function(response, answer, params)
        print(result["result"]["keystring-scores"])


if __name__ == "__main__":
    navier_stokes_comparison()