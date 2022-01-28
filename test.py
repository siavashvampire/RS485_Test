import math

data = [22, 257, 4667, 32000]
data = [17, 1548, 10257, 33]
print(data)
Year = 2000 + data[0]
num2 = format(data[1], "b")
Day = int(num2[-5:], 2)
month = int(num2[-12:-8], 2)

num3 = format(data[2], "b")
minute = int(num3[-6:], 2)
Hour = int(num3[-13:-8], 2)

Milis = int(data[3])
second = int(Milis / 1000)

asd = "{Year}-{Month}-{Day} {Hour}:{Minute}:{Second}".format(Year=Year, Month=month, Day=Day, Hour=Hour, Minute=minute,
                                                             Second=second)

print(asd)

# 2022-01-28 17:29:28
