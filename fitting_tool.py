import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score

def linearRegression(x_data, y_data):

    x_measure = x_data.reshape(-1,1)
    y_measure = y_data

    model = LinearRegression()
    model.fit(x_measure, y_measure)

    x_min = 0
    x_max = x_measure.max()+(x_measure.max()*0.1)
    x_fit = np.linspace(x_min,x_max,100).reshape(-1,1)
    y_fit = model.predict(x_fit)
    r2 = r2_score(y_measure, model.predict(x_measure))

    return x_fit, y_fit, model.coef_, model.intercept_, r2

def polynomialRegression(x_data, y_data, Deg):

    # x_measure = x_data.values.reshape(-1,1)
    # y_measure = y_data.values

    x_measure = x_data.reshape(-1,1)
    y_measure = y_data

    poly_features = PolynomialFeatures(degree=Deg, include_bias=False)
    X_poly = poly_features.fit_transform(x_measure)

    model = LinearRegression()
    model.fit(X_poly, y_measure)

    x_min = 0
    x_max = x_measure.max()+(x_measure.max()*0.1)

    x_fit = np.linspace(x_min,x_max,100).reshape(-1,1)
    x_new_fit = poly_features.transform(x_fit)

    y_fit = model.predict(x_new_fit)

    #r2 = r2_score(y_measure, model.predict(x_measure))

    return x_fit, y_fit, model.coef_, model.intercept_

