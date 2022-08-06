import json
import logging
import os
from itertools import cycle

import file_helpers
import server_pool
import sqs

RR_TIME = 0
RR_OVERLOAD = 0
RR_ITERATORS = None

def round_robin(incoming, cluster):
    print("Processing incoming web requests with round robin algorithm...\n")
    global RR_TIME
    global RR_OVERLOAD
    global RR_ITERATORS

    training_data = list()

    # TODO: Make feature selection consistent across containers
    # TODO: Make server response time correlate with its ability to handle server loads
    server_attr = ["Server-Locale", "Server-Response-Time", "Server-Current-Load"]
    misc_attr = ["Last-Request-Time-Delta", "Overloaded"]
    features = [*server_attr] + [*misc_attr]

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
    avg_load = 0
    # Determine where the IP is coming from
    for index, ip in enumerate(incoming):
        # Get the current place in the round robin circle that the iterator is on
        locale_number = int(ip[:2])
        locale_name = route_info[locale_number]
        iterator = RR_ITERATORS[locale_name]

        to_query = next(iterator)
        response_time = to_query.query_server(ip)
        server_info = to_query.info()
        avg_load += int(server_info["Server-Current-Load"])

        RR_TIME += response_time

        is_overloaded = False

        # On a first batch of 10k web-requests it was found that:
        # Average Load: 5.2651
        # RR Number of Servers Overloaded: 472
        # RR Cumulative Response Time (minutes): 70.72
        # Thus, the threshold value is set at 5
        threshold = 5

        if to_query.load > threshold:
            RR_OVERLOAD += 1
            is_overloaded = True

        # Add the remaining features to the server info
        server_info["Overloaded"] = is_overloaded
        # TODO: Implement this feature
        # server_info["IP-Locale"] = locale_name

        training_data.append(server_info)

    time_conversion = float("{0:.2f}".format(((RR_TIME / 1000) / 60)))

    # Create dummy matrix for locales
    print("Writing the training data...")

    # Write training data to csv
    file_pattern = "Data/batch_%s.csv"

    file_helpers.write_training_data(file_pattern, features, training_data)

    print(f"Average Load: {(avg_load / len(incoming))}")
    print(f"RR Number of Servers Overloaded: {RR_OVERLOAD}")
    print(f"RR Cumulative Response Time (minutes): {time_conversion}")


def main():
    # TODO: Implement interprocess communication
    # server_pool     = sqs.get_url("SERVER_POOL_SQS")
    # load_balancer   = sqs.get_url("LOAD_BALANCER_SQS")
    # request_spawner = sqs.get_url("REQUEST_SPAWNER_SQS")

    # server_pool     = "ilb-server-pool"
    # load_balancer   = "ilb-load-balancer"

    cluster = server_pool.basic_cluster()

    # TODO: Look into itertools.combinations_with_replacement
    global RR_ITERATORS
    RR_ITERATORS = cluster.get_iterators()

    request_spawner = "ilb-request-spawner"
    request_spawner_tag = request_spawner + ".fifo"

    request_q = sqs.get_queue(request_spawner_tag)

    print("Listening for incoming web requests...")

    to_process = list()

    while (True):
        data = sqs.receive_message(request_q)

        if data:
            for x in data:
                # print(json.loads(x))
                to_process.extend(json.loads(x))

            round_robin(to_process, cluster)
            print("\n")



if __name__ == "__main__":
    main()
