
import json 
import NN
import numpy as np
import pickle
from django.shortcuts import render
import requests

def predictions(request):
    

    f = open('training_data.txt', 'r')
    data = f.read()
    data = json.loads(data)
    training_data = []
    changes = []
    for i in data:
        training_data.append(np.array(data[i]['si']))
        li = []
        li.append(data[i]['day_change'])
        li = np.array(li)
        changes.append(li)



    training_data = np.array(training_data)
    changes = np.array(changes)
    maxes = []
    for i in range(len(training_data[0])):
        max = -float('inf')
        for set in training_data:
            if abs(set[i]) > max:
                max = abs(set[i])
        for set in training_data:
            set[i] /= max
        total = 0.
        count = 0.
        for set in training_data:
            if set[i] != 0:
                total += set[i]
                count += 1.
        average = total / count
        for set in training_data:
            if set[i] == 0:
                set[i] = average
        maxes.append(max)
    for set in changes:
        set[0] *= 100
    X = training_data[:500]
    y = changes[:500]
    n = 300

    model = NN.Model()
    model.add(NN.Layer_Dense(14, n))
    model.add(NN.Activation_ReLU())
    model.add(NN.Layer_Dense(n, n))
    model.add(NN.Activation_ReLU())
    model.add(NN.Layer_Dense(n, n))
    model.add(NN.Activation_ReLU())
    model.add(NN.Layer_Dense(n, n))
    model.add(NN.Activation_ReLU())
    model.add(NN.Layer_Dense(n, n))
    model.add(NN.Activation_ReLU())
    model.add(NN.Layer_Dense(n, 1))
    model.add(NN.Activation_Linear())


    model.set(
        Loss=NN.Loss_MeanSquaredError(),
        optimizer=NN.Optimizer_Adam(learning_rate=.0001, decay=.00001),
        accuracy=NN.Accuracy_Regression()
    )

    model.finalize()
    model.load_parameters('parameters.txt')

    X = training_data

    output = model.forward(X)

    best = []

    for j in range(10):
        max = -float('inf')
        loc = -1
        for i in range(len(output)):
            if i in best:
                continue
            else:
                if output[i][0] > max:
                    max = output[i][0]
                    loc = i
        best.append(loc)

    best_tickers = []


    for j in best:  
        for index, i in enumerate(data):
            if index == j:
                ti = i 
                tiurl = f'https://api.polygon.io/v1/meta/symbols/{i}/company?apiKey=2ckUQrRRwUoyMS6pdg5LlYxLIIe75den'
                # tir = requests.get(tiurl)
                tidata = data[i]
                tidict = {
                    'ticker': ti,
                    #'name': tidata['name'],
                    'name': 'test',
                    # 'sector': tidata['sector'],
                    'sector' : 'sector',
                    # 'logo': tidata['logo'],
                    'logo' : 'logo',
                    # 'industry': tidata['industry'],
                    'industry' : 'industry',
                    # 'ceo': tidata['ceo']
                    'ceo' : 'ceo',
                }
                best_tickers.append(tidict)




    context = {
        'best': best_tickers,
    }
    return render(request, 'predictions.html', context)

