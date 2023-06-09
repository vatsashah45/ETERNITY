from FunctionBase import FunctionBase
from CalculationErrorException import CalculationErrorException


class FunctionMAD(FunctionBase):
    '''Class used to calculate the Mean Average Deviation function.'''

    def __init__(self, arguments: list) -> None:
        '''Constructor.'''
        super(FunctionMAD, self).__init__()
        self.arguments = arguments

    def calculateEquation(self) -> float:
        '''
            Function used to calculate the Mean Absolute Deviation of the input values.
            Returns MAD(self.arguments)
        '''
        # Calculate the mean of inputs
        mean = 0
        for i in self.arguments:
            mean += i
        mean = mean/len(self.arguments)

        deviation = 0

        # Calculate deviation
        for i in self.arguments:
            sum = i - mean
            if sum < 0:
                sum = -sum
            deviation += sum

        return self.truncate(deviation / len(self.arguments), self.ROUNDING)
