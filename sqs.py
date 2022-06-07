import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
sqs = boto3.resource('sqs')


def get_url(tag):
    prefix = os.environ["SQS_PREFIX"]
    return prefix + os.environ[tag]


def get_queue(name):
    try:
        queue = sqs.get_queue_by_name(QueueName=name)
        logger.info("Got queue '%s' with URL=%s", name, queue.url)
    except ClientError as error:
        logger.info("Couldn't get queue named %s.", name)
        return False
    else:
        return queue


def get_queues(prefix=None):
    if prefix:
        queue_iter = sqs.queues.filter(QueueNamePrefix=prefix)
    else:
        queue_iter = sqs.queues.all()
    queues = list(queue_iter)
    if queues:
        logger.info("Got queues: %s", ', '.join([q.url for q in queues]))
    else:
        logger.warning("No queues found.")
    return queues


def remove_queue(queue):
    """
    Removes an SQS queue. When run against an AWS account, it can take up to
    60 seconds before the queue is actually deleted.

    :param queue: The queue to delete.
    :return: None
    """
    try:
        queue.delete()
        logger.info("Deleted queue with URL=%s.", queue.url)
    except ClientError as error:
        logger.exception("Couldn't delete queue with URL=%s!", queue.url)
        raise error


def delete_message(queue, msg_id, receipt_handle):
    response = queue.delete_messages(
        Entries=[
            {
                'Id': msg_id,
                'ReceiptHandle': receipt_handle
            },
        ]
    )

    return response

def receive_message(queue):
    response = queue.receive_messages(
        MaxNumberOfMessages=10,
        WaitTimeSeconds=3
    )

    data = list()

    for message in response:
        data.append(message.body)

        # It is important to keep in mind that receiving a message from the SQS queue doesn’t automatically delete it
        # TODO: add error handling
        status = delete_message(queue, message.message_id, message.receipt_handle)

    return data
