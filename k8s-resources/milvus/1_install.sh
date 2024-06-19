helm repo add milvus https://zilliztech.github.io/milvus-helm/
helm repo update


helm install milvus milvus/milvus -n milvus --create-namespace -f values.yaml --set etcd.replicaCount=1 --set minio.mode=standalone --set pulsar.enabled=false --set cluster.enabled=false
