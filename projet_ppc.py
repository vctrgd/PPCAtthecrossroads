#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Created on Mon Jan 27 08:12:15 2025

@author: vrigaud
"""
import multiprocessing
import time
import random

# Directions du carrefour
DIRECTIONS = ["Nord", "Sud", "Est", "Ouest"]

num_vehicles=10

# Processus pour générer le trafic
def normal_traffic_gen(queues, num_vehicles):
    for i in range(num_vehicles):
        source = random.choice(DIRECTIONS)
        destination = random.choice([d for d in DIRECTIONS if d != source])
        
        vehicle = f"Voiture-{i+1} ({source} -> {destination})"
        vehicle_type = "normal"
        print(f"Génération: {vehicle}")
        queues[source].put((vehicle, destination, vehicle_type))  # Ajouter le véhicule à la file source
        
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
 
# Processus pour gérer chaque direction
def direction_handler(direction, queue, queues, light_status):
    while True:
        if not queue.empty():
            vehicle, destination, vehicle_type = queue.get()

            # Vérifier si le feu est vert pour cette direction
            if light_status[direction] == "vert":
                print(f"{direction}: {vehicle} passe vers {destination}.")
                time.sleep(1)  # Simule le passage
                if destination in queues:
                    queues[destination].put((vehicle, destination,vehicle_type))
                    print(f"{vehicle} est arrivé à {destination}")
            else:
                print(f"{direction}: {vehicle} en attente (feu rouge).")
                queue.put((vehicle, destination,vehicle_type))  # Remet dans la file d'attente
                time.sleep(1)

# Processus pour gérer le carrefour
def intersection_manager(queues, light_status):
    while True:
        for direction, queue in queues.items():
            if not queue.empty():
                vehicle, destination, vehicle_type = queue.get()

                if light_status[direction] == "vert":
                    print(f"Feu vert pour {direction}: {vehicle} passe.")
                    time.sleep(1)
                else:
                    print(f"Feu rouge pour {direction}: {vehicle} attend.")
                    queue.put((vehicle, destination, vehicle_type))  # Remettre en attente
                    time.sleep(1)

if __name__ == "__main__":
    # Création des queues pour chaque direction
    queues = {direction: multiprocessing.Queue() for direction in DIRECTIONS}

    # Création d'une mémoire partagée pour les feux de circulation
    with multiprocessing.Manager() as manager:
        light_status = manager.dict({direction: "rouge" for direction in DIRECTIONS})
    
        # Démarrer le processus des feux
        lights_process = multiprocessing.Process(target=lights, args=(light_status,))
        lights_process.start()
    
        # Démarrer le générateur de trafic
        traffic_gen_process = multiprocessing.Process(target=normal_traffic_gen, args=(queues,num_vehicles))
        traffic_gen_process.start()
    
        # Démarrer les gestionnaires de direction
        processes = []
        for direction in DIRECTIONS:
            process = multiprocessing.Process(target=direction_handler, args=(direction, queues[direction], queues, light_status))
            processes.append(process)
            process.start()
    
        # Démarrer le gestionnaire de carrefour
        manager_process = multiprocessing.Process(target=intersection_manager, args=(queues, light_status))
        manager_process.start()
    
        # Attendre la fin du générateur de trafic
        traffic_gen_process.join()
    
        # Arrêter tous les processus après un délai
        time.sleep(20)
        for process in processes:
            process.terminate()
    

        lights_process.terminate()
