class PID:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        
        self.prev_error = 0
        self.integral = 0
        
    def update(self, error):
        """
        PID hesaplamasını yapar.
        Input: error (Hedef ile anlık durum arasındaki fark)
        Output: control_variable (Düzeltme miktarı)
        """
        # P (Proportional)
        P = self.Kp * error
        
        # I (Integral)
        self.integral += error
        I = self.Ki * self.integral
        
        # D (Derivative)
        derivative = error - self.prev_error
        D = self.Kd * derivative
        
        # PID Output
        output = P + I + D
        
        # Bir sonraki döngü için hatayı sakla
        self.prev_error = error
        
        return output
    
    def reset(self):
        self.prev_error = 0
        self.integral = 0
