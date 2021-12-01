from django.shortcuts import render


import json 
import NN
import numpy as np
import pickle
from django.shortcuts import render
import requests

def create(request):
    
    context = {
    }
    return render(request, 'create.html', context)

def train(request, info):

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

    final_X = training_data[:500]
    X = final_X
    y = changes[:500]


    n = 150

    next_index = info.index('~')
    epochs = info[:next_index]
    epochs = int(epochs)
    info = info[next_index + 1:]
    size = info[0]
    size = float(size)
    info = info[1:]
    layer_sizes = []
    while info[:5] == 'layer':
        info = info[5:]
        try:
            next_index = info.index('layer')
            layer_sizes.append(info[:next_index])
            info = info[next_index:]
        except:
            next_index = info.index('~end~')
            layer_sizes.append(info[:next_index])
            info = info[next_index + 5:]
            break
    new_layer_sizes = []
    for i in layer_sizes:
        new_layer_sizes.append(int(i))
    layer_sizes = new_layer_sizes
    info = info[4:]
    next_index = info.index('optimizer')
    loss_type = info[:next_index]
    info = info[next_index:]
    info = info[9:]
    try:
        next_index = info.index('learning_rate')
        optimizer = info[:next_index]
        info = info[next_index:]
        info = info[13:]
        try:
            next_index = info.index('decay')
            learning_rate = float(info[:next_index])
            info = info[next_index:]
            info = info[5:]
            try:
                next_index = info.index('momentum')
                decay = float(info[:next_index])
                info = info[next_index:]
                info = info[8:]
                momentum = float(info)
            except: 
                decay = float(info)
        except: 
            try:
                next_index = info.index('momentum')
                decay = float(info[:next_index])
                info = info[next_index:]
                info = info[8:]
                momentum = float(info)
            except: 
                decay = float(info)
    except:
        try:
            next_index = info.index('decay')
            learning_rate = float(info[:next_index])
            info = info[next_index:]
            info = info[5:]
            try:
                next_index = info.index('momentum')
                decay = float(info[:next_index])
                info = info[next_index:]
                info = info[8:]
                momentum = float(info)
            except: 
                pass
        except: 
            try:
                next_index = info.index('momentum')
                decay = float(info[:next_index])
                info = info[next_index:]
                info = info[8:]
                momentum = float(info)
            except: 
                decay = float(info)

    params = {
        'size': size,
        'layer_sizes': layer_sizes,
        'loss_type': loss_type,
        'optimizer': optimizer,
        'epochs': epochs
    }

    try:
        params['learning_rate'] = learning_rate
    except:
        pass

    try:
        params['decay'] = decay
    except: 
        pass

    try:
        params['momentum'] = momentum
    except:
        pass

    model = NN.Model()
    
    model.add(NN.Layer_Dense(14, params['layer_sizes'][0]))
    model.add(NN.Activation_ReLU())

    for i in range(1, len(params['layer_sizes'])):
        model.add(NN.Layer_Dense(params['layer_sizes'][i-1], params['layer_sizes'][i]))
        model.add(NN.Activation_ReLU())

    model.add(NN.Layer_Dense(params['layer_sizes'][-1], 1))
    model.add(NN.Activation_Linear())

    if params['loss_type'] == 'LAM':
        loss_function = NN.Loss_MeanAbsoluteError()
    else:
        loss_function = NN.Loss_MeanSquaredError()

    if params['optimizer'] == 'ADAM':
        optimizer_function = NN.Optimizer_Adam(
            learning_rate=params['learning_rate'], 
            decay=params['decay'])
    elif params['optimizer'] == 'RMSPROP':
        optimizer_function = NN.Optimizer_RMSprop(
            learning_rate=params['learning_rate'], 
            decay=params['decay'], 
            epsilon=1e-7,
            rho=0.9)
    elif params['optimizer'] == 'ADAGRAD':
        optimizer_function = NN.Optimizer_Adagrad(
            learning_rate=params['learning_rate'], 
            decay=params['decay'], 
            epsilon=1e-7)
    elif params['optimizer'] == 'SGD':
        optimizer_function = NN.Optimizer_SGD(
            learning_rate=params['learning_rate'], 
            decay=params['decay'], 
            momentum=params['momentum'])

    model.set(
        Loss=loss_function,
        optimizer=optimizer_function,
        accuracy=NN.Accuracy_Regression()
    )

    model.finalize()


    model.train(X, y, epochs=params['epochs'], print_every=100)
    '''model.save_parameters('parameters.txt')

    model.load_parameters('parameters.txt')'''

    X = training_data[500:]
    y = changes[500:]

    outputs = model.forward(X)

    correct = 0.
    total = 0.

    for pred_y, act_y in zip(outputs, y):
        total += 1
        if pred_y > 0:
            if act_y > 0:
                correct += 1
        if pred_y < 0:
            if act_y < 0:
                correct += 1


    if correct == 0:
        tell_one = "There seems to be something wrong. Tweak your parameters and try again!"
        tell_two = ""
    else:
        percentage = correct / total 

        tell_one = f'The model was correct {percentage * 100:.3f}% of the time'
        tell_two = f'The model guessed correct {correct} out of {total} attempts'

    context = {
        "info": info,
        "params": params,
        "statement_one": tell_one,
        "statement_two": tell_two
    }
    return render(request, 'train.html', context)


