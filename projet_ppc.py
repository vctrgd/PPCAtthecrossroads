#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import multiprocessing
import time
import random

# Directions du carrefour
DIRECTIONS = ["Nord", "Sud", "Est", "Ouest"]

# Processus pour générer le trafic en version normal
def normal_traffic_gen(queues, num_vehicles=10):
    for i in range(num_vehicles):
        source = random.choice(DIRECTIONS)
        destination = random.choice([d for d in DIRECTIONS if d != source])
        
        vehicle = f"Voiture-{i+1} ({source} -> {destination})"
        print(f"Génération: {vehicle}")
        queues[source].put((vehicle, destination))  # Ajouter le véhicule à la file source
        
        time.sleep(random.uniform(0.5, 1.5))

# Processus pour gérer les feux de circulation
def lights(light_status, cycle_time=5):
    while True:
        # Activer Nord-Sud, bloquer Est-Ouest
        light_status["Nord"] = light_status["Sud"] = "vert"
        light_status["Est"] = light_status["Ouest"] = "rouge"
        print("\n[FEUX] Nord-Sud: VERT | Est-Ouest: ROUGE")
        time.sleep(cycle_time)
        
        # Activer Est-Ouest, bloquer Nord-Sud
        light_status["Nord"] = light_status["Sud"] = "rouge"
        light_status["Est"] = light_status["Ouest"] = "vert"
        print("\n[FEUX] Nord-Sud: ROUGE | Est-Ouest: VERT")
        time.sleep(cycle_time)

# gestion du carrefour
def coordinator(queues, light_status):
    while True:
        # On vérifie chaque direction et décide si un véhicule peut passer
        for direction in DIRECTIONS:
            # Si des véhicules sont dans la queue de la direction et que le feu est vert
            if not queues[direction].empty() and light_status[direction] == "vert":
                vehicle, destination = queues[direction].get()  # Retirer le véhicule de la queue
                print(f"{vehicle} de {direction} passe vers {destination}.")
                # Mettre le véhicule dans la queue de la destination
                if destination in queues:
                    queues[destination].put((vehicle, destination))
                    print(f"{vehicle} est arrivé à {destination}")
            else:
                if not queues[direction].empty():
                    print(f"Feu rouge pour {direction}. Les véhicules attendent.")
                
        time.sleep(1) 

if __name__ == "__main__":
    # Création des queues pour chaque direction
    queues = {direction: multiprocessing.Queue() for direction in DIRECTIONS}

    # Création d'une mémoire partagée pour les feux de circulation
    manager = multiprocessing.Manager()
    light_status = manager.dict({direction: "rouge" for direction in DIRECTIONS})

    # Démarrer le processus des feux
    lights_process = multiprocessing.Process(target=lights, args=(light_	status,))
    lights_process.start()

    # Démarrer le générateur de trafic
    traffic_gen_process = multiprocessing.Process(target=normal_traffic_gen, args=(queues,))
    traffic_gen_process.start()

    # Démarrer le coordinateur
    coordinator_process = multiprocessing.Process(target=coordinator, args=(queues, light_status))
    coordinator_process.start()

    # Attendre la fin du générateur de trafic
    traffic_gen_process.join()

    # Arrêter tous les processus après un délai
    time.sleep(20)
    lights_process.terminate()
    coordinator_process.terminate()
