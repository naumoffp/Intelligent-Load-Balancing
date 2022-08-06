import json
import os
import random
import time

import numpy as np
from numpy.random import multinomial

import sqs


class IPRegistry(object):
    def __init__(self):
        self.definitions = None
        self.build_definitions()

    def query(self, ip):
        # The first two numbers in an IP address in this registry indicate what continent it is orginating from
        geo_block = ip[:2]
        return self.definitions[geo_block]

    def build_definitions(self):
        # TODO: Have this be generated from a file
        # This route info is completely arbitrary
        route_info = {
            10: "Africa (AF)",
            20: "Antarctica (AN)",
            30: "Asia (AS)",
            40: "Europe (EU)",
            50: "North America (NA)",
            60: "Oceania (OC)",
            70: "South America (SA)"
        }

        # TODO: Add route info for localities and different regions inside of continents

        self.definitions = route_info
        return True


class IPBatch(object):
    def __init__(self):
        self.registry = IPRegistry()

    def rng(self, a, n, k):
        return random.sample(range(a, n), k)

    def determine_locale_dist(self, ip_amount, skew):
        # TODO: Add weights to some continents
        # TODO: Make it sometimes so that batch requests only come from one or two continents
        # TODO: Add exception for entering in a skew of 0

        # This will generate n integers between 0 and ip_amount, whose sum is ip_amount, with equal probability of drawing a given position.
        # Greater values for the skew will lead to greater variance
        s = skew
        n = len(self.registry.definitions)
        ip_dist = np.random.multinomial(ip_amount, np.random.dirichlet(np.ones(n) * (1/s))).tolist()

        # Swap the smallest number of ip addresses for Antartica's index position for realism
        an_index = 0
        min_index = ip_dist.index(min(ip_dist))
        ip_dist[an_index], ip_dist[min_index] = ip_dist[min_index], ip_dist[an_index]

        return ip_dist

    def generate_ip(self, ip_locale, locale_amount):
        # format: xx.xxx.xx.xxx
        small_batch = list()

        for _ in range(locale_amount):
            # self.rng returns a list so unpack it inplace
            rng_address = [ip_locale, *self.rng(100, 1000, 1), *self.rng(10, 100, 1), *self.rng(100, 1000, 1)]

            # Use map() to convert everything in the list to a string format
            ip = ".".join(map(str, rng_address))

            small_batch.append(ip)

        return small_batch

    def generate_batch(self, ip_amount, skew=2):
        # Get the geo distribution for where the ips are coming from
        ip_dist = self.determine_locale_dist(ip_amount, skew)
        batch = list()

        # Iterate over all 7 contintents in the distribution
        for index, n in enumerate(ip_dist):
            # Sanity check
            if n == 0:
                continue

            # Enumerate starts at 0 so add 1 to index
            # Arbitrarily multiply by 10 due to IPRegistry().definitions
            # TODO: refactor the locale logic into a different method that determines the locale automatically
            locale = (index + 1) * 10

            # Generate the specified number of ips that is deterimined by each element in ip_dist
            small_batch = self.generate_ip(locale, n)
            batch.extend(small_batch)

        # Example conversion of a locale distribution to an ip batch
        # [0 0 2 1 0 0 0] goes to --> ['30.482.43.513', '30.250.86.174', '40.574.39.640']

        return batch


def init_queue():
    # TODO: Add error handling
    server_pool     = "ilb-server-pool"
    load_balancer   = "ilb-load-balancer"

    request_spawner = "ilb-request-spawner"
    request_spawner_tag = request_spawner + ".fifo"
    spawner_queue = sqs.get_queue(request_spawner_tag)

    if not spawner_queue:
        print("Creating the queue...")

        spawner_queue = sqs.create_queue(
            request_spawner_tag,
            {
                'ReceiveMessageWaitTimeSeconds': str(10),
                'FifoQueue': str(True),
                'ContentBasedDeduplication': str(True),
                'VisibilityTimeout': str(1)
            }
        )

    return spawner_queue


def shutdown_queue():
    # TODO: Add error handling and make sure no messages are in-flight
    print("Removing the queue...")
    sqs.remove_queue(spawner_q)

def main():
    # server_pool     = sqs.get_url("SERVER_POOL_SQS")
    # load_balancer   = sqs.get_url("LOAD_BALANCER_SQS")
    # request_spawner = sqs.get_url("REQUEST_SPAWNER_SQS")


    ip_spawner = IPBatch()
    batch_routine = [1000]

    spawner_queue = init_queue()
    group_id = "ILBRS"

    while (True):
        user_input = input("Press Enter to send a batch of web traffic!")
        if user_input == "x":
            break

        for x in batch_routine:
            batch = ip_spawner.generate_batch(x)
            spawner_queue.send_message(MessageBody=json.dumps(batch), MessageGroupId=group_id)

    # If production is not specified the default assumption will be false
    if os.environ.get("PRODUCTION", False):
        shutdown_queue()


if __name__ == "__main__":
    main()
