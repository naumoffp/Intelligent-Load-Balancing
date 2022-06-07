import json
import logging
import os

import sqs


def main():
    # server_pool     = sqs.get_url("SERVER_POOL_SQS")
    # load_balancer   = sqs.get_url("LOAD_BALANCER_SQS")
    # request_spawner = sqs.get_url("REQUEST_SPAWNER_SQS")

    server_pool     = "ilb-server-pool"
    load_balancer   = "ilb-load-balancer"

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

            print("-"*10)
            print(to_process)



if __name__ == "__main__":
    main()
