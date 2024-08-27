CURRENT_DIR=$(pwd)

sed "s|<HOST_PATH>|$CURRENT_DIR|g" federated-template.yaml > federated-deployment.yaml

kubectl apply -f federated-deployment.yaml

kubectl wait --for=condition=Ready pod/federated-learning-global -n kubeflow --timeout=300s

kubectl exec -it -n kubeflow federated-learning-global -- python3 /app/install_dependancies.py
