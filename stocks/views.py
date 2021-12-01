from os import error
from django.shortcuts import render
from numpy.lib.function_base import percentile
import requests
import NN
import numpy as np
import pickle



def stocks(request):
    context = {

    };
    print(request)
    if request.GET:
        api_key = '&apiKey=2ckUQrRRwUoyMS6pdg5LlYxLIIe75den'
        specific = f"https://api.polygon.io/vX/reference/financials?ticker={request.GET['ticker'].upper()}" + api_key
        r = requests.get(specific)
        cont_data = r.json()

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

        specific = f"https://api.polygon.io/vX/reference/financials?ticker={request.GET['ticker'].upper()}" + api_key
        r = requests.get(specific)
        data = r.json()

        if data['results']:
            data = data['results'][0]

            si = [] 
            try:
                si.append(data['financials']['balance_sheet']['assets']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['balance_sheet']['equity']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['balance_sheet']['liabilities']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['cash_flow_statement']['exchange_gains_losses']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['cash_flow_statement']['net_cash_flow']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['cash_flow_statement']['net_cash_flow_from_financing_activities']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['comprehensive_income']['comprehensive_income_loss']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['comprehensive_income']['comprehensive_income_loss_attributable_to_parent']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['comprehensive_income']['other_comprehensive_income_loss']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['income_statement']['basic_earnings_per_share']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['income_statement']['cost_of_revenue']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['income_statement']['gross_profit']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['income_statement']['operating_expenses']['value'])
            except:
                si.append(0)
            try:
                si.append(data['financials']['income_statement']['revenues']['value'])
            except:
                si.append(0)

            with open('maxes.txt', 'rb') as f:
                maxes = pickle.load(f)

            for i in range(14):
                si[i] /= maxes[i]

            si = np.array(si)
            
            output = model.forward(si)

            with open('percentiles.txt', 'rb') as f:
                percentiles = pickle.load(f)

            if output < 0:
                percentile = 'dont buy'
            elif output > percentiles[9]:
                percentile = 10
            else:
                for i in range(9):
                    if output > percentiles[i] and output < percentiles[i + 1]:
                        percentile = i + 1
        else:
            percentile = "None"

        ti = request.GET['ticker'].upper()
        tiurl = f"https://api.polygon.io/v1/meta/symbols/{ti}/company?apiKey=2ckUQrRRwUoyMS6pdg5LlYxLIIe75den"
        tir = requests.get(tiurl)
        tidata = tir.json()

        try:
            info_sentence = ""
            if tidata['ceo']:
                info_sentence += f"{tidata['name']}'s CEO is {tidata['ceo']}. "
            if tidata['sector'] and tidata['industry']:
                info_sentence += f"{tidata['name']} is in the {tidata['industry']} of the {tidata['sector']}. "

            location = f"{tidata['name']} is based out of {tidata['hq_state']}, {tidata['hq_country']}"


            similar = tidata['similar']
            if len(similar) > 10:
                similar = similar[:10]

            tidict = {
                'name': tidata['name'],
                'sentence': info_sentence,
                'description': tidata['description'],
                'logo': tidata['logo'],
                'similar': similar,
                'location': location,
            }

            nurl = f"https://api.polygon.io/v2/reference/news?ticker={ti}&apiKey=2ckUQrRRwUoyMS6pdg5LlYxLIIe75den"
            nir = requests.get(nurl)
            ndata = nir.json()
            ndata = ndata["results"]
            news = []
            for index, item in enumerate(ndata):
                if index >= 4:
                    break
                news_specific = {
                    'title': item['title'],
                    'url': item['article_url'],
                }
                news.append(news_specific)

            if percentile == 'dont buy':
                prediction = 'Our system expects this stock to go down, this is a sell'
            elif percentile == 'None': 
                prediction = "We can't seem to find any financial data for this stock"
            elif percentile > 0 and percentile < 5:
                prediction = f'Our system has scored this stock a {percentile}/10, this is a weak buy'
            elif percentile >= 5 and percentile <= 8:
                prediction = f'Our system has scored this stock a {percentile}/10, this is a medium buy'
            else:
                prediction = f'Our system has scored this stock a {percentile}/10, this is a strong buy'

            if cont_data["results"]:
                my_data = cont_data["results"][0]
            else:
                my_data = []

            context = {
                "data": my_data,
                "pred": prediction,
                "info": tidict,
                "news": news
            }
            return render(request, 'stock_detail.html', context)
        except:
            return render(request, 'not_found.html', {})
    return render(request, 'stocks.html', context)

def stock_detail(request, ticker):
    api_key = '&apiKey=2ckUQrRRwUoyMS6pdg5LlYxLIIe75den'
    specific = f'https://api.polygon.io/vX/reference/financials?ticker={ticker.upper()}' + api_key
    r = requests.get(specific)
    cont_data = r.json()

    n = 150

    model = NN.Model()
    model.add(NN.Layer_Dense(14, n))
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

    specific = f'https://api.polygon.io/vX/reference/financials?ticker={ticker.upper()}' + api_key
    r = requests.get(specific)
    data = r.json()

    data = data['results'][0]

    si = [] 
    try:
        si.append(data['financials']['balance_sheet']['assets']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['balance_sheet']['equity']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['balance_sheet']['liabilities']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['cash_flow_statement']['exchange_gains_losses']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['cash_flow_statement']['net_cash_flow']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['cash_flow_statement']['net_cash_flow_from_financing_activities']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['comprehensive_income']['comprehensive_income_loss']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['comprehensive_income']['comprehensive_income_loss_attributable_to_parent']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['comprehensive_income']['other_comprehensive_income_loss']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['income_statement']['basic_earnings_per_share']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['income_statement']['cost_of_revenue']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['income_statement']['gross_profit']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['income_statement']['operating_expenses']['value'])
    except:
        si.append(0)
    try:
        si.append(data['financials']['income_statement']['revenues']['value'])
    except:
        si.append(0)

    with open('maxes.txt', 'rb') as f:
        maxes = pickle.load(f)

    for i in range(14):
        si[i] /= maxes[i]

    si = np.array(si)
    
    output = model.forward(si)

    with open('percentiles.txt', 'rb') as f:
        percentiles = pickle.load(f)


    if output < 0:
        p = 'dont buy'
    elif output > percentiles[9]:
        percentile = 10
    else:
        for i in range(9):
            if output > percentiles[i] and output < percentiles[i + 1]:
                percentile = i + 1

    context = {
        "data": cont_data["results"][0],
        "pred": percentile
    }
    return render(request, 'stock_detail.html', context)