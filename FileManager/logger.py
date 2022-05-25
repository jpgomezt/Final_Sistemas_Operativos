import logging

class Logger:

    def __init__(logger_file, data_file):
        logger_file = logging.basicConfig(filename=logger_file, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z', level=logging.ERROR)
        data_file = data_file
        error_count = 0
    
    def write_error(error, data):
        error_count += 1
        error = "[" + str(error_count) + "] " + str(error)
        logging.error(error)
        file = open(data_file, "a")
        file.write("[" + str(error_count) + "] " + data.decode() + "\n")
        file.close()

    def write_start(self):
        error = "Prueba"
        logging.error(error)
