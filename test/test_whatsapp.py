from whatsapp_toolkit import send_message

# Ejemplo de uso
telefono_prefijo = "521"
telefono = "4778966517"
tel_completo = telefono_prefijo + telefono
mensaje = """
Hola, este es un mensaje de prueba enviado desde Whatsapp Toolkit.
"""

is_grupo = True

id_grupo = "120363402051212345"


objetiv0 = id_grupo if is_grupo else tel_completo
response = send_message(objetiv0, mensaje, delay_ms=2000)
print(response)