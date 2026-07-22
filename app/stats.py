import math
from numba import njit


@njit
def category_stats(prices, type_ids):
    n = len(type_ids)
    if n == 0:
        return 0.0, 0.0, 0.0, 0.0

    max_val = -math.inf
    min_val = math.inf
    suma = 0.0

    # Primer ciclo: Máximo, mínimo y suma (ignorando nulos por seguridad)
    for i in type_ids:
        precio = prices[i]
        if math.isnan(precio):
            continue
        if precio > max_val:
            max_val = precio
        if precio < min_val:
            min_val = precio
        suma += precio

    mean_val = suma / n if n > 0 else 0.0

    # Segundo ciclo: Desviación estándar muestral
    suma_cuadrados = 0.0
    for i in type_ids:
        precio = prices[i]
        if math.isnan(precio):
            continue
        suma_cuadrados += (precio - mean_val) ** 2

    if n > 1:
        desviacion = math.sqrt(suma_cuadrados / (n - 1))
    else:
        desviacion = 0.0

    return max_val, min_val, mean_val, desviacion