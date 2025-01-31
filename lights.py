import time
import os
import multiprocessing
import signal

def manage_lights(lights_dict):
    """Gère le changement des feux tricolores en mode normal."""
    while True:
        # Lire l'état actuel des feux
        northsouth = lights_dict["northsouth"]
        # Basculer les feux
        lights_dict["northsouth"] = not northsouth
        lights_dict["eastwest"] = northsouth  # L'opposé de northsouth
        print(f"🔄 Changement des feux : NS = {lights_dict['northsouth']}, EW = {lights_dict['eastwest']}")

        time.sleep(6)  # Attendre 5 secondes avant le changement