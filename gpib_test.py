import visa
import gpib

rm = visa.ResourceManager('@py')
res = rm.list_resources()
print res

inst = rm.open_resource(res[1])
print(inst.query("*IDN?"))
