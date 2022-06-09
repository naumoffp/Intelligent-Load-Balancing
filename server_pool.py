import random
import time
import math
import re
from itertools import cycle


# TODO: Make it so that the server and IP registries are synced across containers
class Server(object):
    def __init__(self, locale):
        self.name = None
        self.locale = self.query_locale(locale)
        self.response_time = self.query_hardware()

        # Measured in milliseconds
        self.load = 0
        self.last_request = math.floor(time.time())
        self.latest_time_delta = 0

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
        inefficiency = 0

        # Factor the server load into the inefficiency score
        # Use the timestamp to see when the last request was
        time_delta = time.time() - self.last_request

        # Update this for the info report
        self.latest_time_delta = time_delta

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

        ip_locale = int(ip[:2])

        # This is designed to punish requests coming from other continents
        distance = abs(self.locale - ip_locale)
        if distance != 0:
            # See https://serverfault.com/questions/143804/network-latency-how-long-does-it-take-for-a-packet-to-travel-halfway-around-t
            inefficiency += 100

        # Add the hardware inefficiency to the load
        self.load += inefficiency

        # Cooling fans at work
        self.load = max(0, self.load - (25 * math.floor(time_delta)))

        server_response = self.response_time + self.load

        return server_response

    def info(self):
        # TODO: Make feature selection consistent across containers
        # server_attr = ["Server-Locale", "Server-Response-Time", "Server-Current-Load"]
        # misc_attr = ["IP-Locale",  "Last-Request-Time-Delta", "Overloaded"]
        # features = [*server_attr] + [*misc_attr]

        # TODO: Have this be generated from a file
        route_info = {
            10: "Africa (AF)",
            20: "Antarctica (AN)",
            30: "Asia (AS)",
            40: "Europe (EU)",
            50: "North America (NA)",
            60: "Oceania (OC)",
            70: "South America (SA)"
        }

        locale = route_info[self.locale]
        current_response_time = str(self.response_time)
        current_load = str(self.load)
        latest_time_delta = str(self.latest_time_delta)

        latest_info = {"Server-Locale": locale,
                       "Server-Response-Time": current_response_time,
                       "Server-Current-Load": current_load,
                       "Last-Request-Time-Delta": latest_time_delta
        }

        return latest_info


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

    def get_iterators(self):
        iterators = dict()
        for locale, sub_cluster in self.cluster.items():
            iterators[locale] = cycle(sub_cluster)

        return iterators


def basic_cluster():
    cluster = ServerCluster()

    cluster.add_servers("Antarctica (AN)", amount=2)

    cluster.add_servers("Africa (AF)", amount=4)
    cluster.add_servers("Asia (AS)", amount=4)
    cluster.add_servers("South America (SA)", amount=4)
    cluster.add_servers("Oceania (OC)", amount=4)

    cluster.add_servers("Europe (EU)", amount=6)
    cluster.add_servers("North America (NA)", amount=6)

    return cluster


def main():

    # Testing
    # na = x.query_cluster("North America (NA)")
    # eu = x.query_cluster("Europe (EU)")

    # for z in na:
    #     z.info()

    # for g in eu:
    #     g.info()

    print("This is the server pool")


if __name__ == "__main__":
    main()
