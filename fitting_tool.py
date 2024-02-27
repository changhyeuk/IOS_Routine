import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score

def linearFit(x_data, y_data):

    x_measure = x_data.values.reshape(-1,1)
    y_measure = y_data.values

    model = LinearRegression()
    model.fit(x_measure, y_measure)

    x_min = 0
    x_max = x_measure.max()+(x_measure.max()*0.1)
    x_fit = np.linspace(x_min,x_max,100).reshape(-1,1)
    y_fit = model.predict(x_fit)
    r2 = r2_score(y_measure, model.predict(x_measure))

    return x_fit, y_fit, model.coef_, model.intercept_, r2