# Taller de MLOps: Despliegue de una API de Predicción con CI/CD y GitOps

Este repositorio contiene el desarrollo completo de un experimento de MLOps cuyo objetivo es entrenar, contenerizar, monitorear y desplegar una API de predicción ligera basada en el dataset *penguins*. Se implementa un entorno CI/CD automatizado mediante **GitHub Actions** y se orquesta el despliegue con enfoque **GitOps** usando **Argo CD**.

El flujo contempla el entrenamiento del modelo, empaquetamiento en imágenes Docker, despliegue en Kubernetes, generación de tráfico con un **LoadTester**, y observabilidad completa mediante **Prometheus** y **Grafana**. Todo el proceso sigue una secuencia de pasos iterativos donde se valida el funcionamiento tanto a nivel de contenedores individuales como en un entorno orquestado con declaración de recursos, asegurando consistencia en los cambios y trazabilidad de las versiones.

---

## Estructura del Proyecto

La estructura del directorio sigue una organización modular, alineada con los principios de separación de responsabilidades: desarrollo, infraestructura, configuración y despliegue.

```plaintext
MLOPS_PUJ_Grupo6_Copia/
├── .github/workflows/ci-cd.yml            # Pipeline CI/CD GitHub Actions
├── argo-cd/app.yaml                       # Declaración Application de Argo CD
├── images/                                # Capturas para documentación
├── taller_argo/
│   ├── api/                               # API FastAPI de predicción
│   │   ├── app/
│   │   │   ├── main.py                    # Código principal de la API
│   │   │   └─ model.pkl                   # Modelo entrenado
│   │   ├── Dockerfile
│   │   └─ requirements.txt
│   ├── loadtester/                        # Generador de carga sobre la API
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └─ requirements.txt
│   └── manifests/
│       ├── grafana-config/
│       │   ├── dashboard.json             # Panel de visualización Prometheus
│       │   ├── dashboards.yaml            # Proveedor de dashboards
│       │   └─ datasources.yaml            # Fuente de datos Prometheus
│       ├── prometheus-config/
│       │   └─ prometheus.yml              # Configuración de scrapeo
│       ├── api-deployment.yaml
│       ├── script-deployment.yaml
│       ├── grafana-deployment.yaml
│       ├── prometheus-deployment.yaml
│       └── kustomization.yaml
├── docker-compose.yaml                    # Stack local opcional para pruebas
├── .gitignore
└── README.md
```

---

## Requisitos

* Docker y Docker Compose
* Cuenta en Docker Hub
* Kubernetes (ej: Docker Desktop con K8s)
* GitHub con acceso a Secrets para CI/CD
* Entorno de desarrollo (VS Code, PyCharm o terminal Docker-enabled)

---

## Descripción General del Flujo

El desarrollo inicia con la construcción de la API en entorno local, verificando su correcto funcionamiento con `uvicorn`. Posteriormente, se encapsula este servicio dentro de una imagen Docker, validando su funcionalidad de manera aislada.

Luego, se introduce un componente adicional denominado **LoadTester**, encargado de generar solicitudes automáticas a la API, con el fin de simular carga y permitir la visualización de métricas a través de Prometheus y Grafana. Ambos servicios se integran mediante manifiestos de Kubernetes.

En fases posteriores, se automatiza el entrenamiento del modelo y la construcción de la imagen de la API mediante **GitHub Actions**, asegurando que cada cambio en el repositorio pueda activar un pipeline CI/CD completo. Este flujo se complementa con la incorporación de **Argo CD**, herramienta que permite mantener el clúster de Kubernetes sincronizado con el estado deseado definido en Git, cumpliendo así los principios de GitOps.

El diseño modular de este taller permite validar de forma independiente cada componente (API, contenedores, monitoreo, automatización), pero también integrarlos de forma progresiva para reflejar un entorno real de despliegue continuo con observabilidad.

---

## Paso 1: Entrenamiento del modelo y prueba local de la API

El primer paso consiste en entrenar un modelo ligero usando el dataset *penguins* incluido en la librería `seaborn`. Esto permite generar un archivo `model.pkl`, que luego será utilizado por la API para realizar predicciones. Todo el proceso se realiza en un entorno virtual de Python 3.9.

```bash
cd taller_argo
py -3.9 -m venv venv
venv/Scripts/activate
cd api
pip install -r requirements.txt
python train_model.py
uvicorn app.main:app --reload
```
Análogo en Ubuntu
```bash
cd taller_argo
python3.9 -m venv venv
source venv/bin/activate
cd api 
pip install -r requirements.txt
python train_model.py
uvicorn app.main:app --reload
```

Una vez levantado el servidor, se puede acceder a la documentación interactiva de la API en:

```
http://localhost:8000/docs
```

![Acceso a la API local](images/localhost-uvicorn.png)

---

## Paso 2: Construcción de la imagen Docker de la API

Una vez validado el comportamiento de la API en desarrollo, se construye una imagen Docker que encapsula tanto el código como el modelo entrenado. Esto permite ejecutar el servicio de forma reproducible y aislada.

```bash
deactivate
cd taller_argo/api
docker build -t api-fastapi .
docker run -p 8989:8989 --name api-run -it api-fastapi
```

Accede nuevamente desde el navegador a:

```
http://localhost:8989/docs
```

![API desplegada con Docker](images/api-docker.png)

Finalmente, puedes eliminar la imagen y el contenedor para limpiar el entorno:

```bash
docker rm api-run
docker rmi api-fastapi
```

---

## Paso 3: Composición con Docker y generación de carga

En este paso se incorpora el componente **LoadTester**, cuya función es enviar peticiones continuas a la API para simular uso real. Se configura un archivo `docker-compose.yaml` que permite lanzar tanto la API como el LoadTester de forma coordinada.

```bash
cd taller_argo
docker compose up --build
```

Para detener y eliminar los contenedores junto con las imágenes creadas:

```bash
docker compose down --rmi all
```

![Carga del LoadTester](images/loadtester_compose.png)

---

## Paso 4: Publicación de imágenes en Docker Hub

Una vez probadas localmente, las imágenes se etiquetan y se suben al repositorio de Docker Hub para poder ser utilizadas posteriormente en Kubernetes. Se recomienda usar versionamiento explícito (`v1`, `v2`, `v3`) para facilitar la trazabilidad.

```bash
docker login

docker build -t usuario/penguin-api:v1 ./api
docker build -t usuario/penguin-loadtester:v1 ./loadtester

docker push usuario/penguin-api:v1
docker push usuario/penguin-loadtester:v1
```

![Imágenes en Docker Hub](images/dockerhub-penguinApi.png)

---

## Paso 5: Despliegue de los componentes en Kubernetes

Activado el entorno Kubernetes (por ejemplo desde Docker Desktop), se procede a desplegar los componentes como pods y servicios. Esto se hace mediante archivos YAML que describen los recursos.

```bash
kubectl apply -k manifests/
```

Verifica el estado del clúster con:

```bash
kubectl get pods
kubectl get svc
kubectl get configmap
```

Y realiza pruebas accediendo a los servicios vía `port-forward`:

```bash
kubectl port-forward svc/api 8989:8989
kubectl port-forward svc/prometheus 9090:9090
kubectl port-forward svc/grafana 3000:3000
```

![Prometheus operativo](images/prometheus.png)

![Dashboard en Grafana](images/grafana.png)

---

## Paso 6: Automatización con Argo CD

Argo CD permite sincronizar los manifiestos declarativos directamente desde GitHub al clúster, garantizando coherencia y trazabilidad. Para instalarlo:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl get pods -n argocd
```

Aplica tu definición de aplicación:

```bash
kubectl apply -f argo-cd/app.yaml -n argocd
```

Accede a la interfaz con:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

![Interfaz de Argo CD](images/argo-ui.png)

Obtén la contraseña inicial con:

### En Windows (PowerShell):

```powershell
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}"
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("<output>"))
```

### En Linux o WSL:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

---


## Paso 7: Pipeline CI/CD con GitHub Actions

El archivo `.github/workflows/ci-cd.yml` define un flujo automatizado que se activa con cada `push` sobre la rama principal. Realiza lo siguiente:

1. Entrena el modelo y genera `model.pkl`
2. Construye la imagen Docker
3. Versiona y sube la imagen al Docker Hub
4. Actualiza el manifiesto con el nuevo tag
5. Realiza commit del manifiesto actualizado (opcional)

Es necesario definir dos `secrets` en GitHub:

* `DOCKER_USERNAME`: usuario de Docker Hub
* `DOCKER_PASSWORD`: contraseña o token de acceso
* `GH_PUSH_TOKEN`: token de GitHub para que Actions pueda acceder y sobreescribir el procedimiento.

![Git Actions](images/GitActions.png)

---

## Paso 8: Verificación de estado y limpieza del entorno Kubernetes

En caso de necesitar desmontar todos los componentes desplegados, se pueden eliminar los manifiestos ejecutando:

```bash
kubectl delete -k manifests/
```

También se pueden eliminar manifiestos uno a uno si es necesario:

```bash
kubectl delete -f manifests/api-deployment.yaml
kubectl delete -f manifests/script-deployment.yaml
kubectl delete -f manifests/prometheus-deployment.yaml
kubectl delete -f manifests/grafana-deployment.yaml
```

Para verificar las últimas interacciones del LoadTester (útil para depuración y validación de tráfico generado hacia la API):

```bash
kubectl logs -l app=loadtester --tail=10 -f
```

![Loadtester Funcionando](images/last10-loadtester.png)

Este comando muestra las últimas 10 líneas de log y se mantiene en espera de nuevas peticiones (modo seguimiento).

---

## Problemas encontrados durante el desarrollo

Durante el desarrollo del proyecto se presentaron varios desafíos técnicos que obligaron a ajustes y correcciones iterativas:

* Fallos intermitentes en el acceso al endpoint `/predict` cuando la API aún no estaba lista al inicio del LoadTester.
* ConfigMap mal montados por errores en rutas o nombres de archivo.
* Incompatibilidades entre versiones de `scikit-learn` y los formatos esperados en `model.pkl`.
* Timeout y errores de conexión durante sincronización con Argo CD debido a imágenes con etiquetas inválidas o ausentes en Docker Hub.

Estas situaciones se resolvieron implementando validaciones, corrigiendo el orden de despliegue, ajustando los volúmenes montados y asegurando que los manifiestos estuvieran correctamente versionados y alineados con el pipeline CI/CD.

---

## Para Iniciar el Experimento en la VM

Iniciamos la máquina virtual, y descargamos la actualización del experimento a traves de GitHub. Luego de hacer esto, dentro del directorio de desarrollo del taller hacemos lo siguiente:

```bash
minikube delete  # En caso de que se encuentre apagado Minikube
minikube start --driver=docker --cpus=4 --memory=8192 --addons=default-storageclass
```

Para saber con mayor claridad los recursos con los que contamos para el levantamiento, usamos los siguientes comandos:

```bash
free -h
nproc
```

Comprobamos el estado de `minikube`

```bash
kubectl get nodes
kubectl get pods -A
```

Arrancamos ArgoCD (si existe problemas por el firewall se puede descargar el archivo autogenerado e instalarlo manualmente).

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Verificamos que actualmente se encuentre los pods de Argo CD estable.

```bash
kubectl get pods -n argocd
```

Activamos los manifiestos vía Argo CD.

```bash
kubectl apply -f argo-cd/app.yaml
```

Se utiliza port-forward para acceder a Argo CD.

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d # obtención de la clave en ubuntu
```
**Nota:** Para validar el correcto funcionamiento de los diferentes pods, podemos usar `port-forward` ya vistos para acceder a las instancias en la VM, y poder verificar su correcto funcionamiento.

## Datos de Prueba

Puedes probar el endpoint `/predict` con ejemplos como:

```json
{
  "bill_length_mm": 45.1,
  "bill_depth_mm": 14.5,
  "flipper_length_mm": 210,
  "body_mass_g": 4200
}
```

```json
{
  "bill_length_mm": 38.2,
  "bill_depth_mm": 18.1,
  "flipper_length_mm": 180,
  "body_mass_g": 3750
}
```

---

Este flujo completo permite validar el ciclo de vida de un modelo de machine learning en producción, incluyendo entrenamiento, despliegue, monitoreo, automatización de versiones y actualización continua declarativa basada en Git.

---

## Lecciones Aprendidas

El desarrollo de este taller permitió consolidar una visión práctica de los principios y herramientas clave en un flujo MLOps moderno. A través del proceso se obtuvieron las siguientes lecciones:

* **Automatizar el entrenamiento y el empaquetado del modelo** permite reducir errores manuales y facilita la trazabilidad de versiones en producción.
* **Docker y Kubernetes** son herramientas fundamentales para garantizar portabilidad, escalabilidad y aislamiento en servicios de machine learning.
* La incorporación de **observabilidad con Prometheus y Grafana** proporciona métricas valiosas para monitorear el uso de la API y la estabilidad del entorno.
* **Argo CD** representa una solución eficaz para aplicar GitOps en entornos reales, donde se requiere que el clúster refleje fielmente el estado declarado en un repositorio.
* El uso de **GitHub Actions** como orquestador de CI/CD simplifica la integración continua en entornos con múltiples versiones y múltiples pasos.

Este ejercicio también evidenció la importancia de una buena organización de carpetas, la necesidad de manejo explícito de errores, y la conveniencia de mantener una estructura declarativa y versionada de todos los recursos.

---

## Conclusión

Este proyecto entrega un entorno funcional completo de MLOps, integrando entrenamiento, versionamiento, empaquetamiento, despliegue automatizado, monitoreo y sincronización continua. El flujo cubre desde el desarrollo local hasta un despliegue automatizado en clúster Kubernetes, utilizando prácticas modernas y herramientas ampliamente utilizadas en la industria.

La secuencia de pasos implementada no solo valida el funcionamiento del modelo, sino también su despliegue confiable y su capacidad de monitoreo, ofreciendo una base sólida para expandir hacia flujos más complejos o entornos reales de producción.

Este taller demuestra que, con una arquitectura modular y herramientas correctamente integradas, es posible construir entornos reproducibles, auditables y mantenibles, alineados con las mejores prácticas de MLOps y DevOps.

---




