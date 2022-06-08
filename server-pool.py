import random
import time
import math


# TODO: Make it so that the server and IP registries are synced across containers
class Server(object):
    def __init__(self, locale):
        self.locale = self.query_locale(locale)
        self.response_time = self.query_hardware()

        # Measured in milliseconds
        self.load = 0
        self.last_request = math.floor(time.time())

    def query_locale(self, locale):
        # TODO: Organize route info so that distances between eachother reflect the real wolrd
        route_info = {
            "Africa (AF)": 10,
            "Antarctica (AN)": 20,
            "Asia (AS)": 30,
            "Europe (EU)": 40,
            "North America (NA)": 50,
            "Oceania (OC)": 60,
            "South America (SA)": 70
        }

        return route_info[locale]

    def query_hardware(self):
        # Measured in milliseconds
        return random.randint(200, 2000)

    def query_server(self, ip):
        # Measured in milliseconds
        inefficiency = self.load

        # Factor the server load into the inefficiency score
        # Use the timestamp to see when the last request was
        time_delta = time.time() - self.last_request

        # Sleep for one millisecond just in case this method is running on a supercomputer
        time.sleep(0.01)
        self.last_request = math.floor(time.time())

        # This is used to arbitrarility induce stress on the load for too many consecutive requests
        # Measured in seconds
        upper_limit = 1
        hardware_stress = max(0, 1 - time_delta)

        # Convert seconds to milliseconds and then arbitrarily divide by 10
        inefficiency += math.floor((hardware_stress * 1000) / 10)

        if hardware_stress < 0.95:
            # Reduce the stress of the machine if given 0.2 seconds to process
            self.load = math.floor(self.load / 2)
            inefficiency = 0


        # Add the hardware inefficiency to the load
        self.load += inefficiency

        ip_locale = int(ip[:2])

        # This is designed to punish requests coming from other continents
        distance = abs(self.locale - ip_locale)
        if distance != 0:
            # See https://serverfault.com/questions/143804/network-latency-how-long-does-it-take-for-a-packet-to-travel-halfway-around-t
            inefficiency += 100


        # Cooling fans at work
        self.load = max(0, self.load - 25)

        server_response = self.response_time + inefficiency

        return server_response


class ServerCluster(object):
    def __init__(self):
        pass

def main():
    x = Server("North America (NA)")
    while (True):
        print(x.query_server("50.123.45.678"))


if __name__ == "__main__":
    main()
