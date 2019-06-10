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
      self._lock = threading.Lock()
      self._responses = []

  def __iter__(self):
      return self

  def _next(self):
      # some logic that depends upon what responses have been seen
      # before returning the next request message
      # with selsdelFunc resp: ', resp)
      print("_next")

      
      while True:
        with self._lock:
          if len(self._responses) > 0:
            print("Sending something...")
            response = self._responses.pop(0)
            # actions = [collective_pb2.Action(id="0", action=0, direction=0)]
            # actionPacket = collective_pb2.ActionPacket(actions=actions)
            return response
          else:
            # print("Nothing here, waiting...")
            time.sleep(0.01)

      # actions = [collective_pb2.Action(id="0", action=0, direction=0)]
      # actionPacket = collective_pb2.ActionPacket(actions=actions)
      # return actionPacket
      # print(self._modelFunc)
      # try:
      #   resp = self._modelFunc('test')
      #   print(resp)
      #   return resp
      # except:
      #   print("There was an error calling the function")
      #   raise Exception('There was an error calling the function')

  def __next__(self):  # Python 3
      return self._next()

  def add_response(self, response):
      print("Adding a response...")
      with self._lock:
        print("Got lock...")
        self._responses.append(response)
        print("Response added!")
  

def connectRemoteModel(secret, modelName, modelFunc, addr=PROD_SERVER_ADDR):
  # Create the stub
  channel = grpc.insecure_channel(addr)
  stub = collective_pb2_grpc.CollectiveStub(channel)
  metadata = [('auth-secret', secret), ('model-name', modelName)]

  requestItt = MySmarterRequestIterator()

  responses = stub.ConnectRemoteModel(requestItt, metadata=metadata)
  t1 = time.time()*1000.0
  try:
      for response in responses:
        t2 = time.time()*1000.0
        diff = t2 - t1
        t1 = t2
        print("Packet delta: ", diff)
        # actionPacket = modelFunc(response)
        actions = [collective_pb2.Action(id="0", action=0, direction=0)]
        actionPacket = collective_pb2.ActionPacket(actions=actions)
        requestItt.add_response(actionPacket)
  #     for obsvPacket in stub.CreateRemoteModel(metadata=metadata):
  #         action = 0
  #         direction = 0
  #         print("Performing action: ", action, " in direction: ", direction)
  #         actionRes = stub.ExecuteAgentAction(v1.ExecuteAgentActionRequest(api=api, id=obsv.entity.id, action=action, direction=direction), metadata=metadata)
  except KeyboardInterrupt:
      responses.cancel()