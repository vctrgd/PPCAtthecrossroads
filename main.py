# main.py
import multiprocessing
import time
import sysv_ipc
import normalTrafficGeneration
import priorityTrafficGeneration 
import coordinator
import lights
import display

# Créer une nouvelle MessageQueue (clé unique)
mqNorth = sysv_ipc.MessageQueue(1, sysv_ipc.IPC_CREAT)
mqSouth = sysv_ipc.MessageQueue(2, sysv_ipc.IPC_CREAT)
mqEast = sysv_ipc.MessageQueue(3, sysv_ipc.IPC_CREAT)
mqWest = sysv_ipc.MessageQueue(4, sysv_ipc.IPC_CREAT)
mqList = [mqNorth, mqSouth, mqEast, mqWest]

def clear_queues(mqList):
    """Vide toutes les queues de messages au lancement."""
    for mq in mqList:
        try:
            while True:
                mq.receive(block=False)  # Tente de vider les messages existants
        except sysv_ipc.BusyError:
            pass  # La queue est vide, on passe à la suivante
        
clear_queues(mqList)

if __name__ == "__main__":
    
    manager = multiprocessing.Manager()
    lights_dict = manager.dict({"northsouth": True, "eastwest": False})    
    # Créer un verrou partagé pour synchroniser l'accès à currentId
    lockCurrentId = multiprocessing.Lock()
    
    # Créer un entier partagé pour currentId, initialisé à 0
    currentId = multiprocessing.Value("i", 0)

    display_process = multiprocessing.Process(target=display.run_display)
    display_process.start()
    time.sleep(3) 


    lights_process = multiprocessing.Process(target=lights.manage_lights, args=(lights_dict,))
    lights_process.start()

    # Démarrer le processus de lecture des files de messages
    read_process = multiprocessing.Process(target=coordinator.coordinate, args=(mqList,lights_dict,lights_process.pid))
    read_process.start()
    
  

    # Démarrer les générateurs de trafic avec currentId et le verrou partagés
    normal_traffic_process_north = multiprocessing.Process(target=normalTrafficGeneration.normalTrafficGenerator, args=(mqNorth, "North", currentId, lockCurrentId))
    normal_traffic_process_south = multiprocessing.Process(target=normalTrafficGeneration.normalTrafficGenerator, args=(mqSouth, "South", currentId, lockCurrentId))
    normal_traffic_process_east = multiprocessing.Process(target=normalTrafficGeneration.normalTrafficGenerator, args=(mqEast, "East", currentId, lockCurrentId))
    normal_traffic_process_west = multiprocessing.Process(target=normalTrafficGeneration.normalTrafficGenerator, args=(mqWest, "West", currentId, lockCurrentId))

    priority_traffic_process_north = multiprocessing.Process(target=priorityTrafficGeneration.priorityTrafficGenerator, args=(mqNorth, "North", currentId, lockCurrentId))
    priority_traffic_process_south = multiprocessing.Process(target=priorityTrafficGeneration.priorityTrafficGenerator, args=(mqSouth, "South", currentId, lockCurrentId))
    priority_traffic_process_east = multiprocessing.Process(target=priorityTrafficGeneration.priorityTrafficGenerator, args=(mqEast, "East", currentId, lockCurrentId))
    priority_traffic_process_west = multiprocessing.Process(target=priorityTrafficGeneration.priorityTrafficGenerator, args=(mqWest, "West", currentId, lockCurrentId))
    
    
    normal_traffic_process_north.start()
    normal_traffic_process_south.start()
    normal_traffic_process_east.start()
    normal_traffic_process_west.start()
    priority_traffic_process_north.start()
    priority_traffic_process_south.start()
    priority_traffic_process_east.start()
    priority_traffic_process_west.start()
    
    # Exécution pendant 30 secondes
    time.sleep(10)

    # Terminer les processus proprement
    normal_traffic_process_north.terminate()
    normal_traffic_process_north.join()
    
    normal_traffic_process_south.terminate()
    normal_traffic_process_south.join()
    
    normal_traffic_process_east.terminate()
    normal_traffic_process_east.join()
    
    normal_traffic_process_west.terminate()
    normal_traffic_process_west.join()
    
    priority_traffic_process_north.terminate()
    priority_traffic_process_north.join()
    
    priority_traffic_process_south.terminate()
    priority_traffic_process_south.join()
    
    priority_traffic_process_east.terminate()
    priority_traffic_process_east.join()
    
    priority_traffic_process_west.terminate()
    priority_traffic_process_west.join()
    
    lights_process.terminate()
    lights_process.join()
    
    read_process.terminate()
    read_process.join()
    
    display_process.terminate()
    display_process.join()
    manager.shutdown()