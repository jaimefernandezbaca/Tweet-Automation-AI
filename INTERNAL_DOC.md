Tweet Automation AI – Documentación Interna (Explicada para futuros mantenedores)
Este documento es interno y no debe subirse a GitHub.

1. Qué hace este proyecto (explicación sencilla)

Este proyecto permite programar tweets que se publican automáticamente sin tener que tener abierta ninguna aplicación, ordenador, ni terminal.

El sistema está dividido en tres partes:

Una interfaz (UI) muy simple hecha en Streamlit, donde el usuario:

introduce las claves de su cuenta de X (API keys)

escribe su tweet

elige fecha y hora para publicarlo

Una base de datos en Supabase, donde se guarda cada tweet programado.

Un servicio en la nube (Fly.io) que ejecuta automáticamente un script cada vez que es llamado por EasyCron.
Ese script revisa si hay tweets que ya toca publicar y los envía a la API de X.

Todo es 100% automático una vez configurado.

2. Diagrama de arquitectura (explicación paso a paso)
[ Usuario ]
   │
   ▼
Streamlit (UI local)
   │  - el usuario programa un tweet
   │  - envía los datos a Supabase
   ▼
Supabase (base de datos en la nube)
   │  - guarda tweets pendientes
   ▼
EasyCron (cron externo)
   │  - cada X minutos hace una llamada HTTP
   ▼
Fly.io (servidor FastAPI)
   │  - expone /run
   │  - cuando se llama /run ejecuta runner.py
   ▼
runner.py
   │  - lee tweets pendientes de Supabase
   │  - publica en X vía API v2
   ▼
X (Twitter)

3. Qué archivos son críticos y qué hace cada uno
app.py

Interfaz Streamlit que el usuario abre en su ordenador.
Esta pantalla es donde el usuario:

introduce claves de API de X (input manual, no almacenamos nada sensible)

escribe el tweet

selecciona fecha/hora

pulsa “Schedule tweet”

Cuando eso pasa, se envía una petición a Supabase creando un registro del tweet.

Si algo falla al programar tweets: revisar este archivo.

scheduled_tweets (tabla en Supabase)

Guarda:

texto del tweet

fecha/hora exacta en la que debe publicarse

claves de API del usuario (si se usa multiusuario, habría que cifrar)

estado:

pending → pendiente de publicar

sent → ya publicado

failed → intentado pero falló

Si los tweets no aparecen o no están en el estado correcto: revisar la tabla o las consultas REST.

runner.py

Es el “motor” real.
El backend que:

Consulta Supabase y busca filas donde:

status = 'pending'

run_at <= ahora

Publica el tweet usando la API v2 de X via Tweepy.Client, porque:

El plan Free de X SÍ permite publicar usando API v2.

El plan Free de X NO permite publicar usando API v1.1.

Actualiza el status a:

sent

failed

Este archivo no interactúa con el usuario directamente.
Solo se ejecuta cuando Fly.io recibe una llamada a /run.

Si el tweet no se publica o se queda en pending: revisar runner.py y logs.

server.py

Servidor FastAPI que vive en Fly.io.

Ofrece un endpoint:

GET /run


Cada vez que se llama:

ejecuta runner.main()

revisa pendientes

publica lo que toca

Si Fly.io deja de responder o EasyCron no dispara: revisar este archivo.

Dockerfile

Define cómo construir la imagen de Docker que se sube a Fly.io.
Contiene:

instalación de dependencias

copia del código

comando para arrancar Uvicorn

Si el deploy falla: mirar este archivo.

fly.toml

Archivo de configuración de Fly.io.
Fly lo genera automáticamente con fly launch, pero se puede editar.

Contiene:

nombre de la app

puerto interno (8000)

reglas de despliegue

autoscaling

Si Fly.io no arranca la app correctamente: revisar este archivo.

4. Variables que se deben configurar SIEMPRE

El sistema depende de 2 variables de entorno:

SUPABASE_URL=xxxxx
SUPABASE_KEY=xxxxx


En local se exportan con:

export SUPABASE_URL="..."
export SUPABASE_KEY="..."


En Fly.io se configuran con:

fly secrets set SUPABASE_URL=... SUPABASE_KEY=...


Si estas variables no existen, nada funcionará.

5. Dependencias y versiones importantes

Se instalan desde requirements.txt.

Claves:

tweepy → usamos el Client de API v2, no el API v1.1

fastapi → para exponer /run

uvicorn → servidor para Fly.io

requests → para hablar con Supabase REST

streamlit → UI local

6. Cómo desplegar en Fly.io (resumen)

Desde la carpeta del repo:

fly auth login
fly launch
fly secrets set SUPABASE_URL=xxx SUPABASE_KEY=xxx
fly deploy


Fly crea una URL como:

https://tweet-automation-ai.fly.dev/run


Cada llamada a ese endpoint ejecuta runner.py.

7. EasyCron (automatizar publicación)

EasyCron llama a la URL de Fly.io cada X minutos.

Ejemplo configuración:

URL:

https://tweet-automation-ai.fly.dev/run


Frecuencia (free):

*/10 * * * *


(cada 10 minutos)

Frecuencia (de pago):

* * * * *


(cada minuto)

Timezone:

Europe/Madrid


Cuando EasyCron llama a /run:

el backend se despierta,

ejecuta runner.py,

publica tweets pendientes.

8. Qué mirar si algo falla (guía rápida)
1. El tweet no se publica

Revisar fly logs

Puede haber error de X (403, 401, 429)

Ver si el tweet pasó a failed

2. El tweet no aparece en Supabase

Revisar app.py

Ver si hay errores de “Supabase error XX”

3. EasyCron dice “failed”

Revisar si la URL de Fly responde

4. No ejecuta nada

Revisar que Fly siga arrancado server.py

Revisar secrets en Fly

5. X devuelve 403

Seguir usando API v2

No usar API v1.1

Ver si las claves están bien

9. Mejoras a futuro

Cifrar claves de usuario antes de guardarlas en Supabase

Añadir interfaz para listar y cancelar tweets programados

Añadir logs de ejecución en Supabase

Añadir protección (token secreto) al endpoint /run

Backups automáticos

UI pública (desplegar Streamlit en Cloud)

10. Resumen ejecutivo

Este proyecto funciona así:

La UI solo programa tweets (no publica)

Supabase almacena lo programado

Fly.io ejecuta el motor real

EasyCron es el reloj (scheduler)

X API v2 publica los tweets

Todo está desacoplado para que no necesites tu ordenador encendido en ningún punto.