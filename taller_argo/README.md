#           Taller Argo

Inicializar la api a modo de prueba
```bash
py -3.9 -m venv venv
venv/Scripts/activate
cd api
pip install -r requirements.txt
python train_model.py
uvicorn app.main:app --reload
```

Modo de acceso
```plaintext
localhost:8000
```

Pruebas de la API
```plaintext
{
  "bill_length_mm": 45.1,
  "bill_depth_mm": 14.5,
  "flipper_length_mm": 210,
  "body_mass_g": 4200
}
{
  "bill_length_mm": 50.2,
  "bill_depth_mm": 15.1,
  "flipper_length_mm": 220,
  "body_mass_g": 5400
}
{
  "bill_length_mm": 38.2,
  "bill_depth_mm": 18.1,
  "flipper_length_mm": 180,
  "body_mass_g": 3750
}
```

Inicialización de un contenedor de prueba que guarde la API
```bash
deactivate
docker build -t api-fastapi .
docker run -p 8989:8989 --name api-run -it api-fastapi
```

Borrar tanto el contenedor como la imagen de la API
```bash
docker rm api-run
docker rmi api-fastapi
```

Prueba del testerload con la api, se adiciona el docker compose sólo para este propósito
corroboramos las solicitudes por segundo y matamos los contenedores
```bash
cd ..
docker compose up --build 
```

Eliminamos la prueba por completo 
```bash
docker compose down --rmi all 
```

En el pc local se activa kubernetes en docker desktop para el desarrollo, se utiliza ya la construcción de las imágenes one by one

```bash
docker build -t blutenherz/penguin-api:v1 ./api
docker build -t blutenherz/penguin-loadtester:v1 ./loadtester
docker build -t blutenherz/penguin-api:v2 ./api
docker build -t blutenherz/penguin-loadtester:v2 ./loadtester
docker login # en caso de no haber logueado previamente
docker push blutenherz/penguin-api:v1
docker push blutenherz/penguin-loadtester:v1
docker push blutenherz/penguin-api:v2
docker push blutenherz/penguin-loadtester:v2
```


```bash
kubectl cluster-info
kubectl get nodes
```

```bash
kubectl apply -f manifests/api-deployment.yaml
kubectl apply -f manifests/script-deployment.yaml
kubectl apply -f manifests/prometheus-deployment.yaml
kubectl apply -f manifests/grafana-deployment.yaml
kubectl get pods
kubectl get svc
kubectl get configmap
# Revisión de que la api y el loadtester están en línea correctamente 
kubectl port-forward svc/api 8989:8989
kubectl port-forward svc/prometheus 9090:9090
kubectl port-forward svc/grafana 3000:3000
kubectl apply -k manifests/
kubectl logs -l app=loadtester --tail=10 -f
kubectl delete -f manifests/
```


```bash
kubectl create configmap prometheus-config --from-file=prometheus.yml=manifests/prometheus-config/prometheus.yml --dry-run=client -o yaml > manifests/prometheus-configmap.yaml

kubectl create configmap grafana-datasource --from-file=datasources.yaml=manifests/grafana-config/datasources.yaml --dry-run=client -o yaml > manifests/grafana-datasource.yaml

kubectl create configmap grafana-dashboard-config --from-file=dashboards.yaml=manifests/grafana-config/dashboards.yaml --dry-run=client -o yaml > manifests/grafana-dashboard-config.yaml

kubectl create configmap grafana-dashboard-json --from-file=dashboard.json=manifests/grafana-config/dashboard.json --dry-run=client -o yaml > manifests/grafana-dashboard-json.yaml

```

```plaintext
localhost:9090
predict_requests_total # consumo del endpoint /metrics de la api
localhost:3000
Predicciones FastAPI

```