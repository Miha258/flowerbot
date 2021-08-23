



class Clock:

  __DAY = 86400
  def __init__(self,secs:int):
      self.__secs = secs % self.__DAY

  def get_time(self):
      s = self.__secs % 60
      m = (self.__secs // 60) % 60
      h = (self.__secs // 3600) % 24
      return h,m,s



