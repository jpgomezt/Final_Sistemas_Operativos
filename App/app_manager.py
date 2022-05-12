import os
import time

if __name__=="__main__":
    numero = os.getpid()
    while True:
        time.sleep(numero)
