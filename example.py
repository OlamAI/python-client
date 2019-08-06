import random
from terrariumai import connectRemoteModel, createAction

def randomAction():
    return random.randint(0, 1)
def randomDirection():
    return random.randint(0, 3)

def modelFunc(obsv):
  if obsv.isAlive:
    action = createAction(obsv.id, randomAction(), randomDirection())
    print("Alive: ", obsv.isAlive)
    print("Cells: ", obsv.cells)
    print(obsv)
    print("--------------------")
    return action
  if not obsv.isAlive:
    print("Entity died :(")

# Prod
connectRemoteModel(
    secret='6090b011-3ab8-421f-a2a5-9fad27553237', 
    modelFunc=modelFunc, 
    addr='collective.terrarium.ai:9090'
)

# # Training
# connectRemoteModel(
#     secret='', 
#     modelFunc=modelFunc, 
#     addr='127.0.0.1:9090'
# )