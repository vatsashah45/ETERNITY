from FunctionBase import FunctionBase
import FunctionExponent
from CalculationErrorException import CalculationErrorException

class FunctionCosh(FunctionBase):
    '''Class used to calculate the Cosh function.'''
    
    def __init__(self, num: float) -> None:
        '''Constructor.'''
        super(FunctionCosh, self).__init__()
        self.num = num

    def calculateEquation(self, isDeg:bool = False) -> float:
        '''
            Function used to calculate cosh using exponents.
            Returns sinh(self.num)
        '''

        # If the number is in degrees, convert it to radians
        num = self.num
        if(isDeg):
            num = self.degreeToRadian(num)
            
        # Calculate cosh using (e^x+e^-x)/2 where x is the input
        # https://www.whitman.edu/mathematics/calculus_online/section04.11.html
        num1 = FunctionExponent.FunctionExponent(self.e, num).calculateEquation()
        num2 = FunctionExponent.FunctionExponent(self.e, -num).calculateEquation()
        result = (num1+num2)/2
        
        # Handle exceptions. We don't want a number too large or small
        if(result > self.MAX_RESULT):
            raise CalculationErrorException("MATH ERROR: Result too large")
        elif(result < self.MIN_RESULT):
            raise CalculationErrorException("MATH ERROR: Result too small")      
          
        return self.truncate(result, self.ROUNDING)