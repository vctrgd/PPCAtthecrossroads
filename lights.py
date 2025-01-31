import time
import os
import multiprocessing
import signal

def manage_lights(lights_dict):
    def handler(sig, frame):
        if sig == signal.SIGUSR1:
            print("Prio détecté NORD - SUD")
            # Basculer les feux
            print(f"🔄 Changement des feux : NS = {True}, EW = {False}")

            lights_dict["northsouth"] = True
            lights_dict["eastwest"] = False  # L'opposé de northsouth
        if sig == signal.SIGUSR2:
            print("Prio détecté EST - OUEST")
            # Basculer les feux
            lights_dict["northsouth"] = False
            lights_dict["eastwest"] = True  # L'opposé de northsouth
            print(f"🔄 Changement des feux : NS = {False}, EW = {True}")
            
    """Gère le changement des feux tricolores en mode normal."""
    signal.signal(signal.SIGUSR1, handler)
    signal.signal(signal.SIGUSR2, handler)

    
    while True:
        # Lire l'état actuel des feux
        northsouth = lights_dict["northsouth"]
        # Basculer les feux
        lights_dict["northsouth"] = not northsouth
        lights_dict["eastwest"] = northsouth  # L'opposé de northsouth
        print(f"🔄 Changement des feux : NS = {lights_dict['northsouth']}, EW = {lights_dict['eastwest']}")

        time.sleep(6)  # Attendre 5 secondes avant le changement
        

        