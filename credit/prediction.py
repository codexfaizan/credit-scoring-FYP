import numpy as np
import joblib 


def prediction(input):
  
    #array = np.array([[data1, data2, data3, data4, data5, data6]])
    model = joblib.load('credit_scoring_model.pkl')
    #input = np.array(input.iloc[0][features])
    input = np.array(input)
    input = input.reshape(1,4)
    prediction = model.predict(input)
    if prediction[0] == 0:
        return "Congratulations! You are eligible for Loan."
    else:
        return "Sorry! You are not eligible for Loan."
