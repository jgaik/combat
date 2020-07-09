import os

if __name__ == "__main__":
  path = os.getcwd() + os.sep + "random"
  for name in range(3):
    os.mkdir(path + os.sep + str(name))
    for id in range(10):
      with open(path + os.sep + str(name) + os.sep + str(id) + ".txt", "x"):
        pass