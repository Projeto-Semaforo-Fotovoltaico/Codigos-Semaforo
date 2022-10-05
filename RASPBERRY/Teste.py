import numpy as np
import matplotlib.pyplot as plt
import random
from time import sleep

vetorLogico = np.zeros(10)
soma = 0
k = 0

def smooth(val):
    global soma, k, vetorLogico

    soma = soma - vetorLogico[k]
    vetorLogico[k] = val

    soma = soma + vetorLogico[k]
    k = k + 1

    if k == len(vetorLogico):
        k = 0
    
    return soma/vetorLogico.size

