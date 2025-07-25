import math
import numpy as np
import random

class Value():
    def __init__(self,data,child=(),op='',label=''):
        self.data=data
        self._op=op
        self._prev=set(child)
        self.label=label
        self.grad=0.0
        self._backward=lambda:None
    
    def __repr__(self):
        return f"Value(data={self.data})"
    
    def __add__(self,other):
        other=other if isinstance(other,Value) else Value(other)
        out=Value(self.data+other.data,(self,other),op='+')
        def _backward():
            self.grad+=1.0*out.grad
            other.grad+=1.0*out.grad
        out._backward=_backward
        return out
    
    def __mul__(self,other):
        other=other if isinstance(other,Value) else Value(other)
        out=Value(self.data*other.data,(self,other),op='*')
        def _backward():
            self.grad+=out.grad*other.data
            other.grad+=out.grad*self.data
        out._backward=_backward
        return out
    
    def __pow__(self,other):
        assert isinstance(other,(int,float)),"self**other: invalid other"
        out=Value(self.data**other,(self,))

        def _backward():
            self.grad+=other*(self.data**(other-1))*out.grad
        out._backward=_backward
        return out
    
    def __rmul__(self,other):
        return self*other
    
    def __truediv__(self,other):
        return self*other**-1
    
    def __sub__(self,other):
        return self+(-other)
    
    def __neg__(self):
        return self*-1
    
    def __radd__(self,other):
        return self+other
    
    def tanh(self):
        x=self.data
        t=(math.exp(2*x)-1)/(math.exp(2*x)+1)
        out=Value(t,(self,),"tanh")

        def _backward():
            self.grad+=(1-t**2)*out.grad
        out._backward=_backward
        return out
    
    def exp(self):
        x=self.data
        out=Value(math.exp(x),(self,),"exp")
        def _backward():
            self.grad+=out.data*out.grad
        out._backward=_backward
        return out
    
    def backward(self):
        visited=set()
        topo=[]
        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)
        build_topo(self)
        self.grad=1.0
        for ver in reversed(topo):
            ver._backward()

class Neuron():
    def __init__(self,nin):
        self.w=[Value(random.uniform(-1,1)) for _ in range(nin)]
        self.b=Value(random.uniform(-1,1))

    def __call__(self,x):
        out=sum((wi*xi for wi,xi in zip(self.w,x)),self.b)
        return out.tanh()
    
    def parameters(self):
        return self.w+[self.b]
    
class Layer():
    def __init__(self,nin,nout):
        self.neurons=[Neuron(nin) for _ in range(nout)]

    def __call__(self,x):
        out=[n(x) for n in self.neurons]
        return out[0] if len(out)==1 else out
    
    def parameters(self):
        return [p for ne in self.neurons for p in ne.parameters()]
    
class MLP():
    def __init__(self,nin,nouts):
        sz=[nin]+nouts
        self.layers=[Layer(n_in,n_out) for n_in,n_out in zip(sz,sz[1:])]

    def __call__(self,x):
        for layer in self.layers:
            x=layer(x)
        return x
    
    def parameters(self):
        return [p for l in self.layers for p in l.parameters()]
    
# n = MLP(3, [4, 4, 1])
# xs = [
#   [2.0, 3.0, -1.0],
#   [3.0, -1.0, 0.5],
#   [0.5, 1.0, 1.0],
#   [1.0, 1.0, -1.0],
# ]
# ys = [1.0, -1.0, -1.0, 1.0] # desired targets
# for k in range(20):
  
#   # forward pass
#   ypred = [n(x) for x in xs]
#   loss = sum((yout - ygt)**2 for ygt, yout in zip(ys, ypred))
  
#   # backward pass
#   for p in n.parameters():
#     p.grad = 0.0
#   loss.backward()
  
#   # update
#   for p in n.parameters():
#     p.data += -0.1 * p.grad
  
#   print(k, loss.data)
  