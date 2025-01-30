# main.py
import multiprocessing
import time
import sysv_ipc
import normalTrafficGeneration
import priorityTrafficGeneration 
import coordinator
import lights

# Créer une nouvelle MessageQueue (clé unique)
mqNorth = sysv_ipc.MessageQueue(1, sysv_ipc.IPC_CREAT)
mqSouth = sysv_ipc.MessageQueue(2, sysv_ipc.IPC_CREAT)
mqEast = sysv_ipc.MessageQueue(3, sysv_ipc.IPC_CREAT)
mqWest = sysv_ipc.MessageQueue(4, sysv_ipc.IPC_CREAT)
mqList = [mqNorth, mqSouth, mqEast, mqWest]

if __name__ == "__main__":
    # Créer un verrou partagé pour synchroniser l'accès à currentId
    lock = multiprocessing.Lock()
    
    # Créer un entier partagé pour currentId, initialisé à 0
    currentId = multiprocessing.Value("i", 0)

    # Démarrer le processus de lecture des files de messages
    read_process = multiprocessing.Process(target=coordinator.readQueue, args=(mqList,))
    read_process.start()

    # Démarrer les générateurs de trafic avec currentId et le verrou partagés
    normal_traffic_process_north = multiprocessing.Process(target=normalTrafficGeneration.normalTrafficGenerator, args=(mqNorth, "North", currentId, lock))
    normal_traffic_process_south = multiprocessing.Process(target=normalTrafficGeneration.normalTrafficGenerator, args=(mqSouth, "South", currentId, lock))
    normal_traffic_process_east = multiprocessing.Process(target=normalTrafficGeneration.normalTrafficGenerator, args=(mqEast, "East", currentId, lock))
    normal_traffic_process_west = multiprocessing.Process(target=normalTrafficGeneration.normalTrafficGenerator, args=(mqWest, "West", currentId, lock))

    normal_traffic_process_north.start()
    normal_traffic_process_south.start()
    normal_traffic_process_east.start()
    normal_traffic_process_west.start()

    # Exécution pendant 10 secondes
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
    
    read_process.terminate()
    read_process.join()