class CalculadoraCerebro:
    def __init__(self):
        # 1. El 'Diccionario': Aquí guardaremos las funciones
        self._operaciones = {}

    def enseñar(self, nombre_operacion: str):
        """
        Este es el DECORADOR.
        Recibe el nombre (ej: "suma") y devuelve el 'sticker' real.
        """
        def sticker(funcion_original):
            # 2. El Momento del Registro:
            # Guardamos la función en el diccionario usando el nombre como llave.
            print(f"💾 Registrando operación: '{nombre_operacion}'...")
            self._operaciones[nombre_operacion] = funcion_original
            
            # 3. El Retorno Limpio:
            # Devolvemos la función TAL CUAL. No la envolvemos, no la cambiamos.
            # Simplemente la dejamos pasar después de anotarla en la lista.
            return funcion_original
        
        return sticker

    def calcular(self, nombre_operacion, a, b):
        # 4. El Uso (Dispatch):
        # Buscamos la función en el diccionario y la ejecutamos.
        funcion = self._operaciones.get(nombre_operacion)
        
        if funcion:
            return funcion(a, b)
        else:
            return "Error: No sé hacer eso"

# --- INSTANCIAMOS EL CEREBRO ---
cerebro = CalculadoraCerebro()

# --- AQUÍ OCURRE LA MAGIA (Tiempo de Carga) ---
# Al poner @cerebro.enseñar, Python ejecuta 'sticker' INMEDIATAMENTE al leer el archivo.

@cerebro.enseñar("suma")
def sumar_numeros(x, y):
    return x + y

@cerebro.enseñar("multiplicacion")
def multiplicar_potente(x, y):
    return x * y

print("\n--- INICIANDO PROGRAMA ---")

# --- TIEMPO DE EJECUCIÓN ---
# El usuario pide "suma". El cerebro busca en su diccionario y encuentra 'sumar_numeros'.
resultado1 = cerebro.calcular("suma", 5, 3)
print(f"Resultado Suma: {resultado1}")  # 8

resultado2 = cerebro.calcular("multiplicacion", 10, 10)
print(f"Resultado Multi: {resultado2}") # 100