from whatsapp_toolkit import WhatsappClient, send_message

# Ejemplo de uso
telefono_prefijo = "521"
telefono = "4778966517"
tel_completo = telefono_prefijo + telefono
mensaje = """
Hola, este es un mensaje de prueba enviado desde Whatsapp Toolkit.
"""
response = send_message(tel_completo, mensaje, delay=2000)
print(response)