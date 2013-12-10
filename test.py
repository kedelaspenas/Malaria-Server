import re
a = '(123,223)(312,212)(42,23)'

b = [i for i in re.findall('[0-9]+,[0-9]+', a).split(',',i)]
print b

