import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

# Cargar y limpiar dataset
df = sns.load_dataset("penguins").dropna()

# Definir variables predictoras y la variable objetivo
X = df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]]
y = df["species"].astype("category").cat.codes  # Codificamos especies como 0, 1, 2

# Entrenar modelo
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) 
clf = RandomForestClassifier(n_estimators=35, random_state=42) # random forest pequeño
# se puede variar la semilla para variar resultados
clf.fit(X_train, y_train)

# Guardar modelo entrenado
os.makedirs("app", exist_ok=True)
joblib.dump(clf, "app/model.pkl")

print("Modelo entrenado y guardado en app/model.pkl")
