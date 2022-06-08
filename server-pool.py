import random
import time
import math
import re


# TODO: Make it so that the server and IP registries are synced across containers
class Server(object):
    def __init__(self, locale):
        self.name = None
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
        return random.randint(200, 600)

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
        inefficiency += self.load

        server_response = self.response_time + inefficiency

        return server_response

    def info(self):
        print("Name: " + str(self.name))
        print("Locale: " + str(self.locale))
        print("Response Time: " + str(self.response_time))
        print("Load: " + str(self.load))
        print("Last Request (UTC): " + str(self.last_request))
        print("-"*88)


 # TODO: Make it so that the server and IP registries are synced across containers
class ServerCluster(object):

    def __init__(self):
        self.cluster = {
            "Africa (AF)": list(),
            "Antarctica (AN)": list(),
            "Asia (AS)": list(),
            "Europe (EU)": list(),
            "North America (NA)": list(),
            "Oceania (OC)": list(),
            "South America (SA)": list()
        }

    def query_cluster(self, locale):
        return self.cluster[locale]

    def add_servers(self, locale, amount):
        # Create each new server, attatch a name, then append it to the cluster
        for n in range(amount):
            name = locale[-4:] + "-" + str(n+1)
            # Remove parentheses from the string
            name = re.sub('[()]', '', name)
            new_server = Server(locale)
            new_server.name = name

            self.cluster[locale].append(new_server)


def main():
    x = ServerCluster()
    x.add_servers("North America (NA)", 3)
    x.add_servers("Europe (EU)", 3)

    na = x.query_cluster("North America (NA)")
    eu = x.query_cluster("Europe (EU)")

    for z in na:
        z.info()

    for g in eu:
        g.info()




if __name__ == "__main__":
    main()
