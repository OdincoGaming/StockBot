import keras
import tensorflow as tf
from keras.models import Model, load_model
from keras.callbacks import ModelCheckpoint
from keras.layers import Dense, Dropout, LSTM, Input, Activation, concatenate
from keras import optimizers
import numpy as np
#np.random.seed(4)
#tf.random.set_seed(4)
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import preprocessing
import os

# dataset
history = 30
checkpoints = []
############################################################################################################################################################################################
############################################################################################################################################################################################
def csv_to_dataset(csv_path):
    data = pd.read_csv(csv_path)
    data = data.drop('date', axis=1)
    data = data.drop(0, axis=0)

    data = data.values

    data_normaliser = preprocessing.MinMaxScaler()
    data_normalised = data_normaliser.fit_transform(data)

    # using the last {history} open close high low volume data points, predict the next open value
    ohlcv_norm = np.array([data_normalised[i:i + history].copy() for i in range(len(data_normalised) - history)])
    ndo_norm = np.array([data_normalised[:, 0][i + history].copy() for i in range(len(data_normalised) - history)])
    ndo_norm = np.expand_dims(ndo_norm, -1)

    ndo = np.array([data[:, 0][i + history].copy() for i in range(len(data) - history)])
    ndo = np.expand_dims(ndo, -1)

    y_normaliser = preprocessing.MinMaxScaler()

    y_normaliser.fit(ndo)

    tech_ind = []
    for his in ohlcv_norm:
        # note since we are using his[3] we are taking the SMA of the closing price
        sma = np.mean(his[:, 3])
        tech_ind.append(np.array([sma]))

    tech_ind = np.array(tech_ind)

    tech_ind_scaler = preprocessing.MinMaxScaler()
    tech_ind_norm = tech_ind_scaler.fit_transform(tech_ind)
        
    assert ohlcv_norm.shape[0] == ndo_norm.shape[0] == tech_ind_norm.shape[0]
    return ohlcv_norm, tech_ind_norm, ndo_norm, ndo, y_normaliser
#############################################################################################################################################################################################
#############################################################################################################################################################################################

def check_for_model():
    path = os.getcwd() + "\\data\\model"
    for file_path in list(filter(lambda x: x.endswith('model.h5f'), os.listdir(path))):
        if file_path == 'base_model.h5':
            return True
        else:
            return False

def csv_to_model(file):
###################################################################################
    #dataset
    path = os.getcwd() + "\\data\\csv\\" + file
    ohlcv_histories, tech_ind, ndo, unscaled_y, y_normaliser = csv_to_dataset(path)

    test_split = 0.9
    n = int(ohlcv_histories.shape[0] * test_split)

    ohlcv_train = ohlcv_histories[:n]
    tech_ind_train = tech_ind[:n]
    y_train = ndo[:n]

    ohlcv_test = ohlcv_histories[n:]
    tech_ind_test = tech_ind[n:]
    y_test = ndo[n:]

    unscaled_y_test = unscaled_y[n:]

    print(ohlcv_train.shape)
    print(ohlcv_test.shape)
###################################################################################
    # model architecture
    # define two sets of inputs
    lstm_input = Input(shape=(history, 5), name='lstm_input')
    dense_input = Input(shape=(tech_ind.shape[1],), name='tech_input')

    # the first branch operates on the first input
    x = LSTM(50, name='lstm_0')(lstm_input)
    x = Dropout(0.2, name='lstm_dropout_0')(x)
    lstm_branch = Model(inputs=lstm_input, outputs=x)

    # the second branch opreates on the second input
    y = Dense(20, name='tech_dense_0')(dense_input)
    y = Activation("relu", name='tech_relu_0')(y)
    y = Dropout(0.2, name='tech_dropout_0')(y)
    technical_indicators_branch = Model(inputs=dense_input, outputs=y)

    # combine the output of the two branches
    combined = concatenate([lstm_branch.output, technical_indicators_branch.output], name='concatenate')

    z = Dense(64, activation="sigmoid", name='dense_pooling')(combined)
    z = Dense(1, activation="linear", name='dense_out')(z)
###################################################################################
    # create model
    # our model will accept the inputs of the two branches and
    # then output a single value
    basemodelcheck = check_for_model()
    if basemodelcheck:

       # train the network
        print("[INFO] retrieving base model...")
        path = os.getcwd() + "\\data\\model\\base_model.h5"
        model = load_model(path)
        adam = optimizers.Adam(lr=0.0005)
        model.compile(optimizer=adam, loss='mse')
        path = os.getcwd() + "\\data\\model\\checkpoint\\checkpoint.ckpt"
        checkpoint = ModelCheckpoint(path, monitor='val_acc', verbose=1, save_best_only=True, save_weights_only=False, mode='auto')
        checkpoints = [checkpoint]
        model.fit(x=[ohlcv_train, tech_ind_train], y=y_train, batch_size=32, epochs=50, shuffle=True, validation_split=0.1)
        path = os.getcwd() + "\\data\\model\\model_weights.h5"
        model.save_weights(path)

        # evaluation

        y_test_predicted = model.predict([ohlcv_test, tech_ind_test])
        y_test_predicted = y_normaliser.inverse_transform(y_test_predicted)
        y_predicted = model.predict([ohlcv_histories, tech_ind])
        y_predicted = y_normaliser.inverse_transform(y_predicted)
        assert unscaled_y_test.shape == y_test_predicted.shape
        real_mse = np.mean(np.square(unscaled_y_test - y_test_predicted))
        scaled_mse = real_mse / (np.max(unscaled_y_test) - np.min(unscaled_y_test)) * 100
        print(scaled_mse)

        plt.gcf().set_size_inches(22, 15, forward=True)
        start = 0
        end = -1
        real = plt.plot(unscaled_y_test[start:end], label='real')
        pred = plt.plot(y_test_predicted[start:end], label='predicted')

        plt.legend(['Real', 'Predicted'])
        plt.show()
        path = os.getcwd() + "\\data\\model\\base_model.h5"
        model.save(path)
###################################################################################
    else:
        model = Model(inputs=[lstm_branch.input, technical_indicators_branch.input], outputs=z)
        adam = optimizers.Adam(lr=0.0005)
        model.compile(optimizer=adam, loss='mse')

        path = os.getcwd() + "\\data\\model\\checkpoint\\checkpoint.ckpt"
        checkpoint = tf.keras.callbacks.ModelCheckpoint(path, monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=False, mode='min', save_freq='epoch')
        checkpoints = [checkpoint]
        model.fit(x=[ohlcv_train, tech_ind_train], y=y_train, batch_size=32, epochs=50, shuffle=True, validation_split=0.1, callbacks=checkpoints)

        # evaluation
        y_test_predicted = model.predict([ohlcv_test, tech_ind_test])
        y_test_predicted = y_normaliser.inverse_transform(y_test_predicted)
        y_predicted = model.predict([ohlcv_histories, tech_ind])
        y_predicted = y_normaliser.inverse_transform(y_predicted)
        assert unscaled_y_test.shape == y_test_predicted.shape
        real_mse = np.mean(np.square(unscaled_y_test - y_test_predicted))
        scaled_mse = real_mse / (np.max(unscaled_y_test) - np.min(unscaled_y_test)) * 100
        print(scaled_mse)

        plt.gcf().set_size_inches(22, 15, forward=True)
        start = 0
        end = -1
        real = plt.plot(unscaled_y_test[start:end], label='real')
        pred = plt.plot(y_test_predicted[start:end], label='predicted')

        plt.legend(['Real', 'Predicted'])
        plt.show()
        path = os.getcwd() + "\\data\\model\\base_model.h5"
        model.save(path)