import pickle
import argparse
import matplotlib.pyplot as plt


def read_file(file_path):
  history = load_history(file_path)  

  keys = []
  val_keys = []

  for key in history.keys():
    if 'val' in key:
      val_keys.append(key)
    else:
      keys.append(key)

  while True:
    if openDialog((keys, val_keys), history) == False:
      break

def selectFromList(lst):
  error = True

  for i, key in enumerate(lst): 
    print('\t{} {}'.format(i,key))
    
  while error:
    try:

      index = int(input('\tIndex:'))
      if(index < 0): return None
      return lst[index]
    except:
      pass
def openDialog(keys, history):

  print('TrainData:')
  train = selectFromList(keys[0])
  if train == None:
    return False
  
  print('ValidationData:')
  validation = selectFromList(keys[1])
  if validation == None:
    return False

  title = input('Title: ')

  plot_history_charts(title, history[train], history[validation])

  return True

def plot_history_charts(title, data, val_data):
  l1, = plt.plot(data, label='Train')
  l2, = plt.plot(val_data, label="Validation")
  plt.ylabel(title)
  plt.legend(handles=[l1, l2])
  plt.show()

def load_history(file_path):
  obj = None
  with open(file_path, 'rb') as file:
    obj = pickle.load(file)

  return obj

def arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument('file')

  return parser.parse_args()

def main():
  args = arguments()
  read_file(args.file)


if __name__ == "__main__":
    main()