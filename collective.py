import threading
import grpc
import sys
import time
sys.path.insert(0, './api')
import collective_pb2
import collective_pb2_grpc


PROD_SERVER_ADDR = "" # TODO

def defaultModelFunc(obsv):
  raise Exception('You need to pass in a model function.')

# Create an iterator to let us send a stream
class MySmarterRequestIterator(object):
  def __init__(self):
      self._request = None

  def __iter__(self):
      return self

  def _next(self):
    # Block until we get the lock, then return the request
    self._lock.acquire()
    return self._request

  def __next__(self):  # Python 3
    return self._next()

  def set_request(self, request):
    self._request = request

  def set_lock(self, lock):
    self._lock = lock
  

def connectRemoteModel(secret, modelFunc, addr=PROD_SERVER_ADDR):
  # Create the stub
  channel = grpc.insecure_channel(addr)
  stub = collective_pb2_grpc.CollectiveStub(channel)
  metadata = [('model-secret', secret)]
  # Create and acquire the lock
  lock = threading.Lock()
  lock.acquire()
  # Create the iterator
  requestItt = MySmarterRequestIterator()
  requestItt.set_lock(lock)
  # Connect
  responses = stub.ConnectRemoteModel(requestItt, metadata=metadata)
  # Try/catch cleanup for Notebook
  try:
      for response in responses:
        # Create the request
        actions = []
        for obsv in response.observations:
          actions.append(modelFunc(obsv))
        actionPacket = collective_pb2.ActionPacket(actions=actions)
        # Set the request to the iterator
        requestItt.set_request(actionPacket)
        # Release lock so the iterator can make a passthrough
        lock.release()
  except KeyboardInterrupt:
    # Release lock
    lock.release()
    # Send cancel to the server
    responses.cancel()

def createAction(id, action, direction):
  return collective_pb2.Action(id=id, action=action, direction=direction)