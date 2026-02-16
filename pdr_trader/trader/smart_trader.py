from __future__ import division
import pandas as pd
import numpy as np
import datetime
import time
import matplotlib.pyplot as plt
import yfinance as yf

import keras
from keras.models import Sequential
from keras.layers import Dense,Dropout,BatchNormalization,Conv1D,Flatten,MaxPooling1D,LSTM
from keras.callbacks import EarlyStopping,ModelCheckpoint,TensorBoard
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from pandas_datareader import data as pdr


def main():

    end_date = datetime.datetime(2011, 3, 31)
    start_date = datetime.datetime(1973, 1, 1)
    yf.pdr_override()
    df = pdr.get_data_yahoo('^GSPC', start=start_date, end=end_date)
    df.drop("Adj Close",axis=1,inplace=True)
    dfm=df.resample("M").mean()
    dfm=dfm[:-1] # As we said, we do not consider the month of end_date
    print(df.head())
    print(df.tail())

    start_year = start_date.year
    start_month = start_date.month
    end_year = end_date.year
    end_month = end_date.month
  
    first_days = []
    mask = (df.index.month == 1) & (df.index.year == 1973)
    print(df.index[mask])

    for month in range(start_month, 13):
        month_str = f"{month:02d}"  # Format month with leading zero if needed
        mask = (df.index.month == month) & (df.index.year == start_year)
        first_days.append(min(df.index[mask]))

    # Other years
    for year in range(start_year + 1, end_year):
        for month in range(1, 13):
            month_str = f"{month:02d}"  # Format month with leading zero if needed
            mask = (df.index.month == month) & (df.index.year == year)
            first_days.append(min(df.index[mask]))

    # Last year
    for month in range(1, end_month + 1):
        month_str = f"{month:02d}"  # Format month with leading zero if needed
        mask = (df.index.month == month) & (df.index.year == end_year)
        first_days.append(min(df.index[mask]))

    dfm["fd_cm"] = first_days[:-1]
    dfm["fd_nm"] = first_days[1:]
    dfm["fd_cm_open"] = np.array(df.loc[first_days[:-1], "Open"])
    dfm["fd_nm_open"] = np.array(df.loc[first_days[1:], "Open"])
    dfm["rapp"] = dfm["fd_nm_open"].divide(dfm["fd_cm_open"])

    dfm["mv_avg_12"]= dfm["Open"].rolling(window=12).mean().shift(1)
    dfm["mv_avg_24"]= dfm["Open"].rolling(window=24).mean().shift(1)

    dfm=dfm.iloc[24:,:] # WARNING: DO IT JUST ONE TIME!
    execute(dfm)
    print(dfm.index)

    print(dfm.head())
    print(dfm.tail())

def create_window(data, window_size = 1):   

    data_s = data.copy()
    for i in range(window_size):
        data = pd.concat([data, data_s.shift(-(i + 1))], axis = 1)
        
    data.dropna(axis=0, inplace=True)
    return(data)

def model_lstm(window,features):  

    model=Sequential()
    model.add(LSTM(300, input_shape = (window,features), return_sequences=True))
    model.add(Dropout(0.5))
    model.add(LSTM(200, input_shape=(window,features), return_sequences=False))
    model.add(Dropout(0.5))
    model.add(Dense(100,kernel_initializer='uniform',activation='relu'))        
    model.add(Dense(1,kernel_initializer='uniform',activation='relu'))
    model.compile(loss='mse',optimizer='adam')
    return model

def execute(dfm: pd.DataFrame):

    scaler=MinMaxScaler(feature_range=(0,1))
    dg=pd.DataFrame(scaler.fit_transform(dfm[["High","Low","Open","Close","Volume","fd_cm_open",\
                                              "mv_avg_12","mv_avg_24","fd_nm_open"]].values))
    dg0=dg[[0,1,2,3,4,5,6,7]]


    window=4
    dfw=create_window(dg0,window)

    X_dfw=np.reshape(dfw.values,(dfw.shape[0],window+1,8))
    print(X_dfw.shape)
    print(dfw.iloc[:4,:])
    print(X_dfw[0,:,:])

    y_dfw=np.array(dg[8][window:])
    mtest=72


    X_trainw=X_dfw[:-mtest-1,:,:]
    X_testw=X_dfw[-mtest-1:,:,:]
    y_trainw=y_dfw[:-mtest-1]
    y_testw=y_dfw[-mtest-1:]


    model=model_lstm(window+1,8)
    history=model.fit(X_trainw,y_trainw,epochs=500, batch_size=24, validation_data=(X_testw, y_testw), \
                      verbose=0, callbacks=[],shuffle=False)

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper right')
    plt.show()

if __name__ == "__main__":
    main()