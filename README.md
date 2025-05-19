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

Una vez levantado el servidor, se puede acceder a la documentación interactiva de la API en:

```
http://localhost:8000/docs
```

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

Este paso permite verificar que la API es capaz de manejar tráfico y que la estructura de logs y respuestas funciona correctamente.

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

Este paso puede repetirse cada vez que se introduzcan mejoras o ajustes al código de la API o el LoadTester, generando nuevas versiones.

---

## Paso 5: Despliegue de los componentes en Kubernetes

Activado el entorno Kubernetes (por ejemplo desde Docker Desktop), se procede a desplegar los componentes como pods y servicios. Esto se hace mediante archivos YAML que describen los recursos.

```bash
kubectl apply -f manifests/api-deployment.yaml
kubectl apply -f manifests/script-deployment.yaml
kubectl apply -f manifests/prometheus-deployment.yaml
kubectl apply -f manifests/grafana-deployment.yaml

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

Y accede a la interfaz con:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Obtén la contraseña inicial con:

```powershell
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}"
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("<output>"))
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

---

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
